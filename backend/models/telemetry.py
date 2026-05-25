"""Telemetry ORM model. Append-only audit log.

Per ARCHITECTURE.md rule 9 (Auditability), every ISCS decision is
captured as a structured row. The richness columns (request_path,
stability, selected_state_id, decision_reason, max_complexity) make
the audit trail directly queryable without parsing the metadata JSON.
See ADR 0009.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)
    event = Column(String(64), nullable=False, index=True)
    event_metadata = Column("metadata", JSON, nullable=False, default=dict)

    # ISCS audit columns (Sprint 10 / ADR 0009). Nullable for non-decision events.
    request_path = Column(String(128), nullable=True)
    stability = Column(Float, nullable=True)
    selected_state_id = Column(String(128), nullable=True)
    decision_reason = Column(String(64), nullable=True)
    max_complexity = Column(Integer, nullable=True)
