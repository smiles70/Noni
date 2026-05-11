"""Account and Learner ORM models.

See `docs/architecture/SCHEMA.md` and ADR 0023.

Design notes:
- `accounts.auth_user_id` is a logical UUID reference to the identity
  provider's user id (e.g. Supabase auth.users.id). Intentionally NOT a
  foreign key, so the vendor's schema can change without breaking us.
- `accounts.email` is CITEXT (case-insensitive) in Postgres.
- `learners` records the relationship between an account and a learner
  identity; for adult learners this is typically `relationship='self'`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("auth_user_id", name="uq_accounts_auth_user_id"),
        UniqueConstraint("email", name="uq_accounts_email"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    email = Column(CITEXT(), nullable=False)
    display_name = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    learners = relationship(
        "Learner", back_populates="account", cascade="all, delete-orphan"
    )


class Learner(Base):
    __tablename__ = "learners"
    __table_args__ = (
        CheckConstraint(
            "relationship IN ('self','gift_recipient')",
            name="ck_learners_relationship",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    display_name = Column(String(256), nullable=True)
    relationship_type = Column(
        "relationship", String(32), nullable=False, default="self"
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    account = relationship("Account", back_populates="learners")
