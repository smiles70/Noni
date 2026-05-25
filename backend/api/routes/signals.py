"""Signals API — ingest authenticated user actions and telemetry.

Sprint 22 I2: gated to signed-in accounts; raw-dict payload replaced
with strict Pydantic schema.
"""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.deps import get_current_account
from backend.models.accounts import Account
from backend.models.user import UserAction
from backend.services.telemetry import record
from backend.core.geragogy_engine.cognitive_model import GeragogySignalModel

router = APIRouter()
model = GeragogySignalModel()


class TelemetryEventIn(BaseModel):
    """Strict schema for telemetry ingestion. Replaces raw dict."""

    type: str = Field(..., min_length=1, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post("/user-action")
def user_action(
    action: UserAction,
    account: Account = Depends(get_current_account),
) -> dict:
    record("USER_ACTION", action.model_dump())
    signals = model.update(action)
    return {"signals": signals}


@router.post("/telemetry")
def log_event(
    body: TelemetryEventIn,
    account: Account = Depends(get_current_account),
) -> dict:
    return record(body.type, body.payload)
