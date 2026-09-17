"""Onboarding telemetry routes.

EPIC-002 Phase 4: Onboarding telemetry tracking for monitoring.

Endpoints:
    POST /api/v1/telemetry/onboarding    Track onboarding events
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db
from backend.app.telemetry import record_marketing_event, record_onboarding_event

router = APIRouter()


# ---------------------------------------------------------------------------
# EPIC-002 Phase 4: Onboarding telemetry endpoint
# ---------------------------------------------------------------------------


class OnboardingTelemetryEvent(BaseModel):
    """Onboarding telemetry event model."""

    event: str
    timestamp: int
    user_id: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/onboarding")
def track_onboarding_event(
    event_data: OnboardingTelemetryEvent,
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> dict:
    """Track onboarding event for monitoring and analytics.

    EPIC-002 Phase 4: This endpoint receives onboarding telemetry events
    from the frontend and forwards them to BetterStack monitoring.

    Args:
        event_data: Onboarding event data
        authorization: Bearer token header (optional for telemetry)
        db: Database session

    Returns:
        Success acknowledgment

    Raises:
        400: Invalid event data
    """
    # Validate event data
    if not event_data.event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {"code": "invalid_event", "message": "Event name is required"}
            },
        )

    # Record the event using the telemetry system
    record_onboarding_event(
        event=event_data.event,
        timestamp=event_data.timestamp,
        user_id=event_data.user_id,
        metadata=event_data.metadata,
    )

    return {"status": "recorded"}


# ---------------------------------------------------------------------------
# Marketing surface telemetry (WS-D: scroll-depth baseline)
# ---------------------------------------------------------------------------


class MarketingTelemetryEvent(BaseModel):
    """Marketing telemetry event model (scroll-depth milestones)."""

    event: str
    timestamp: int
    user_id: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/marketing")
def track_marketing_event(
    event_data: MarketingTelemetryEvent,
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> dict:
    """Track marketing-surface events (scroll depth) for analytics.

    WS-D: receives milestone events from public marketing pages
    (/caregiver, /for-communities) so scroll-depth baselines can be
    measured before wayfinding changes ship.

    Args:
        event_data: Marketing event data
        authorization: Bearer token header (optional — public pages)
        db: Database session

    Returns:
        Success acknowledgment

    Raises:
        400: Invalid event data
    """
    if not event_data.event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {"code": "invalid_event", "message": "Event name is required"}
            },
        )

    record_marketing_event(
        event=event_data.event,
        timestamp=event_data.timestamp,
        user_id=event_data.user_id,
        metadata=event_data.metadata,
    )

    return {"status": "recorded"}
