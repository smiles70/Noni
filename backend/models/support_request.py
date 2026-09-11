"""Support request models for the n8n help flow."""

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


class SupportRequest(Base):
    """A context-aware help request submitted from the caregiver or
    senior-care-facility path. Persisted before handoff to n8n so the
    request survives queue or webhook outages."""

    __tablename__ = "support_requests"
    __table_args__ = (
        CheckConstraint(
            "context IN ('caregiver', 'facility')",
            name="ck_support_requests_context",
        ),
        CheckConstraint(
            "status IN ('submitted', 'n8n_delivered', 'n8n_failed', 'resolved')",
            name="ck_support_requests_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(
        String(64), nullable=False, unique=True, index=True
    )  # idempotency key from caller
    context = Column(String(32), nullable=False)  # caregiver | facility
    category = Column(String(64), nullable=False)
    email = Column(String(256), nullable=True)
    message = Column(Text, nullable=False)
    page_path = Column(String(256), nullable=True)
    ip_address = Column(String(64), nullable=True)

    status = Column(String(32), nullable=False, default="submitted")
    n8n_response_code = Column(Integer, nullable=True)
    n8n_response_text = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class SupportRequestAudit(Base):
    """Append-only audit of handoff and staff status changes."""

    __tablename__ = "support_request_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    support_request_id = Column(
        UUID(as_uuid=True), ForeignKey("support_requests.id"), nullable=False, index=True
    )
    action = Column(String(32), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    detail = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
