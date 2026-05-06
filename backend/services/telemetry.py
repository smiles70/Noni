"""Telemetry Service.

Persists every event to the telemetry_events table.
Per ARCHITECTURE.md rule 9: audit-grade durability.
"""

from typing import List, Dict

from backend.core.database import SessionLocal
from backend.models.telemetry import TelemetryEvent


def record(event_type: str, metadata: dict) -> Dict:
    """Append a telemetry event durably. Returns the recorded event."""
    db = SessionLocal()
    try:
        ev = TelemetryEvent(event=event_type, event_metadata=metadata or {})
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return {
            "id": ev.id,
            "time": ev.time.isoformat(),
            "event": ev.event,
            "metadata": ev.event_metadata,
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
            }
            for r in rows
        ]
    finally:
        db.close()
