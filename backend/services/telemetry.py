"""Telemetry Service.

Persists every event to the telemetry_events table.
Per ARCHITECTURE.md rule 9: audit-grade durability.
Sprint 10 (ADR 0009) added the audit kwargs for ISCS decision capture.
"""

from typing import Dict, List, Optional

from backend.core.database import SessionLocal
from backend.models.telemetry import TelemetryEvent


def record(
    event_type: str,
    metadata: Optional[dict] = None,
    *,
    request_path: Optional[str] = None,
    stability: Optional[float] = None,
    selected_state_id: Optional[str] = None,
    decision_reason: Optional[str] = None,
    max_complexity: Optional[int] = None,
) -> Dict:
    """Append a telemetry event. Returns the recorded event (or a queued
    envelope when TELEMETRY_ASYNC is on).

    E70-B2: when TELEMETRY_ASYNC=1 AND REDIS_URL is set, the write is
    enqueued to Celery instead of running synchronously on the request's
    second DB connection. Falls back to sync on broker failure so events
    are never silently dropped.
    """
    from backend.core.config import settings

    if getattr(settings, "TELEMETRY_ASYNC", False) and getattr(
        settings, "REDIS_URL", ""
    ):
        try:
            from backend.tasks.telemetry_tasks import record_telemetry_event

            record_telemetry_event.delay(
                event_type=event_type,
                metadata=metadata or {},
                request_path=request_path,
                stability=stability,
                selected_state_id=selected_state_id,
                decision_reason=decision_reason,
                max_complexity=max_complexity,
            )
            return {
                "queued": True,
                "event": event_type,
                "request_path": request_path,
            }
        except Exception:
            pass  # broker down -> durable sync write below
    return _record_sync(
        event_type,
        metadata,
        request_path=request_path,
        stability=stability,
        selected_state_id=selected_state_id,
        decision_reason=decision_reason,
        max_complexity=max_complexity,
    )


def _record_sync(
    event_type: str,
    metadata: Optional[dict] = None,
    *,
    request_path: Optional[str] = None,
    stability: Optional[float] = None,
    selected_state_id: Optional[str] = None,
    decision_reason: Optional[str] = None,
    max_complexity: Optional[int] = None,
) -> Dict:
    """Append a telemetry event durably. Returns the recorded event."""
    db = SessionLocal()
    try:
        ev = TelemetryEvent(
            event=event_type,
            event_metadata=metadata or {},
            request_path=request_path,
            stability=stability,
            selected_state_id=selected_state_id,
            decision_reason=decision_reason,
            max_complexity=max_complexity,
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return {
            "id": ev.id,
            "time": ev.time.isoformat(),
            "event": ev.event,
            "metadata": ev.event_metadata,
            "request_path": ev.request_path,
            "stability": ev.stability,
            "selected_state_id": ev.selected_state_id,
            "decision_reason": ev.decision_reason,
            "max_complexity": ev.max_complexity,
        }
    finally:
        db.close()


def recent(limit: int = 100) -> List[Dict]:
    """Read recent events (for debugging / audit views)."""
    db = SessionLocal()
    try:
        rows = (
            db.query(TelemetryEvent)
            .order_by(TelemetryEvent.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "time": r.time.isoformat(),
                "event": r.event,
                "metadata": r.event_metadata,
                "request_path": r.request_path,
                "stability": r.stability,
                "selected_state_id": r.selected_state_id,
                "decision_reason": r.decision_reason,
                "max_complexity": r.max_complexity,
            }
            for r in rows
        ]
    finally:
        db.close()
