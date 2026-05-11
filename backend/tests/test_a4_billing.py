"""Sprint A4 — billing, webhook idempotency, gift redemption."""

from __future__ import annotations

import json
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.core.config import settings
from backend.models.billing import Entitlement, Product, Purchase

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A4 billing tests require Postgres.",
)


# ---------- fixtures ----------


@pytest.fixture(scope="module")
def DbSession():  # noqa: N802
    engine = create_engine(settings.DATABASE_URL, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


PRODUCT_CODE = "modules_4_5_test_a4"


@pytest.fixture(autouse=True)
def _seed_product(DbSession):
    with DbSession() as db:
        db.execute(
            text("DELETE FROM entitlements WHERE product_code = :p"),
            {"p": PRODUCT_CODE},
        )
        db.execute(
            text("DELETE FROM purchases WHERE product_code = :p"), {"p": PRODUCT_CODE}
        )
        db.execute(text("DELETE FROM products WHERE code = :p"), {"p": PRODUCT_CODE})
        db.execute(
            text("DELETE FROM processed_webhook_events WHERE event_id LIKE 'evt_a4_%'")
        )
        db.commit()
        db.add(
            Product(
                code=PRODUCT_CODE,
                display_name="A4 test product",
                price_cents=4900,
                currency="usd",
                stripe_price_id="price_test_a4",
                active=True,
                content_version=1,
            )
        )
        db.commit()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


def _signin(client: TestClient, email: str) -> str:
    r = client.post("/auth/callback", json={"credential": f"mock:{email}"})
    assert r.status_code == 200, r.text
    return r.json()["account_id"]


def _post_mock_webhook(
    client: TestClient,
    *,
    event_id: str,
    event_type: str,
    purchase_id: str,
    is_gift: bool = False,
    extra: dict | None = None,
):
    payload_object = {
        "id": f"cs_a4_{purchase_id[:8]}",
        "metadata": {
            "purchase_id": purchase_id,
            "is_gift": "true" if is_gift else "false",
            "product_code": PRODUCT_CODE,
        },
        "payment_intent": f"pi_a4_{purchase_id[:8]}",
    }
    if extra:
        payload_object.update(extra)
    body = {
        "_mock": True,
        "id": event_id,
        "type": event_type,
        "data": {"object": payload_object},
    }
    return client.post(
        "/api/billing/stripe-webhook",
        content=json.dumps(body),
        headers={"content-type": "application/json"},
    )


# ---------- /health ----------


def test_billing_health_reports_mock_provider(client):
    r = client.get("/api/billing/health")
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "mock"
    assert body["stripe_mode"] == "mock"


# ---------- /checkout ----------


def test_checkout_requires_session(client):
    r = client.post("/api/billing/checkout", json={"product_code": PRODUCT_CODE})
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_checkout_unknown_product_404(client):
    _signin(client, "a4-unknown@example.test")
    r = client.post("/api/billing/checkout", json={"product_code": "nope"})
    assert r.status_code == 404
    assert r.json()["detail"]["envelope_id"] == "billing.product_unavailable"


def test_checkout_self_purchase_creates_purchase_row(client, DbSession):
    _signin(client, "a4-self@example.test")
    r = client.post(
        "/api/billing/checkout", json={"product_code": PRODUCT_CODE, "is_gift": False}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["checkout_url"].startswith("https://mock-stripe.local/")
    purchase_id = uuid.UUID(body["purchase_id"])
    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == purchase_id).one()
        assert p.status == "pending"
        assert p.beneficiary_account_id == p.buyer_account_id
        assert p.gift_claim_token_hash is None


def test_checkout_gift_purchase_issues_token_hash(client, DbSession):
    _signin(client, "a4-giftbuyer@example.test")
    r = client.post(
        "/api/billing/checkout", json={"product_code": PRODUCT_CODE, "is_gift": True}
    )
    assert r.status_code == 200
    purchase_id = uuid.UUID(r.json()["purchase_id"])
    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == purchase_id).one()
        assert p.beneficiary_account_id is None
        assert p.gift_claim_token_hash is not None
        assert len(p.gift_claim_token_hash) == 64  # sha256 hex


# ---------- webhook: idempotency + grant ----------


def test_webhook_rejects_unsigned_body(client):
    r = client.post(
        "/api/billing/stripe-webhook",
        content="not even json",
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["envelope_id"] == "billing.webhook_rejected"


def test_checkout_completed_grants_entitlement(client, DbSession):
    _signin(client, "a4-grant@example.test")
    r = client.post(
        "/api/billing/checkout", json={"product_code": PRODUCT_CODE, "is_gift": False}
    )
    purchase_id = r.json()["purchase_id"]

    rw = _post_mock_webhook(
        client,
        event_id="evt_a4_grant_1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
    )
    assert rw.status_code == 200, rw.text
    assert rw.json()["outcome"] == "granted"

    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id)).one()
        assert p.status == "paid"
        ent = (
            db.query(Entitlement)
            .filter(
                Entitlement.account_id == p.buyer_account_id,
                Entitlement.product_code == PRODUCT_CODE,
            )
            .one()
        )
        assert ent.revoked_at is None


def test_duplicate_webhook_is_noop(client, DbSession):
    _signin(client, "a4-dup@example.test")
    purchase_id = client.post(
        "/api/billing/checkout", json={"product_code": PRODUCT_CODE}
    ).json()["purchase_id"]

    r1 = _post_mock_webhook(
        client,
        event_id="evt_a4_dup_1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
    )
    r2 = _post_mock_webhook(
        client,
        event_id="evt_a4_dup_1",  # same event id
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["outcome"] == "granted"
    assert r2.json()["outcome"] == "duplicate"


def test_refund_revokes_entitlement(client, DbSession):
    _signin(client, "a4-refund@example.test")
    purchase_id = client.post(
        "/api/billing/checkout", json={"product_code": PRODUCT_CODE}
    ).json()["purchase_id"]
    _post_mock_webhook(
        client,
        event_id="evt_a4_refund_1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
    )
    rr = _post_mock_webhook(
        client,
        event_id="evt_a4_refund_2",
        event_type="charge.refunded",
        purchase_id=purchase_id,
    )
    assert rr.status_code == 200
    assert rr.json()["outcome"] == "refunded"
    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id)).one()
        assert p.status == "refunded"
        ent = (
            db.query(Entitlement)
            .filter(
                Entitlement.account_id == p.buyer_account_id,
                Entitlement.product_code == PRODUCT_CODE,
            )
            .one()
        )
        assert ent.revoked_at is not None


# ---------- gift flow end-to-end ----------


def test_gift_flow_purchase_then_claim(client, DbSession):
    # Buyer purchases a gift.
    _signin(client, "a4-gifter@example.test")
    co = client.post(
        "/api/billing/checkout",
        json={"product_code": PRODUCT_CODE, "is_gift": True},
    )
    purchase_id = co.json()["purchase_id"]

    # Find the raw token by looking up the hash and reversing isn't possible
    # — so this test exercises the path where the buyer would have stored
    # the token externally. We mint our own token by directly setting the
    # hash on the row, then "deliver" the token to the recipient.
    from backend.services.gifts import hash_token

    raw_token = "mock-gift-raw-token-A4"
    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id)).one()
        p.gift_claim_token_hash = hash_token(raw_token)
        db.commit()

    # Webhook marks the gift purchase paid (no entitlement granted yet).
    rw = _post_mock_webhook(
        client,
        event_id="evt_a4_gift_1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
        is_gift=True,
    )
    assert rw.status_code == 200

    # Buyer signs out, recipient signs in.
    client.post("/auth/signout")
    client.cookies.clear()
    _signin(client, "a4-recipient@example.test")

    # Preview before claim.
    pv = client.post("/api/gifts/preview", json={"token": raw_token})
    assert pv.status_code == 200
    assert pv.json()["valid"] is True
    assert pv.json()["product_code"] == PRODUCT_CODE

    # Claim.
    cl = client.post("/api/gifts/claim", json={"token": raw_token})
    assert cl.status_code == 200, cl.text
    body = cl.json()
    assert body["product_code"] == PRODUCT_CODE
    recipient_id = body["granted_to_account_id"]

    # Entitlement now exists for recipient; token consumed.
    with DbSession() as db:
        ent = (
            db.query(Entitlement)
            .filter(
                Entitlement.account_id == uuid.UUID(recipient_id),
                Entitlement.product_code == PRODUCT_CODE,
            )
            .one()
        )
        assert ent.revoked_at is None
        p = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id)).one()
        assert p.gift_claim_token_hash is None  # single-use
        assert p.gift_claimed_at is not None


def test_gift_double_claim_rejected(client, DbSession):
    _signin(client, "a4-gifter2@example.test")
    purchase_id = client.post(
        "/api/billing/checkout",
        json={"product_code": PRODUCT_CODE, "is_gift": True},
    ).json()["purchase_id"]

    from backend.services.gifts import hash_token

    raw_token = "mock-gift-raw-token-double-A4"
    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id)).one()
        p.gift_claim_token_hash = hash_token(raw_token)
        db.commit()
    _post_mock_webhook(
        client,
        event_id="evt_a4_gift_d1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
        is_gift=True,
    )

    client.post("/auth/signout")
    client.cookies.clear()
    _signin(client, "a4-r1@example.test")
    r1 = client.post("/api/gifts/claim", json={"token": raw_token})
    assert r1.status_code == 200

    # Second account tries to redeem the same (now consumed) token.
    client.post("/auth/signout")
    client.cookies.clear()
    _signin(client, "a4-r2@example.test")
    r2 = client.post("/api/gifts/claim", json={"token": raw_token})
    assert r2.status_code == 400
    assert r2.json()["detail"]["envelope_id"] == "gift.invalid_or_already_claimed"
