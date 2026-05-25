"""Curriculum API.

All page-level selection is performed by the canonical ISCS.
Per ARCHITECTURE.md rule 1: no UI complexity decision is delegated
to the client. Endpoints derive stability from the server-side
`InterfaceStateEstimator` and never accept signals from the request body.

Per ADR 0009, every ISCS decision is recorded to the telemetry table
with promoted audit columns (request_path, stability, selected_state_id,
decision_reason, max_complexity).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import require_entitlement
from backend.core.database import get_db
from backend.services.rate_limit import RateLimit, client_ip, enforce
from backend.core.interface_control.state_estimator import InterfaceStateEstimator
from backend.core.interface_control.stability_metric import compute_stability
from backend.core.interface_control.state_selector import select_ui_state
from backend.models.curriculum_units import (
    BRIDGE_UNITS,
    UNITS,
    CurriculumUnit,
    get_unit,
)
from backend.services import telemetry as telemetry_service
from backend.models.curriculum_units_module_2 import (
    UNITS_MODULE_2,
    get_module_2_unit,
)
from backend.models.curriculum_units_module_3 import (
    UNITS_MODULE_3,
    get_module_3_unit,
)
from backend.models.curriculum_units_module_4 import (
    UNITS_MODULE_4,
    get_module_4_unit,
)
from backend.models.curriculum_units_module_5 import (
    UNITS_MODULE_5,
    get_module_5_unit,
)

router = APIRouter()
estimator = InterfaceStateEstimator()

# Modules 4 and 5 ship as a single paid bundle (ADR 0021).
PAID_BUNDLE_CODE = "modules_4_5"

# Single dependency instance, shared by every paid route. Exposed at module
# level so tests can override it via `app.dependency_overrides[paid_bundle_dep]`
# when their focus is content/behavior, not entitlement enforcement.
paid_bundle_dep = require_entitlement(PAID_BUNDLE_CODE)

LIMIT_CURRICULUM_PER_IP = RateLimit(
    action="curriculum", max_per_window=120, window_seconds=60
)


def _current_stability() -> float:
    """Read current stability without injecting external signal.

    A no-op telemetry update progresses the covariance growth term so
    repeated reads do not return identical values, while not biasing
    the state estimate.
    """
    _, cov = estimator.update([0.0, 0.0, 0.0])
    return compute_stability(cov)


def _selected_id(approved) -> str:
    """Extract a stable id from whatever shape select_ui_state returned."""
    if isinstance(approved, dict):
        sid = approved.get("id")
        if isinstance(sid, str):
            return sid
    return "unknown"


@router.get("/what-is-ai")
def what_is_ai(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    telemetry = [0.2, 0.2, 0.3]
    _, cov = estimator.update(telemetry)
    stability = compute_stability(cov)
    pages = [
        {
            "id": "ai-1",
            "title": "What Is Artificial Intelligence?",
            "content": [
                "Artificial Intelligence (AI) means computers helping people think or decide.",
                "AI does not think like a human. It follows patterns.",
                "You already use AI in maps, phones, and search.",
            ],
            "complexity": 1,
        },
        {
            "id": "ai-2",
            "title": "Examples You Already Know",
            "content": ["GPS directions", "Email spam filters", "Voice assistants"],
            "complexity": 2,
        },
    ]
    max_complexity = max(p["complexity"] for p in pages)
    approved = select_ui_state(pages, stability)
    telemetry_service.record(
        "iscs_decision",
        metadata={"candidate_ids": [p["id"] for p in pages]},
        request_path="/api/curriculum/what-is-ai",
        stability=stability,
        selected_state_id=_selected_id(approved),
        decision_reason="approved",
        max_complexity=max_complexity,
    )
    return {"ui_state": approved, "stability": stability}


@router.get("/units")
def list_units(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    """Catalog of available curriculum units (no page-level content)."""
    return {
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "description": u.description,
                "max_complexity": u.max_complexity,
                "stability_threshold": u.stability_threshold,
            }
            for u in UNITS
        ]
    }


@router.get("/menu")
def lesson_menu(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    """Full lesson menu / table of contents (S25.1).

    Returns the entire free-track tree in one roundtrip so the menu UI
    can render without N module fetches:

      {
        "modules": [
          {"id": 1, "title": "...", "units": [{"id", "title", "description"}...]},
          {"id": 2, "title": "...", "units": [...]},
          {"id": 3, "title": "...", "units": [...]},
        ],
        "bridge_units": [{"id", "title", "description"}...]
      }

    Authoritative ordering is the order of each list as defined in the
    units modules. The menu does NOT include Modules 4+ - those are the
    paid track and are gated by entitlement.
    """

    def _serialize(u: CurriculumUnit) -> dict:
        return {
            "id": u.id,
            "title": u.title,
            "description": u.description,
        }

    return {
        "modules": [
            {
                "id": 1,
                "title": "Module 1 — Meeting Claude",
                "units": [_serialize(u) for u in UNITS],
            },
            {
                "id": 2,
                "title": "Module 2 — Sustained use over time",
                "units": [_serialize(u) for u in UNITS_MODULE_2],
            },
            {
                "id": 3,
                "title": "Module 3 — Long-term judgment",
                "units": [_serialize(u) for u in UNITS_MODULE_3],
            },
        ],
        "bridge_units": [_serialize(u) for u in BRIDGE_UNITS],
    }


@router.get("/bridge-units")
def list_bridge_units(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    """Catalog of optional, menu-only side lessons.

    These units are deliberately separate from /units (the linear free
    sequence): they are not part of /next-unit's walk and not in the
    main catalog. The lesson-menu UI (S25.1) consumes this list to show
    them in a "side lessons" section.
    """
    return {
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "description": u.description,
                "max_complexity": u.max_complexity,
                "stability_threshold": u.stability_threshold,
            }
            for u in BRIDGE_UNITS
        ]
    }


@router.get("/units/{unit_id}")
def get_unit_page(unit_id: str) -> dict:
    """Return the ISCS-approved page from the requested unit."""
    unit = get_unit(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")

    stability = _current_stability()
    candidates = [
        p.model_dump() for p in unit.pages if p.complexity <= unit.max_complexity
    ]
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail=f"Unit {unit_id} has no pages within its max_complexity",
        )
    approved = select_ui_state(candidates, stability)
    telemetry_service.record(
        "iscs_decision",
        metadata={
            "unit_id": unit.id,
            "candidate_ids": [c["id"] for c in candidates],
        },
        request_path=f"/api/curriculum/units/{unit.id}",
        stability=stability,
        selected_state_id=_selected_id(approved),
        decision_reason="approved",
        max_complexity=unit.max_complexity,
    )
    return {
        "unit_id": unit.id,
        "unit_title": unit.title,
        "ui_state": approved,
        "stability": stability,
    }


@router.get("/next-unit")
def next_unit() -> dict:
    """Recommend the most advanced unit reachable at the current ISCS stability.

    Linear curriculum: walk UNITS in order; advance while
    `current_stability <= unit.stability_threshold`. The first unit
    that fails the gate is the stopping point.

    Without per-learner state (deferred to Auth sprint), this reflects
    *system-level* readiness, not individual mastery.
    """
    stability = _current_stability()
    chosen = None
    for u in UNITS:
        if stability <= u.stability_threshold:
            chosen = u
        else:
            break
    if chosen is None:
        chosen = UNITS[0]
    telemetry_service.record(
        "iscs_recommendation",
        metadata={"unit_count": len(UNITS)},
        request_path="/api/curriculum/next-unit",
        stability=stability,
        selected_state_id=chosen.id,
        decision_reason="linear-walk",
        max_complexity=chosen.max_complexity,
    )
    return {
        "unit_id": chosen.id,
        "title": chosen.title,
        "stability": stability,
        "reason": "system-level recommendation (no per-learner state yet)",
    }


# ===== Module 2: Sustained, real-world use of Claude over time =====
# See ADR 0015 for why we keep the unit data but reject the drop-in's
# request-body-signals wiring (Rule 1: Backend Authority).


@router.get("/module-2/units")
def list_module_2_units(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    """Catalog of Module 2 curriculum units (no page-level content)."""
    return {
        "module": 2,
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "description": u.description,
                "max_complexity": u.max_complexity,
                "stability_threshold": u.stability_threshold,
                "telemetry_requirements": u.telemetry_requirements,
            }
            for u in UNITS_MODULE_2
        ],
    }


@router.get("/module-2/units/{unit_id}")
def get_module_2_unit_page(unit_id: str) -> dict:
    """Return the ISCS-approved page from the requested Module 2 unit."""
    unit = get_module_2_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 2 unit {unit_id} not found"
        )

    stability = _current_stability()
    candidates = [
        p.model_dump() for p in unit.pages if p.complexity <= unit.max_complexity
    ]
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail=f"Module 2 unit {unit_id} has no pages within its max_complexity",
        )
    approved = select_ui_state(candidates, stability)
    telemetry_service.record(
        "iscs_decision",
        metadata={
            "module": 2,
            "unit_id": unit.id,
            "candidate_ids": [c["id"] for c in candidates],
            "telemetry_requirements": unit.telemetry_requirements,
        },
        request_path=f"/api/curriculum/module-2/units/{unit.id}",
        stability=stability,
        selected_state_id=_selected_id(approved),
        decision_reason="approved",
        max_complexity=unit.max_complexity,
    )
    return {
        "module": 2,
        "unit_id": unit.id,
        "unit_title": unit.title,
        "ui_state": approved,
        "stability": stability,
    }


@router.get("/module-2/next")
def next_module_2_unit() -> dict:
    """Recommend the most advanced Module 2 unit reachable at current stability.

    Linear walk through UNITS_MODULE_2. Per-learner volatility / strain /
    mastery gates from telemetry_requirements are recorded in audit telemetry
    (ADR 0015) but not yet enforced - per-learner state requires auth.
    """
    stability = _current_stability()
    chosen = None
    for u in UNITS_MODULE_2:
        if stability <= u.stability_threshold:
            chosen = u
        else:
            break
    if chosen is None:
        chosen = UNITS_MODULE_2[0]
    telemetry_service.record(
        "iscs_recommendation",
        metadata={
            "module": 2,
            "unit_count": len(UNITS_MODULE_2),
            "telemetry_requirements": chosen.telemetry_requirements,
        },
        request_path="/api/curriculum/module-2/next",
        stability=stability,
        selected_state_id=chosen.id,
        decision_reason="linear-walk",
        max_complexity=chosen.max_complexity,
    )
    return {
        "module": 2,
        "unit_id": chosen.id,
        "title": chosen.title,
        "stability": stability,
        "reason": "system-level recommendation (no per-learner state yet)",
    }


# ===== Module 3: Long-term judgment, recalibration, and autonomy =====
# Same architectural pattern as Module 2 (ADR 0015 / 0016): backend-derived
# stability, no request-body signals. telemetry_requirements recorded in
# event_metadata for future per-learner enforcement (deferred to auth).


@router.get("/module-3/units")
def list_module_3_units(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    return {
        "module": 3,
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "description": u.description,
                "max_complexity": u.max_complexity,
                "stability_threshold": u.stability_threshold,
                "telemetry_requirements": u.telemetry_requirements,
            }
            for u in UNITS_MODULE_3
        ],
    }


@router.get("/module-3/units/{unit_id}")
def get_module_3_unit_page(unit_id: str) -> dict:
    unit = get_module_3_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 3 unit {unit_id} not found"
        )

    stability = _current_stability()
    candidates = [
        p.model_dump() for p in unit.pages if p.complexity <= unit.max_complexity
    ]
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail=f"Module 3 unit {unit_id} has no pages within its max_complexity",
        )
    approved = select_ui_state(candidates, stability)
    telemetry_service.record(
        "iscs_decision",
        metadata={
            "module": 3,
            "unit_id": unit.id,
            "candidate_ids": [c["id"] for c in candidates],
            "telemetry_requirements": unit.telemetry_requirements,
        },
        request_path=f"/api/curriculum/module-3/units/{unit.id}",
        stability=stability,
        selected_state_id=_selected_id(approved),
        decision_reason="approved",
        max_complexity=unit.max_complexity,
    )
    return {
        "module": 3,
        "unit_id": unit.id,
        "unit_title": unit.title,
        "ui_state": approved,
        "stability": stability,
    }


@router.get("/module-3/next")
def next_module_3_unit() -> dict:
    """Recommend the most advanced Module 3 unit reachable at current stability.

    Linear walk through UNITS_MODULE_3. Per-learner volatility/strain/mastery
    gates are recorded but not yet enforced (auth-vendor pass).
    """
    stability = _current_stability()
    chosen = None
    for u in UNITS_MODULE_3:
        if stability <= u.stability_threshold:
            chosen = u
        else:
            break
    if chosen is None:
        chosen = UNITS_MODULE_3[0]
    telemetry_service.record(
        "iscs_recommendation",
        metadata={
            "module": 3,
            "unit_count": len(UNITS_MODULE_3),
            "telemetry_requirements": chosen.telemetry_requirements,
        },
        request_path="/api/curriculum/module-3/next",
        stability=stability,
        selected_state_id=chosen.id,
        decision_reason="linear-walk",
        max_complexity=chosen.max_complexity,
    )
    return {
        "module": 3,
        "unit_id": chosen.id,
        "title": chosen.title,
        "stability": stability,
        "reason": "system-level recommendation (no per-learner state yet)",
    }


# ===== Module 4: Building and using Claude Skills =====
# Same architectural pattern as Modules 2-3 (ADR 0015 / 0016 / 0017): backend-
# derived stability, no request-body signals. telemetry_requirements recorded
# in event_metadata for future per-learner enforcement (deferred to auth).


@router.get("/module-4/units")
def list_module_4_units() -> dict:
    return {
        "module": 4,
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "description": u.description,
                "max_complexity": u.max_complexity,
                "stability_threshold": u.stability_threshold,
                "telemetry_requirements": u.telemetry_requirements,
            }
            for u in UNITS_MODULE_4
        ],
    }


@router.get("/module-4/units/{unit_id}")
def get_module_4_unit_page(
    unit_id: str,
    _account=Depends(paid_bundle_dep),
) -> dict:
    unit = get_module_4_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 4 unit {unit_id} not found"
        )

    stability = _current_stability()
    candidates = [
        p.model_dump() for p in unit.pages if p.complexity <= unit.max_complexity
    ]
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail=f"Module 4 unit {unit_id} has no pages within its max_complexity",
        )
    approved = select_ui_state(candidates, stability)
    telemetry_service.record(
        "iscs_decision",
        metadata={
            "module": 4,
            "unit_id": unit.id,
            "candidate_ids": [c["id"] for c in candidates],
            "telemetry_requirements": unit.telemetry_requirements,
        },
        request_path=f"/api/curriculum/module-4/units/{unit.id}",
        stability=stability,
        selected_state_id=_selected_id(approved),
        decision_reason="approved",
        max_complexity=unit.max_complexity,
    )
    return {
        "module": 4,
        "unit_id": unit.id,
        "unit_title": unit.title,
        "ui_state": approved,
        "stability": stability,
    }


@router.get("/module-4/next")
def next_module_4_unit() -> dict:
    """Recommend the most advanced Module 4 unit reachable at current stability.

    Linear walk through UNITS_MODULE_4. Per-learner volatility/strain/mastery
    gates are recorded but not yet enforced (auth-vendor pass).
    """
    stability = _current_stability()
    chosen = None
    for u in UNITS_MODULE_4:
        if stability <= u.stability_threshold:
            chosen = u
        else:
            break
    if chosen is None:
        chosen = UNITS_MODULE_4[0]
    telemetry_service.record(
        "iscs_recommendation",
        metadata={
            "module": 4,
            "unit_count": len(UNITS_MODULE_4),
            "telemetry_requirements": chosen.telemetry_requirements,
        },
        request_path="/api/curriculum/module-4/next",
        stability=stability,
        selected_state_id=chosen.id,
        decision_reason="linear-walk",
        max_complexity=chosen.max_complexity,
    )
    return {
        "module": 4,
        "unit_id": chosen.id,
        "title": chosen.title,
        "stability": stability,
        "reason": "system-level recommendation (no per-learner state yet)",
    }


# ===== Module 5: Composing Agents from Claude Skills =====
# Same architectural pattern as Modules 2-4 (ADRs 0015 / 0016 / 0017 / 0020):
# backend-derived stability, no request-body signals. telemetry_requirements
# recorded in event_metadata for future per-learner enforcement (deferred to
# auth). Agents are taught declaratively; actually running an agent end-to-end
# is vendor-blocked.


@router.get("/module-5/units")
def list_module_5_units(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    return {
        "module": 5,
        "units": [
            {
                "id": u.id,
                "title": u.title,
                "description": u.description,
                "max_complexity": u.max_complexity,
                "stability_threshold": u.stability_threshold,
                "telemetry_requirements": u.telemetry_requirements,
            }
            for u in UNITS_MODULE_5
        ],
    }


@router.get("/module-5/units/{unit_id}")
def get_module_5_unit_page(
    unit_id: str,
    _account=Depends(paid_bundle_dep),
) -> dict:
    unit = get_module_5_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 5 unit {unit_id} not found"
        )

    stability = _current_stability()
    candidates = [
        p.model_dump() for p in unit.pages if p.complexity <= unit.max_complexity
    ]
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail=f"Module 5 unit {unit_id} has no pages within its max_complexity",
        )
    approved = select_ui_state(candidates, stability)
    telemetry_service.record(
        "iscs_decision",
        metadata={
            "module": 5,
            "unit_id": unit.id,
            "candidate_ids": [c["id"] for c in candidates],
            "telemetry_requirements": unit.telemetry_requirements,
        },
        request_path=f"/api/curriculum/module-5/units/{unit.id}",
        stability=stability,
        selected_state_id=_selected_id(approved),
        decision_reason="approved",
        max_complexity=unit.max_complexity,
    )
    return {
        "module": 5,
        "unit_id": unit.id,
        "unit_title": unit.title,
        "ui_state": approved,
        "stability": stability,
    }


# ===== Curriculum-expansion (Phase 1): /lesson + retrieval-choice =====
# `/lesson` is the additive endpoint that powers the new multi-page
# renderer. The original `/units/{id}` route is left untouched so the
# existing test (`test_get_unit_page_returns_iscs_approved`) and any
# external consumer keep their ISCS-selected single-page behavior.
#
# Per ADR 0009 each call records an `iscs_recommendation` telemetry row;
# the lesson endpoint does NOT use ISCS to *select* a page (the whole
# lesson is returned in author order) but the stability snapshot is
# still useful for audit context.


def _build_lesson_payload(module: int, unit: CurriculumUnit, request_path: str) -> dict:
    """Construct the lesson response for a curriculum unit.

    Used by both the free track (M1-M3) and the paid bundle (M4-M5;
    Sprint "paid modules" P1). The entitlement gate is enforced by the
    route, not here — once a unit has been fetched the payload shape is
    identical so the frontend renderer can be track-agnostic.

    Pages are returned in author order, filtered to those at or below
    the unit's `max_complexity`. The complexity filter is identical to
    the one used by the legacy `/units/{id}` ISCS path so the lesson
    sequence never exposes content the unit's complexity ceiling would
    otherwise exclude.

    `model_dump(exclude_none=True)` keeps the wire payload minimal for
    legacy pages (which carry None for the new optional blocks).
    """
    pages = [
        p.model_dump(exclude_none=True)
        for p in unit.pages
        if p.complexity <= unit.max_complexity
    ]
    if not pages:
        raise HTTPException(
            status_code=500,
            detail=f"Unit {unit.id} has no pages within its max_complexity",
        )
    stability = _current_stability()
    telemetry_service.record(
        "curriculum.lesson_served",
        metadata={
            "module": module,
            "unit_id": unit.id,
            "page_ids": [p["id"] for p in pages],
            "page_count": len(pages),
        },
        request_path=request_path,
        stability=stability,
        selected_state_id=unit.id,
        decision_reason="lesson-sequence",
        max_complexity=unit.max_complexity,
    )
    return {
        "module": module,
        "unit_id": unit.id,
        "unit_title": unit.title,
        "pages": pages,
        "stability": stability,
    }


@router.get("/units/{unit_id}/lesson")
def get_lesson_module_1(unit_id: str) -> dict:
    """Module 1 lesson endpoint — full ordered page list for the unit."""
    unit = get_unit(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")
    return _build_lesson_payload(1, unit, f"/api/curriculum/units/{unit.id}/lesson")


@router.get("/module-2/units/{unit_id}/lesson")
def get_lesson_module_2(unit_id: str) -> dict:
    unit = get_module_2_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 2 unit {unit_id} not found"
        )
    return _build_lesson_payload(
        2, unit, f"/api/curriculum/module-2/units/{unit.id}/lesson"
    )


@router.get("/module-3/units/{unit_id}/lesson")
def get_lesson_module_3(unit_id: str) -> dict:
    unit = get_module_3_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 3 unit {unit_id} not found"
        )
    return _build_lesson_payload(
        3, unit, f"/api/curriculum/module-3/units/{unit.id}/lesson"
    )


# ===== Paid /lesson endpoints (Sprint "paid modules" P1) ================
# These mirror the free /lesson endpoints exactly, gated by the same
# `paid_bundle_dep` entitlement check that protects /units/{id}. The
# 402 paywall handshake is delegated to the dependency so the lesson
# route body sees only authorised callers; non-entitled requests never
# reach _build_lesson_payload and never produce a telemetry row.


@router.get("/module-4/units/{unit_id}/lesson")
def get_lesson_module_4(
    unit_id: str,
    _account=Depends(paid_bundle_dep),
) -> dict:
    """Module 4 lesson endpoint (paid). 402 if no entitlement."""
    unit = get_module_4_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 4 unit {unit_id} not found"
        )
    return _build_lesson_payload(
        4, unit, f"/api/curriculum/module-4/units/{unit.id}/lesson"
    )


@router.get("/module-5/units/{unit_id}/lesson")
def get_lesson_module_5(
    unit_id: str,
    _account=Depends(paid_bundle_dep),
) -> dict:
    """Module 5 lesson endpoint (paid). 402 if no entitlement."""
    unit = get_module_5_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404, detail=f"Module 5 unit {unit_id} not found"
        )
    return _build_lesson_payload(
        5, unit, f"/api/curriculum/module-5/units/{unit.id}/lesson"
    )


class RetrievalChoiceBody(BaseModel):
    """Body schema for the retrieval-choice telemetry endpoint.

    `correct` is computed client-side by comparing `chosen_id` to the
    page's `retrieval.correct_id`. The backend records both fields so
    audit can detect tampering or client bugs (e.g., `correct=true`
    paired with a `chosen_id` that does not match the published
    `correct_id`).
    """

    model_config = ConfigDict(extra="forbid")

    # Widened from le=3 to le=5 in Sprint "paid modules" P2 so paid-track
    # retrieval pages can record their choices through the same endpoint.
    # Entitlement is not re-checked here: a learner who reached a paid
    # retrieval page must already have passed the gate to load the lesson,
    # and a forged module=4 from a non-entitled caller only writes an audit
    # row (no content leak). Audit reconciliation can flag the anomaly.
    module: int = Field(..., ge=1, le=5)
    unit_id: str = Field(..., min_length=1)
    page_id: str = Field(..., min_length=1)
    chosen_id: str = Field(..., min_length=1)
    correct: bool


@router.post("/retrieval-choice")
def record_retrieval_choice(body: RetrievalChoiceBody) -> dict:
    """Record a learner's retrieval-page choice as a telemetry event.

    The endpoint is intentionally permissive: it accepts the choice
    even if the body's `correct` flag disagrees with the unit's
    canonical `correct_id`. Audit can reconcile after the fact.
    Returning a stable shape (`{recorded: true}`) lets the frontend
    treat this as fire-and-forget without parsing.
    """
    telemetry_service.record(
        "curriculum.retrieval_choice",
        metadata={
            "module": body.module,
            "unit_id": body.unit_id,
            "page_id": body.page_id,
            "chosen_id": body.chosen_id,
            "correct": body.correct,
        },
        request_path="/api/curriculum/retrieval-choice",
        selected_state_id=body.unit_id,
        decision_reason="retrieval-choice",
    )
    return {"recorded": True}


@router.get("/module-5/next")
def next_module_5_unit() -> dict:
    """Recommend the most advanced Module 5 unit reachable at current stability.

    Linear walk through UNITS_MODULE_5. Per-learner volatility/strain/mastery
    gates are recorded but not yet enforced (auth-vendor pass).
    """
    stability = _current_stability()
    chosen = None
    for u in UNITS_MODULE_5:
        if stability <= u.stability_threshold:
            chosen = u
        else:
            break
    if chosen is None:
        chosen = UNITS_MODULE_5[0]
    telemetry_service.record(
        "iscs_recommendation",
        metadata={
            "module": 5,
            "unit_count": len(UNITS_MODULE_5),
            "telemetry_requirements": chosen.telemetry_requirements,
        },
        request_path="/api/curriculum/module-5/next",
        stability=stability,
        selected_state_id=chosen.id,
        decision_reason="linear-walk",
        max_complexity=chosen.max_complexity,
    )
    return {
        "module": 5,
        "unit_id": chosen.id,
        "title": chosen.title,
        "stability": stability,
        "reason": "system-level recommendation (no per-learner state yet)",
    }
