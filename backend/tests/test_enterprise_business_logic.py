"""Enterprise Test Suite ET-1 — Business Logic & Stability.

Validates idempotency, multi-request stability, paywall enforcement,
and entitlement gating on the versioned API surface.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

PAID_BUNDLE_CODE = "modules_4_5"
PAID_UNIT = "module4-unit-1"

pytestmark = pytest.mark.skipif(
    "sqlite" in (settings.DATABASE_URL or "").lower(),
    reason="Enterprise business-logic tests require Postgres (UUID, CITEXT, INET).",
)


# ---------------------------------------------------------------------------
# Billing Idempotency
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _seed_bundle_product():
    """Ensure the paid bundle product exists for checkout tests.

    Uses a direct engine connection (not the rolled-back db_session fixture)
    so the product is visible to the TestClient's real DB sessions.
    """
    from backend.models.billing import Product

    engine = create_engine(settings.DATABASE_URL, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        existing = (
            db.query(Product).filter(Product.code == PAID_BUNDLE_CODE).one_or_none()
        )
        if existing is None:
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
    finally:
        db.close()
        engine.dispose()
    yield


_IDEMPOTENCY_TABLE_EXISTS = None


def _idempotency_table_exists() -> bool:
    global _IDEMPOTENCY_TABLE_EXISTS
    if _IDEMPOTENCY_TABLE_EXISTS is None:
        from sqlalchemy import create_engine, inspect

        engine = create_engine(settings.DATABASE_URL)
        _IDEMPOTENCY_TABLE_EXISTS = (
            "idempotency_keys" in inspect(engine).get_table_names()
        )
        engine.dispose()
    return _IDEMPOTENCY_TABLE_EXISTS


def test_billing_checkout_creates_purchase(client: TestClient, auth_headers):
    """POST /api/v1/billing/checkout without idempotency key creates a purchase."""
    headers = auth_headers("et-checkout@example.com")
    payload = {"product_code": PAID_BUNDLE_CODE, "is_gift": False}

    r = client.post("/api/v1/billing/checkout", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "purchase_id" in body
    assert "checkout_url" in body
    assert "provider_session_id" in body


@pytest.mark.skipif(
    not _idempotency_table_exists(),
    reason="idempotency_keys table not present in target database",
)
def test_billing_checkout_idempotency_returns_same_purchase_id(
    client: TestClient, auth_headers
):
    """POST /api/v1/billing/checkout with identical Idempotency-Key
    must return the same purchase_id on both calls."""
    headers = auth_headers("et-idempotency@example.com")
    idempotency_key = f"et-key-{uuid.uuid4()}"
    payload = {"product_code": PAID_BUNDLE_CODE, "is_gift": False}

    r1 = client.post(
        "/api/v1/billing/checkout",
        json=payload,
        headers={**headers, "Idempotency-Key": idempotency_key},
    )
    assert r1.status_code == 200, r1.text
    purchase_id_1 = r1.json()["purchase_id"]

    r2 = client.post(
        "/api/v1/billing/checkout",
        json=payload,
        headers={**headers, "Idempotency-Key": idempotency_key},
    )
    assert r2.status_code == 200, r2.text
    purchase_id_2 = r2.json()["purchase_id"]

    assert purchase_id_1 == purchase_id_2


@pytest.mark.skipif(
    not _idempotency_table_exists(),
    reason="idempotency_keys table not present in target database",
)
def test_billing_checkout_different_idempotency_key_creates_new_purchase(
    client: TestClient, auth_headers
):
    """Different Idempotency-Key must create a new purchase."""
    headers = auth_headers("et-idempotency2@example.com")
    payload = {"product_code": PAID_BUNDLE_CODE, "is_gift": False}

    r1 = client.post(
        "/api/v1/billing/checkout",
        json=payload,
        headers={**headers, "Idempotency-Key": f"key-{uuid.uuid4()}"},
    )
    assert r1.status_code == 200
    purchase_id_1 = r1.json()["purchase_id"]

    r2 = client.post(
        "/api/v1/billing/checkout",
        json=payload,
        headers={**headers, "Idempotency-Key": f"key-{uuid.uuid4()}"},
    )
    assert r2.status_code == 200
    purchase_id_2 = r2.json()["purchase_id"]

    assert purchase_id_1 != purchase_id_2


# ---------------------------------------------------------------------------
# Multi-Request Stability
# ---------------------------------------------------------------------------


def test_multiple_health_requests_all_return_200(client: TestClient):
    """Sequential requests to /health must all succeed.
    Not a load test — validates the app does not crash on repeated access."""
    responses = [client.get("/health") for _ in range(25)]
    assert all(r.status_code == 200 for r in responses)
    # All bodies should be identical (no state mutation on health)
    bodies = [r.json() for r in responses]
    assert all(b == bodies[0] for b in bodies)


# ---------------------------------------------------------------------------
# Paywall & Entitlement (Versioned Paths)
# ---------------------------------------------------------------------------


def test_paid_content_paywalled_for_anonymous_users(client: TestClient):
    res = client.get(f"/api/v1/curriculum/module-4/units/{PAID_UNIT}")
    assert res.status_code == 402
    detail = res.json()["detail"]
    assert detail["envelope_id"] == "billing.signin_or_purchase_required"
    assert detail["product_code"] == PAID_BUNDLE_CODE


def test_paid_content_paywalled_for_signed_in_without_grant(
    client: TestClient, auth_headers
):
    headers = auth_headers("et-no-grant@example.com")
    res = client.get(
        f"/api/v1/curriculum/module-4/units/{PAID_UNIT}",
        headers=headers,
    )
    assert res.status_code == 402
    detail = res.json()["detail"]
    assert detail["envelope_id"] == "billing.purchase_required"
    assert detail["product_code"] == PAID_BUNDLE_CODE


# ---------------------------------------------------------------------------
# Gift Flow (Versioned)
# ---------------------------------------------------------------------------


def test_gift_preview_invalid_token_returns_valid_false(client: TestClient):
    res = client.post("/api/v1/gifts/preview", json={"token": "not-a-real-token"})
    assert res.status_code == 200
    assert res.json()["valid"] is False
