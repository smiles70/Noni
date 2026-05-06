"""Curriculum API.

All page-level selection is performed by the canonical ISCS.
Per ARCHITECTURE.md rule 1: no UI complexity decision is delegated
to the client. Endpoints derive stability from the server-side
`InterfaceStateEstimator` and never accept signals from the request body.
"""

from fastapi import APIRouter, HTTPException

from backend.core.interface_control.state_estimator import InterfaceStateEstimator
from backend.core.interface_control.stability_metric import compute_stability
from backend.core.interface_control.state_selector import select_ui_state
from backend.models.curriculum_units import UNITS, get_unit

router = APIRouter()
estimator = InterfaceStateEstimator()


def _current_stability() -> float:
    """Read current stability without injecting external signal.

    A no-op telemetry update progresses the covariance growth term so
    repeated reads do not return identical values, while not biasing
    the state estimate.
    """
    _, cov = estimator.update([0.0, 0.0, 0.0])
    return compute_stability(cov)


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
    approved = select_ui_state(pages, stability)
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
    # Clamp candidates by the unit's max_complexity ceiling.
    candidates = [
        p.model_dump() for p in unit.pages if p.complexity <= unit.max_complexity
    ]
    if not candidates:
        raise HTTPException(
            status_code=500,
            detail=f"Unit {unit_id} has no pages within its max_complexity",
        )
    approved = select_ui_state(candidates, stability)
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
    return {
        "unit_id": chosen.id,
        "title": chosen.title,
        "stability": stability,
        "reason": "system-level recommendation (no per-learner state yet)",
    }
