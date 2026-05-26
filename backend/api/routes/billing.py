"""Billing routes: checkout creation + webhook ingestion + health.

See ADR 0021 and ADR 0024.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_current_account, get_db
from backend.core.config import settings
from backend.models.accounts import Account
from backend.models.billing import IdempotencyKey, Product, Purchase
from backend.services import gifts
from pybreaker import CircuitBreakerError

from backend.services.payment_provider import (
    WebhookVerificationError,
    get_payment_provider,
)
from backend.services.rate_limit import RateLimit, client_ip, enforce
from backend.tasks.webhook_tasks import process_stripe_webhook

router = APIRouter()

LIMIT_WEBHOOK_PER_IP = RateLimit(action="webhook", max_per_window=10, window_seconds=60)


# ---------- Models ----------


class CheckoutCreateRequest(BaseModel):
    product_code: str
    is_gift: bool = False


class CheckoutCreateResponse(BaseModel):
    purchase_id: str
    checkout_url: str
    provider_session_id: str


class BillingHealthResponse(BaseModel):
    provider: str
    stripe_mode: str  # 'test' | 'live' | 'mock' | 'unknown'


# ---------- Routes ----------


@router.get("/health", response_model=BillingHealthResponse)
def billing_health() -> BillingHealthResponse:
    """Reports the active provider and Stripe mode.

    Used by `make smoke-prod-live` to verify a live-mode promotion.
    """
    provider = get_payment_provider()
    stripe_mode = "mock"
    if provider.name == "stripe":
        if settings.STRIPE_SECRET_KEY.startswith("sk_live_"):
            stripe_mode = "live"
        elif settings.STRIPE_SECRET_KEY.startswith("sk_test_"):
            stripe_mode = "test"
        else:
            stripe_mode = "unknown"
    return BillingHealthResponse(provider=provider.name, stripe_mode=stripe_mode)


@router.post("/checkout", response_model=CheckoutCreateResponse)
def create_checkout(
    body: CheckoutCreateRequest,
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> CheckoutCreateResponse:
    # Sprint 27 M1: Idempotency-Key dedup.
    if idempotency_key:
        cached = (
            db.query(IdempotencyKey)
            .filter(IdempotencyKey.key == idempotency_key)
            .one_or_none()
        )
        if cached is not None:
            import json

            return CheckoutCreateResponse(**json.loads(cached.outcome_json))

    product = (
        db.query(Product)
        .filter(Product.code == body.product_code, Product.active.is_(True))
        .one_or_none()
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"envelope_id": "billing.product_unavailable"},
        )

    purchase_id = uuid.uuid4()
    purchase = Purchase(
        id=purchase_id,
        buyer_account_id=account.id,
        beneficiary_account_id=None if body.is_gift else account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
    )

    if body.is_gift:
        # Issue token immediately so we can return it to the buyer if needed
        # (kept opaque server-side; only revealed in success page / receipt).
        gifts.issue_token(db, purchase)

    db.add(purchase)
    db.flush()

    provider = get_payment_provider()
    try:
        session_obj = provider.create_checkout_session(
            product_code=product.code,
            price_id=product.stripe_price_id or f"price_dev_{product.code}",
            amount_cents=product.price_cents,
            currency=product.currency,
            buyer_account_id=account.id,
            purchase_id=purchase.id,
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            is_gift=body.is_gift,
        )
    except CircuitBreakerError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"envelope_id": "billing.transient_unavailable"},
        )
    purchase.stripe_checkout_session_id = session_obj.provider_session_id
    db.commit()

    result = CheckoutCreateResponse(
        purchase_id=str(purchase.id),
        checkout_url=session_obj.url,
        provider_session_id=session_obj.provider_session_id,
    )

    # Sprint 27 M1: cache outcome for 24h idempotency.
    if idempotency_key:
        import json

        db.add(
            IdempotencyKey(
                key=idempotency_key,
                outcome_json=json.dumps(result.model_dump()),
            )
        )
        db.commit()

    return result


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    db: DbSession = Depends(get_db),
):
    enforce(db, LIMIT_WEBHOOK_PER_IP, client_ip(request))
    db.commit()

    raw_body = await request.body()
    signature = request.headers.get("stripe-signature")

    provider = get_payment_provider()
    try:
        event = provider.verify_webhook(raw_body, signature)
    except WebhookVerificationError as e:
        # Always fail closed; do not hint at which check failed.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"envelope_id": "billing.webhook_rejected"},
        ) from e
    except CircuitBreakerError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"envelope_id": "billing.transient_unavailable"},
        )

    # Sprint 27 H4: defer webhook processing to Celery background queue.
    task = process_stripe_webhook.delay(
        event_id=event.event_id,
        event_type=event.event_type,
        payload=event.payload,
    )
    return {
        "event_id": event.event_id,
        "task_id": task.id,
        "status": "accepted",
    }
