"""Billing-domain ORM models: Product, Purchase, Entitlement,
ProcessedWebhookEvent.

See `docs/architecture/SCHEMA.md`, ADR 0021 (pricing), and ADR 0024 (DB
operational policy — webhook idempotency).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from backend.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_cents >= 0", name="ck_products_price_nonneg"),
    )

    code = Column(String(64), primary_key=True)
    display_name = Column(String(256), nullable=False)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="usd")
    stripe_price_id = Column(String(128), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    content_version = Column(Integer, nullable=False, default=1)


class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = (
        UniqueConstraint(
            "stripe_payment_intent_id", name="uq_purchases_stripe_payment_intent"
        ),
        UniqueConstraint(
            "stripe_checkout_session_id",
            name="uq_purchases_stripe_checkout_session",
        ),
        UniqueConstraint(
            "gift_claim_token_hash",
            name="uq_purchases_gift_claim_token_hash",
        ),
        CheckConstraint(
            "status IN ('pending','paid','refunded','failed')",
            name="ck_purchases_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    beneficiary_account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    gift_claim_token_hash = Column(String(128), nullable=True)
    gift_claimed_at = Column(DateTime(timezone=True), nullable=True)
    product_code = Column(String(64), ForeignKey("products.code"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False)
    stripe_payment_intent_id = Column(String(128), nullable=True)
    stripe_checkout_session_id = Column(String(128), nullable=True)
    status = Column(String(16), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)


class Entitlement(Base):
    __tablename__ = "entitlements"

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_code = Column(String(64), ForeignKey("products.code"), primary_key=True)
    granted_by_purchase_id = Column(
        UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False
    )
    content_version = Column(Integer, nullable=False)
    granted_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(String(64), nullable=True)


class ProcessedWebhookEvent(Base):
    __tablename__ = "processed_webhook_events"
    __table_args__ = (
        CheckConstraint(
            "idempotency_outcome IN ('granted','refunded','noop','error')",
            name="ck_processed_webhook_outcome",
        ),
    )

    event_id = Column(String(128), primary_key=True)
    event_type = Column(String(64), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    idempotency_outcome = Column(String(32), nullable=False)
