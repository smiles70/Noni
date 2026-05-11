"""Governance-domain ORM models: DeletionRequest, RateLimitCounter.

See `docs/architecture/SCHEMA.md`, ADR 0023 (account deletion), and ADR
0024 (rate limiting fallback).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DeletionRequest(Base):
    __tablename__ = "deletion_requests"
    __table_args__ = (
        CheckConstraint(
            "status IN ('requested','cancelled','completed')",
            name="ck_deletion_requests_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True
    )
    requested_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(16), nullable=False, default="requested")


class RateLimitCounter(Base):
    __tablename__ = "rate_limit_counters"

    key = Column(String(256), primary_key=True)
    count = Column(Integer, nullable=False, default=0)
    window_start = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
