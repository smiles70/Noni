"""Rack 2.7: billing, payment provider, and signals branch coverage backfill."""

from __future__ import annotations

import uuid

import pytest

from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.services.mock_parser import MOCK_NAMESPACE


def _auth_user_id(email: str) -> uuid.UUID:
    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


def _auth(email: str) -> dict:
    return {"Authorization": f"Bearer mock:{email}"}


def _create_product(code: str, **kwargs) -> Product:
    db = SessionLocal()
    try:
        product = Product(
            code=code,
            display_name=kwargs.get("display_name", "Test Product"),
            price_cents=kwargs.get("price_cents", 100),
            currency=kwargs.get("currency", "usd"),
            active=kwargs.get("active", True),
            content_version=kwargs.get("content_version", 1),
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        db.expunge(product)
        return product
    finally:
        db.close()


def _create_account(email: str, **kwargs) -> Account:
    db = SessionLocal()
    try:
        account = Account(
            id=kwargs.get("id", uuid.uuid4()),
            auth_user_id=_auth_user_id(email),
            email=email,
            **kwargs,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        db.expunge(account)
        return account
    finally:
        db.close()


def _create_purchase(**kwargs) -> Purchase:
    db = SessionLocal()
    try:
        purchase = Purchase(id=kwargs.get("id", uuid.uuid4()), **kwargs)
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        db.expunge(purchase)
        return purchase
    finally:
        db.close()


# ---------------------------------------------------------------------------
# /api/v1/billing/health
# ---------------------------------------------------------------------------


def test_billing_health_mock_provider(client):
    r = client.get("/api/v1/billing/health")
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "mock"
    assert body["stripe_mode"] == "mock"


@pytest.mark.parametrize(
    "payment_provider, secret_key, expected_mode",
    [
        ("stripe", "sk_live_xxxxxxxxxxxxxxxx", "live"),
        ("stripe", "sk_test_xxxxxxxxxxxxxxxx", "test"),
        ("stripe", "sk_other_xxxxxxxxxxxxxxx", "unknown"),
    ],
)
def test_billing_health_stripe_modes(
    client, monkeypatch, payment_provider, secret_key, expected_mode
):
    from backend.core.config import settings

    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", payment_provider)
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", secret_key)
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret")

    r = client.get("/api/v1/billing/health")
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == payment_provider
    assert body["stripe_mode"] == expected_mode


# ---------------------------------------------------------------------------
# /api/v1/billing/checkout
# ---------------------------------------------------------------------------


def test_checkout_guest_without_gift_flag(client):
    r = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": "rack27-dummy", "is_gift": False},
    )
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_checkout_guest_gift_missing_email(client):
    r = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": "rack27-dummy", "is_gift": True},
    )
    assert r.status_code == 422
    assert r.json()["detail"]["envelope_id"] == "billing.guest_email_required"


def test_checkout_product_unavailable(client):
    r = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": "rack27-missing", "is_gift": False},
        headers=_auth("rack27-buyer@example.com"),
    )
    assert r.status_code == 404
    assert r.json()["detail"]["envelope_id"] == "billing.product_unavailable"


def test_checkout_idempotency_key_caches_result(client, monkeypatch):
    product = _create_product("rack27-idem")
    key = "rack27-idempotency-key-001"

    r1 = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": product.code, "is_gift": False},
        headers={
            "Authorization": "Bearer mock:rack27-idem@example.com",
            "Idempotency-Key": key,
        },
    )
    assert r1.status_code == 200
    body1 = r1.json()

    r2 = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": product.code, "is_gift": False},
        headers={
            "Authorization": "Bearer mock:rack27-idem@example.com",
            "Idempotency-Key": key,
        },
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["purchase_id"] == body1["purchase_id"]
    assert body2["checkout_url"] == body1["checkout_url"]


def test_checkout_circuit_breaker_on_provider(client, monkeypatch):
    from pybreaker import CircuitBreakerError
    from backend.services import payment_provider

    def _boom(*args, **kwargs):
        raise CircuitBreakerError("open")

    monkeypatch.setattr(
        payment_provider.MockPaymentProvider, "create_checkout_session", _boom
    )
    product = _create_product("rack27-cb")

    r = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": product.code, "is_gift": False},
        headers=_auth("rack27-cb@example.com"),
    )
    assert r.status_code == 503
    assert r.json()["detail"]["envelope_id"] == "billing.transient_unavailable"


def test_checkout_gift_issues_token(client):
    product = _create_product("rack27-gift-product")
    r = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": product.code, "is_gift": True},
        headers=_auth("rack27-gift-buyer@example.com"),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["gift_token"] is not None
    assert body["gift_token"] != ""


def test_checkout_guest_gift_succeeds(client):
    product = _create_product("rack27-guest-gift")
    r = client.post(
        "/api/v1/billing/checkout",
        json={
            "product_code": product.code,
            "is_gift": True,
            "buyer_email": "rack27-guest@example.com",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["gift_token"] is not None


# ---------------------------------------------------------------------------
# /api/v1/billing/stripe-webhook
# ---------------------------------------------------------------------------


def _post_webhook(client, body, content_type="application/json"):
    return client.post(
        "/api/v1/billing/stripe-webhook",
        content=body,
        headers={"Content-Type": content_type},
    )


def test_stripe_webhook_rejects_malformed_body(client):
    r = _post_webhook(client, b"not-json")
    assert r.status_code == 400
    assert r.json()["detail"]["envelope_id"] == "billing.webhook_rejected"


def test_stripe_webhook_rejects_missing_mock_flag(client):
    r = _post_webhook(client, b'{"type":"checkout.session.completed"}')
    assert r.status_code == 400


def test_stripe_webhook_rejects_missing_event_type(client):
    r = _post_webhook(client, b'{"_mock":true,"data":{"object":{}}}')
    assert r.status_code == 400


def test_stripe_webhook_rejects_non_object_payload(client):
    r = _post_webhook(client, b'{"_mock":true,"type":"x","data":{"object":"nope"}}')
    assert r.status_code == 400


def test_stripe_webhook_circuit_breaker_on_verify(client, monkeypatch):
    from pybreaker import CircuitBreakerError
    from backend.services import payment_provider

    def _boom(*args, **kwargs):
        raise CircuitBreakerError("open")

    monkeypatch.setattr(payment_provider.MockPaymentProvider, "verify_webhook", _boom)
    r = _post_webhook(client, b'{"_mock":true,"type":"x","data":{"object":{}}}')
    assert r.status_code == 503
    assert r.json()["detail"]["envelope_id"] == "billing.transient_unavailable"


def test_stripe_webhook_accepts_valid_mock_event(client):
    r = _post_webhook(
        client,
        b'{"_mock":true,"type":"checkout.session.completed","data":{"object":{"id":"cs_123"}}}',
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "accepted"


# ---------------------------------------------------------------------------
# /api/v1/billing/mock-checkout-complete
# ---------------------------------------------------------------------------


def test_mock_checkout_complete_forbidden_when_not_mock_provider(client, monkeypatch):
    from backend.core.config import settings

    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_live_xxxxxxxxxxxxxxxx")
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test")

    r = client.post(
        "/api/v1/billing/mock-checkout-complete",
        json={"purchase_id": str(uuid.uuid4())},
        headers=_auth("rack27-stripe@example.com"),
    )
    assert r.status_code == 403
    assert r.json()["detail"]["envelope_id"] == "billing.mock_only"


def test_mock_checkout_complete_purchase_not_found(client):
    r = client.post(
        "/api/v1/billing/mock-checkout-complete",
        json={"purchase_id": str(uuid.uuid4())},
        headers=_auth("rack27-nf@example.com"),
    )
    assert r.status_code == 404


def test_mock_checkout_complete_not_owner(client):
    owner = _create_account("rack27-owner@example.com")
    product = _create_product("rack27-owner-product")
    purchase = _create_purchase(
        buyer_account_id=owner.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
    )

    r = client.post(
        "/api/v1/billing/mock-checkout-complete",
        json={"purchase_id": str(purchase.id)},
        headers=_auth("rack27-not-owner@example.com"),
    )
    assert r.status_code == 403
    assert r.json()["detail"]["envelope_id"] == "billing.purchase_not_owner"


def test_mock_checkout_complete_not_pending(client):
    account = _create_account("rack27-paid@example.com")
    product = _create_product("rack27-paid-product")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
    )

    r = client.post(
        "/api/v1/billing/mock-checkout-complete",
        json={"purchase_id": str(purchase.id)},
        headers=_auth("rack27-paid@example.com"),
    )
    assert r.status_code == 409
    assert r.json()["detail"]["envelope_id"] == "billing.purchase_not_pending"


def test_mock_checkout_complete_non_gift_grants_entitlement(client):
    product = _create_product("rack27-grant-product")
    r_checkout = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": product.code, "is_gift": False},
        headers=_auth("rack27-grant@example.com"),
    )
    assert r_checkout.status_code == 200
    purchase_id = r_checkout.json()["purchase_id"]

    r = client.post(
        "/api/v1/billing/mock-checkout-complete",
        json={"purchase_id": purchase_id},
        headers=_auth("rack27-grant@example.com"),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["outcome"] == "granted"
    assert body["is_gift"] is False
    assert body["granted"] is True
    assert body["product_code"] == product.code


def test_mock_checkout_complete_gift_does_not_grant_beneficiary(client):
    product = _create_product("rack27-gift-complete")
    r_checkout = client.post(
        "/api/v1/billing/checkout",
        json={"product_code": product.code, "is_gift": True},
        headers=_auth("rack27-gift-buyer2@example.com"),
    )
    assert r_checkout.status_code == 200
    purchase_id = r_checkout.json()["purchase_id"]

    r = client.post(
        "/api/v1/billing/mock-checkout-complete",
        json={"purchase_id": purchase_id},
        headers=_auth("rack27-gift-buyer2@example.com"),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["is_gift"] is True
    assert body["granted"] is False


# ---------------------------------------------------------------------------
# /api/v1/signals/telemetry (signals coverage)
# ---------------------------------------------------------------------------


def test_signals_telemetry_rejects_unknown_event(client):
    r = client.post(
        "/api/v1/signals/telemetry",
        json={"type": "not.in.allowlist", "payload": {}},
        headers=_auth("rack27-telemetry@example.com"),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["accepted"] is False
    assert body["envelope_id"] == "telemetry.event_not_allowed"
