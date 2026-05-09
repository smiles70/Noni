"""Golden Landing Flow + Landing Page API.

- `/steps` and `/steps/{id}` expose the conceptual Golden Flow model
  (8 user-state steps; see `docs/flows/golden-landing-flow.md`).
- `/page` exposes the actual user-facing landing-page copy
  (see `backend/content/landing_page.py`).

These are deliberately separate artifacts. See ADR 0006.
"""

from fastapi import APIRouter, HTTPException

from backend.content.landing_page import LANDING_PAGE_CONTENT
from backend.models.landing import LANDING_STEPS, get_step
from backend.models.landing_page import LandingPageContent
from backend.content.signup_first_win import SIGNUP_FIRST_WIN_CONTENT
from backend.models.signup_first_win import SignupFirstWinContent

router = APIRouter()


@router.get("/steps")
def list_steps() -> dict:
    """Return the full ordered set of Golden Flow steps (conceptual model)."""
    return {"steps": [s.model_dump() for s in LANDING_STEPS]}


@router.get("/steps/{step_id}")
def get_step_route(step_id: str) -> dict:
    """Return one Golden Flow step by id."""
    step = get_step(step_id)
    if step is None:
        raise HTTPException(status_code=404, detail=f"Step {step_id} not found")
    return step.model_dump()


@router.get("/page", response_model=LandingPageContent)
def get_landing_page() -> LandingPageContent:
    """Return the user-facing landing-page copy."""
    return LandingPageContent.model_validate(LANDING_PAGE_CONTENT)


# ---- Sign-up -> First Safe Win (Golden Flow Steps 4-6) ----


@router.get("/first-win", response_model=SignupFirstWinContent)
def get_first_win() -> SignupFirstWinContent:
    """Return the typed Sign-up -> First Safe Win content (Steps 4-6).

    Pure read endpoint. Side-effect free. The frontend renders this
    passively; no client-side state derivation.
    """
    return SignupFirstWinContent(**SIGNUP_FIRST_WIN_CONTENT)
