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
    Text,
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


class OrgAuditLog(Base):
    """OB-5: append-only audit of organization/billing mutations.

    Records who granted a license, changed a tier, issued codes, or
    provisioned an org manually — the minimum trail enterprise buyers
    (and health plans) will ask for before signing.
    """

    __tablename__ = "org_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        # nullable=True since ADMIN-OPS E6: account-level staff actions
        # (account.suspend etc.) are audited without an org.
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    actor_account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    action = Column(String(48), nullable=False)
    detail = Column(String(512), nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)


class AccountFlag(Base):
    """Internal support flags on accounts — e.g. sharing-signal scan.

    Separate from OrgAuditLog because a flagged account may not belong
    to any organization (B2C). Never user-facing; support tooling only.
    """

    __tablename__ = "account_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True
    )
    flag = Column(String(64), nullable=False)
    detail = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    # ADMIN-OPS-HYGIENE H1: triage lifecycle — resolve with note + actor.
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    resolution_note = Column(String(512), nullable=True)
