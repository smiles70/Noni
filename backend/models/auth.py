"""Session ORM model — server-side authoritative session row.

See `docs/architecture/SCHEMA.md` and ADR 0023.

Sessions hold the SHA-256 hash of the cookie value; the cookie itself is
never stored. Revocation is a row update (`revoked_at`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET, UUID

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        UniqueConstraint("session_token_hash", name="uq_sessions_token_hash"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token_hash = Column(String(128), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(String(64), nullable=True)
    last_ip = Column(INET(), nullable=True)
    last_user_agent = Column(String(512), nullable=True)
