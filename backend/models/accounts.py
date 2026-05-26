"""Account and Learner ORM models.

See `docs/architecture/SCHEMA.md` and ADR 0023.

Design notes:
- `accounts.auth_user_id` is a logical UUID reference to the identity
  provider's user id (today Clerk's `sub` — see ADR 0024). Intentionally
  NOT a foreign key, so the IdP can be swapped without schema migration.
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
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"
    # M1 (alembic m1_login_schema) relaxed the schema (B12, B8, I-D):
    # - email is now NULLable (identity-provider default tokens may not
    #   carry an email claim; B11 forbids gating the critical path on
    #   an optional provider Backend API call to materialize one).
    # - The UNIQUE constraint on email was dropped to structurally
    #   eliminate the email-collision-relink failure class (FC3).
    # auth_user_id remains the sole identity key.
    __table_args__ = (
        UniqueConstraint("auth_user_id", name="uq_accounts_auth_user_id"),
        Index(
            "idx_accounts_email_active",
            "email",
            unique=False,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    email = Column(CITEXT(), nullable=True)
    display_name = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    learners = relationship(
        "Learner", back_populates="account", cascade="all, delete-orphan"
    )
    purchases = relationship(
        "Purchase",
        foreign_keys="Purchase.buyer_account_id",
        back_populates="buyer",
    )
    entitlements = relationship(
        "Entitlement",
        back_populates="account",
        cascade="all, delete-orphan",
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
