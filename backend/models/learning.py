"""Learning-domain ORM models: Unit, Progress, EstimatorState.

See `docs/architecture/SCHEMA.md`. EstimatorState closes the architect-
review P0 in ADR 0024: per-user persistence of the ISCS estimator.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Unit(Base):
    __tablename__ = "units"

    id = Column(String(128), primary_key=True)
    module_code = Column(String(32), nullable=False)
    unit_index = Column(Integer, nullable=False)
    title = Column(String(512), nullable=False)
    product_code = Column(String(64), ForeignKey("products.code"), nullable=True)
    content_version = Column(Integer, nullable=False, default=1)
    published_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (
        CheckConstraint("status IN ('started','completed')", name="ck_progress_status"),
    )

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    unit_id = Column(String(128), ForeignKey("units.id"), primary_key=True)
    content_version = Column(Integer, nullable=False, default=1)
    status = Column(String(16), nullable=False)
    first_started_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    page_count_seen = Column(Integer, nullable=False, default=0)


class EstimatorState(Base):
    __tablename__ = "estimator_state"

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    scope = Column(String(128), primary_key=True, default="global")
    state_blob = Column(LargeBinary, nullable=False)
    last_stability = Column(Numeric(6, 4), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
