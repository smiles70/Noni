"""Sprint A10 — full local launch smoke.

End-to-end flow covering the launch-critical paths:

    1. Anonymous browsing of free content works
    2. Paid content is paywalled to anonymous users (402 sign-in or buy)
    3. Sign-in works
    4. Paid content is still paywalled to a signed-in user without a grant
    5. Checkout -> webhook -> entitlement granted -> paid content opens
    6. Refund webhook -> entitlement revoked -> paid content paywalled again
    7. Gift flow: separate buyer purchases, recipient signs in and claims,
       recipient now has access; buyer does not

This test exercises real routes against a real Postgres instance using
the MockAuthProvider + MockPaymentProvider configured for dev/tests.
"""

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
from backend.models.billing import Product

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A10 smoke requires Postgres.",
)

# This must match the constant in backend.api.routes.curriculum.
PAID_BUNDLE_CODE = "modules_4_5"

# A real Module 4 unit id from backend/models/curriculum_units_module_4.py.
PAID_UNIT = "module4-unit-1"
# Free content for the negative-control check.
FREE_UNIT_PATH = "/api/curriculum/what-is-ai"


@pytest.fixture(scope="module")
def DbSession():  # noqa: N802
    engine = create_engine(settings.DATABASE_URL, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _seed_bundle_product(DbSession):
    """Ensure the paid bundle product exists and start each test clean."""
    with DbSession() as db:
        db.execute(
            text("DELETE FROM entitlements WHERE product_code = :p"),
            {"p": PAID_BUNDLE_CODE},
        )
        db.execute(
            text("DELETE FROM purchases WHERE product_code = :p"),
            {"p": PAID_BUNDLE_CODE},
        )
        db.execute(
            text("DELETE FROM processed_webhook_events WHERE event_id LIKE 'evt_a10_%'")
        )
        db.execute(
            text("DELETE FROM products WHERE code = :p"), {"p": PAID_BUNDLE_CODE}
        )
        db.commit()
        db.add(
            Product(
                code=PAID_BUNDLE_CODE,
                display_name="Modules 4 & 5 bundle",
                price_cents=4900,
                currency="usd",
                stripe_price_id="price_test_modules_4_5",
                active=True,
                content_version=1,
            )
        )
        db.commit()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


# ---------- helpers ----------


def _signin(client: TestClient, email: str) -> str:
    """Attach a mock Bearer header to the client (ADR 0024).

    The Bearer is read by `get_optional_account` on the next request;
    the account row is upserted lazily. We hit /auth/whoami here so
    the caller can return the account_id for cross-account assertions.
    """
    client.headers["Authorization"] = f"Bearer mock:{email}"
    r = client.get("/auth/whoami")
    assert r.status_code == 200, r.text
    return r.json()["account_id"]


def _checkout(client: TestClient, is_gift: bool = False) -> str:
    r = client.post(
        "/api/billing/checkout",
        json={"product_code": PAID_BUNDLE_CODE, "is_gift": is_gift},
    )
    assert r.status_code == 200, r.text
    return r.json()["purchase_id"]


def _mock_webhook(
    client: TestClient,
    *,
    event_id: str,
    event_type: str,
    purchase_id: str,
    is_gift: bool = False,
):
    body = {
        "_mock": True,
        "id": event_id,
        "type": event_type,
        "data": {
            "object": {
                "id": f"cs_a10_{purchase_id[:8]}",
                "metadata": {
                    "purchase_id": purchase_id,
                    "is_gift": "true" if is_gift else "false",
                    "product_code": PAID_BUNDLE_CODE,
                },
                "payment_intent": f"pi_a10_{purchase_id[:8]}",
            }
        },
    }
    r = client.post(
        "/api/billing/stripe-webhook",
        content=json.dumps(body),
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 200, r.text
    return r.json()


# ---------- 1. anonymous: free content works, paid content is paywalled ----------


def test_smoke_anonymous_can_browse_free_content(client):
    r = client.get(FREE_UNIT_PATH)
    assert r.status_code == 200
    body = r.json()
    assert "ui_state" in body and "stability" in body


def test_smoke_anonymous_hits_paywall_on_paid_content(client):
    r = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r.status_code == 402
    detail = r.json()["detail"]
    assert detail["envelope_id"] == "billing.signin_or_purchase_required"
    assert detail["product_code"] == PAID_BUNDLE_CODE


# ---------- 2. signed-in without grant: still paywalled ----------


def test_smoke_signed_in_without_grant_hits_paywall(client):
    _signin(client, "a10-empty@example.test")
    r = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r.status_code == 402
    assert r.json()["detail"]["envelope_id"] == "billing.purchase_required"


# ---------- 3. full purchase -> access -> refund -> no access ----------


def test_smoke_full_purchase_grants_then_refund_revokes(client):
    _signin(client, "a10-buyer@example.test")

    # Before purchase: paywalled.
    r0 = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r0.status_code == 402

    # Buy -> webhook -> granted.
    purchase_id = _checkout(client, is_gift=False)
    out = _mock_webhook(
        client,
        event_id="evt_a10_grant_1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
    )
    assert out["outcome"] == "granted"

    # Now the paid unit opens.
    r1 = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r1.status_code == 200, r1.text
    body = r1.json()
    assert body["module"] == 4
    assert body["unit_id"] == PAID_UNIT
    assert "ui_state" in body

    # Module 5 is part of the same bundle.
    r2 = client.get("/api/curriculum/module-5/units/module5-unit-1")
    assert r2.status_code == 200

    # Refund.
    refunded = _mock_webhook(
        client,
        event_id="evt_a10_refund_1",
        event_type="charge.refunded",
        purchase_id=purchase_id,
    )
    assert refunded["outcome"] == "refunded"

    # Paid content is paywalled again.
    r3 = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r3.status_code == 402
    assert r3.json()["detail"]["envelope_id"] == "billing.purchase_required"


# ---------- 4. gift purchase -> recipient claims -> recipient has access ----------


def test_smoke_gift_flow_grants_only_recipient(client, DbSession):
    # Buyer purchases as a gift.
    buyer_id = _signin(client, "a10-gifter@example.test")
    purchase_id = _checkout(client, is_gift=True)

    # Set a known token on the purchase so we can simulate delivery.
    from backend.models.billing import Purchase
    from backend.services.gifts import hash_token

    raw_token = "smoke-a10-gift-token"
    with DbSession() as db:
        p = db.query(Purchase).filter(Purchase.id == uuid.UUID(purchase_id)).one()
        p.gift_claim_token_hash = hash_token(raw_token)
        db.commit()

    # Webhook: gift purchase paid (entitlement NOT granted until claim).
    out = _mock_webhook(
        client,
        event_id="evt_a10_gift_1",
        event_type="checkout.session.completed",
        purchase_id=purchase_id,
        is_gift=True,
    )
    assert out["outcome"] == "granted"  # purchase marked paid

    # Buyer does NOT have access (gift not claimed).
    r_buyer = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r_buyer.status_code == 402, r_buyer.text
    assert r_buyer.json()["detail"]["envelope_id"] == "billing.purchase_required"

    # Buyer 'signs out' implicitly when we overwrite the Bearer for the
    # recipient. Nothing server-side to clean up in the Bearer model.
    recipient_id = _signin(client, "a10-recipient@example.test")
    assert recipient_id != buyer_id

    pv = client.post("/api/gifts/preview", json={"token": raw_token})
    assert pv.status_code == 200 and pv.json()["valid"] is True

    cl = client.post("/api/gifts/claim", json={"token": raw_token})
    assert cl.status_code == 200, cl.text

    # Recipient now has access.
    r_recipient = client.get(f"/api/curriculum/module-4/units/{PAID_UNIT}")
    assert r_recipient.status_code == 200, r_recipient.text
    assert r_recipient.json()["unit_id"] == PAID_UNIT
