"""Golden Landing Flow API.

Anonymous reads; no side effects. Per ADR 0001, ISCS does not gate
landing-step selection and no telemetry is emitted for steps 0-3.
"""

from fastapi import APIRouter, HTTPException

from backend.models.landing import LANDING_STEPS, get_step

router = APIRouter()


@router.get("/steps")
def list_steps() -> dict:
    """Return the full ordered set of landing steps."""
    return {"steps": [s.model_dump() for s in LANDING_STEPS]}


@router.get("/steps/{step_id}")
def get_step_route(step_id: str) -> dict:
    """Return one landing step by id."""
    step = get_step(step_id)
    if step is None:
        raise HTTPException(status_code=404, detail=f"Step {step_id} not found")
    return step.model_dump()
