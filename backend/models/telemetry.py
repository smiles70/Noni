"""Telemetry ORM model. Append-only audit log."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)
    event = Column(String(64), nullable=False, index=True)
    event_metadata = Column("metadata", JSON, nullable=False, default=dict)
