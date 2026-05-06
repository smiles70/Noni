"""Signals API - ingest user actions and telemetry; never returns UI."""
from fastapi import APIRouter
from backend.models.user import UserAction
from backend.services.telemetry import record
from backend.core.geragogy_engine.cognitive_model import GeragogySignalModel

router = APIRouter()
model = GeragogySignalModel()


@router.post("/user-action")
def user_action(action: UserAction) -> dict:
    record("USER_ACTION", action.model_dump())
    signals = model.update(action)
    return {"signals": signals}


@router.post("/telemetry")
def log_event(payload: dict) -> dict:
    return record(payload.get("type", "UNKNOWN"), payload)
