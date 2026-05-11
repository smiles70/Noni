"""Webhook event handler with idempotent grant/refund.

See ADR 0024 (DB operational policy — webhook idempotency).

Idempotency: we INSERT a row into `processed_webhook_events` keyed on
`event_id` inside the same transaction as the entitlement grant. A
unique-violation indicates a duplicate delivery; we roll back as a
no-op.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from backend.models.billing import ProcessedWebhookEvent, Purchase
from backend.services import entitlements
from backend.services.payment_provider import WebhookEvent

log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def process_event(db: DbSession, event: WebhookEvent) -> str:
    """Apply a verified webhook event idempotently.

    Returns one of: 'granted', 'refunded', 'noop', 'duplicate', 'error'.
    The route layer MUST commit on success or the idempotency row will
    not persist.

    Caller must have already verified the event signature.
    """
    # Fast path: dedupe.
    existing = (
        db.query(ProcessedWebhookEvent)
        .filter(ProcessedWebhookEvent.event_id == event.event_id)
        .one_or_none()
    )
    if existing is not None:
        return "duplicate"

    try:
        if event.event_type == "checkout.session.completed":
            outcome = _on_checkout_completed(db, event)
        elif event.event_type == "charge.refunded":
            outcome = _on_charge_refunded(db, event)
        else:
            outcome = "noop"
    except Exception:
        log.exception("webhook handler failed: %s", event.event_id)
        outcome = "error"

    # Always record that we saw this event_id so retries are idempotent.
    db.add(
        ProcessedWebhookEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            idempotency_outcome=outcome,
        )
    )
    try:
        db.flush()
    except IntegrityError:
        # Two concurrent deliveries raced to insert the same event_id.
        # Roll back this transaction; the other delivery wins.
        db.rollback()
        return "duplicate"
    return outcome


def _on_checkout_completed(db: DbSession, event: WebhookEvent) -> str:
    """Mark the matching purchase paid and grant the entitlement."""
    purchase = _resolve_purchase(db, event.payload)
    if purchase is None:
        return "noop"
    if purchase.status == "paid":
        return "noop"

    purchase.status = "paid"
    purchase.paid_at = _utcnow()
    purchase.stripe_checkout_session_id = (
        event.payload.get("id") or purchase.stripe_checkout_session_id
    )
    purchase.stripe_payment_intent_id = (
        event.payload.get("payment_intent") or purchase.stripe_payment_intent_id
    )

    # Beneficiary may be the buyer or set later by gift redemption.
    beneficiary_id = purchase.beneficiary_account_id or purchase.buyer_account_id
    is_gift = (event.payload.get("metadata") or {}).get(
        "is_gift"
    ) == "true" or purchase.gift_claim_token_hash is not None
    if is_gift and purchase.beneficiary_account_id is None:
        # Gift purchase pending claim: do NOT grant yet.
        return "granted"  # purchase is paid; entitlement waits for claim

    entitlements.grant(
        db,
        account_id=beneficiary_id,
        product_code=purchase.product_code,
        granted_by_purchase_id=purchase.id,
    )
    return "granted"


def _on_charge_refunded(db: DbSession, event: WebhookEvent) -> str:
    """Mark the purchase refunded and revoke the entitlement (if any)."""
    purchase = _resolve_purchase(db, event.payload)
    if purchase is None:
        return "noop"
    if purchase.refunded_at is not None:
        return "noop"
    purchase.refunded_at = _utcnow()
    purchase.status = "refunded"

    if purchase.beneficiary_account_id is not None:
        entitlements.revoke(
            db,
            account_id=purchase.beneficiary_account_id,
            product_code=purchase.product_code,
            reason="refund",
        )
    return "refunded"


def _resolve_purchase(db: DbSession, payload: dict[str, Any]) -> Purchase | None:
    """Locate the Purchase row referenced by a Stripe event payload.

    Resolution order:
      1. metadata.purchase_id (we set this at checkout creation)
      2. stripe_payment_intent_id
      3. stripe_checkout_session_id (id of the checkout.session payload)
    """
    md = payload.get("metadata") or {}
    purchase_id_raw = md.get("purchase_id")
    if purchase_id_raw:
        try:
            pid = uuid.UUID(purchase_id_raw)
        except ValueError:
            pid = None
        if pid is not None:
            row = db.query(Purchase).filter(Purchase.id == pid).one_or_none()
            if row is not None:
                return row

    payment_intent = payload.get("payment_intent") or payload.get("id")
    if payment_intent:
        row = (
            db.query(Purchase)
            .filter(Purchase.stripe_payment_intent_id == payment_intent)
            .one_or_none()
        )
        if row is not None:
            return row

    cs_id = payload.get("id")
    if cs_id:
        row = (
            db.query(Purchase)
            .filter(Purchase.stripe_checkout_session_id == cs_id)
            .one_or_none()
        )
        if row is not None:
            return row

    return None
