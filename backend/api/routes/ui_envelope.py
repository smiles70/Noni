"""UI State Envelope API.

Per ADR 0019 and `docs/library/CONTRACT.md` Section IV.A, the frontend
may render ONLY backend-approved envelopes. Undefined states return 404;
the frontend is expected to render a `BlockedNotice`, never to guess.
"""

from fastapi import APIRouter, HTTPException

from backend.models.ui_state_envelope import UIStateEnvelope, get_envelope

router = APIRouter()


@router.get("/{state_id}", response_model=UIStateEnvelope)
def get_ui_envelope(state_id: str) -> UIStateEnvelope:
    """Return the authoritative envelope for a UI state.

    404 if the state is undefined. The frontend MUST NOT render
    undefined states (CONTRACT Section IV.A).
    """
    envelope = get_envelope(state_id)
    if envelope is None:
        raise HTTPException(
            status_code=404,
            detail=f"UI state '{state_id}' is undefined.",
        )
    return envelope
