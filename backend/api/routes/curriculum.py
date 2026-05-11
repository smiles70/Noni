"""Curriculum API.

All page-level selection is performed by the canonical ISCS.
Per ARCHITECTURE.md rule 1: no UI complexity decision is delegated
to the client. Endpoints derive stability from the server-side
`InterfaceStateEstimator` and never accept signals from the request body.

Per ADR 0009, every ISCS decision is recorded to the telemetry table
with promoted audit columns (request_path, stability, selected_state_id,
decision_reason, max_complexity).
"""

from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import require_entitlement
from backend.core.interface_control.state_estimator import InterfaceStateEstimator
from backend.core.interface_control.stability_metric import compute_stability
from backend.core.interface_control.state_selector import select_ui_state
from backend.models.curriculum_units import UNITS, get_unit
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
def what_is_ai() -> dict:
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
def list_units() -> dict:
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
def list_module_2_units() -> dict:
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
def list_module_3_units() -> dict:
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
def list_module_5_units() -> dict:
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
