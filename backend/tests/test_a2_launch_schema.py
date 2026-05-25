"""Sprint A2 — launch schema sanity tests.

Verifies the new launch tables exist with expected primary keys, foreign
keys, and a representative round-trip insert + read. Runs against the
Postgres service container in CI.

These are intentionally focused on schema *shape*; behavior is covered by
later sprints (A3 auth, A4 entitlements, etc.).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

# Ensure all launch models are registered on Base.metadata before any
# Inspector/CRUD calls.
from backend.models import accounts as _accounts  # noqa: F401
from backend.models import auth as _auth  # noqa: F401
from backend.models import billing as _billing  # noqa: F401
from backend.models import governance as _governance  # noqa: F401
from backend.models import learning as _learning  # noqa: F401
from backend.models.accounts import Account
from backend.models.auth import Session as SessionRow
from backend.models.billing import (
    Entitlement,
    ProcessedWebhookEvent,
    Product,
    Purchase,
)
from backend.models.learning import EstimatorState, Progress, Unit

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A2 schema requires Postgres (UUID, CITEXT, INET, partial indexes).",
)


@pytest.fixture(scope="module")
def engine():
    return create_engine(settings.DATABASE_URL, future=True)


@pytest.fixture(scope="module")
def Session(engine):  # noqa: N802
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ---------- shape ----------

EXPECTED_TABLES = {
    "accounts",
    "learners",
    "sessions",
    "products",
    "purchases",
    "entitlements",
    "processed_webhook_events",
    "units",
    "progress",
    "estimator_state",
    "deletion_requests",
    "rate_limit_counters",
    "telemetry_events",  # legacy + augmented columns
}


def test_all_launch_tables_present(engine):
    insp = inspect(engine)
    present = set(insp.get_table_names())
    missing = EXPECTED_TABLES - present
    assert not missing, f"Missing tables after migration: {missing}"


def test_telemetry_events_has_new_columns(engine):
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns("telemetry_events")}
    for required in (
        "account_id",
        "session_id",
        "unit_id",
        "occurred_at",
        "expires_at",
    ):
        assert required in cols, f"telemetry_events missing column {required}"


def test_entitlements_composite_primary_key(engine):
    insp = inspect(engine)
    pk = insp.get_pk_constraint("entitlements")["constrained_columns"]
    assert set(pk) == {"account_id", "product_code"}


def test_progress_composite_primary_key(engine):
    insp = inspect(engine)
    pk = insp.get_pk_constraint("progress")["constrained_columns"]
    assert set(pk) == {"account_id", "unit_id"}


def test_processed_webhook_events_pk_is_event_id(engine):
    insp = inspect(engine)
    pk = insp.get_pk_constraint("processed_webhook_events")["constrained_columns"]
    assert pk == ["event_id"]


# ---------- round-trip ----------


def test_end_to_end_purchase_grant_round_trip(engine, Session):
    """Insert account → product → purchase → entitlement → progress.

    Confirms FKs and check constraints are wired correctly.
    """
    with Session() as s:
        # Clean slate (the test uses a unique email so this is mostly belt+suspenders).
        s.execute(
            text("DELETE FROM entitlements WHERE product_code = 'test_product_a2'")
        )
        s.execute(text("DELETE FROM progress WHERE unit_id = 'test_unit_a2'"))
        s.execute(text("DELETE FROM purchases WHERE product_code = 'test_product_a2'"))
        s.execute(text("DELETE FROM units WHERE id = 'test_unit_a2'"))
        s.execute(text("DELETE FROM products WHERE code = 'test_product_a2'"))
        s.execute(
            text("DELETE FROM accounts WHERE email = 'a2-roundtrip@example.test'")
        )
        s.commit()

        account = Account(
            id=uuid.uuid4(),
            email="a2-roundtrip@example.test",
            display_name="A2 Roundtrip",
        )
        s.add(account)

        product = Product(
            code="test_product_a2",
            display_name="A2 Test Product",
            price_cents=4900,
            currency="usd",
            active=True,
            content_version=1,
        )
        s.add(product)

        unit = Unit(
            id="test_unit_a2",
            module_code="m_test",
            unit_index=1,
            title="A2 Test Unit",
            product_code="test_product_a2",
            content_version=1,
        )
        s.add(unit)
        s.commit()

        purchase = Purchase(
            id=uuid.uuid4(),
            buyer_account_id=account.id,
            beneficiary_account_id=account.id,
            product_code=product.code,
            amount_cents=product.price_cents,
            currency="usd",
            stripe_payment_intent_id=f"pi_test_{uuid.uuid4().hex[:12]}",
            stripe_checkout_session_id=f"cs_test_{uuid.uuid4().hex[:12]}",
            status="paid",
            paid_at=datetime.now(timezone.utc),
        )
        s.add(purchase)
        s.commit()

        entitlement = Entitlement(
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
            content_version=product.content_version,
        )
        s.add(entitlement)

        progress = Progress(
            account_id=account.id,
            unit_id=unit.id,
            content_version=unit.content_version,
            status="started",
            page_count_seen=3,
        )
        s.add(progress)

        webhook = ProcessedWebhookEvent(
            event_id=f"evt_test_{uuid.uuid4().hex[:12]}",
            event_type="checkout.session.completed",
            idempotency_outcome="granted",
        )
        s.add(webhook)

        s.commit()

        # Read back.
        round_trip = (
            s.query(Entitlement)
            .filter_by(account_id=account.id, product_code=product.code)
            .one()
        )
        assert round_trip.granted_by_purchase_id == purchase.id
        assert round_trip.revoked_at is None
        assert round_trip.content_version == 1


def test_session_token_hash_is_unique(engine, Session):
    """sessions.session_token_hash must reject duplicates (architect P0)."""
    from sqlalchemy.exc import IntegrityError

    with Session() as s:
        s.execute(text("DELETE FROM sessions WHERE session_token_hash = 'dup_hash_a2'"))
        s.execute(
            text("DELETE FROM accounts WHERE email = 'a2-dupsession@example.test'")
        )
        s.commit()

        account = Account(
            id=uuid.uuid4(),
            email="a2-dupsession@example.test",
        )
        s.add(account)
        s.commit()

        s.add(
            SessionRow(
                account_id=account.id,
                session_token_hash="dup_hash_a2",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        s.commit()

        s.add(
            SessionRow(
                account_id=account.id,
                session_token_hash="dup_hash_a2",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()


def test_processed_webhook_event_id_is_unique(engine, Session):
    """Webhook idempotency: same event_id must be rejected by the PK."""
    from sqlalchemy.exc import IntegrityError

    with Session() as s:
        evt_id = f"evt_dup_a2_{uuid.uuid4().hex[:8]}"
        s.execute(
            text("DELETE FROM processed_webhook_events WHERE event_id = :e"),
            {"e": evt_id},
        )
        s.commit()

        s.add(
            ProcessedWebhookEvent(
                event_id=evt_id,
                event_type="checkout.session.completed",
                idempotency_outcome="granted",
            )
        )
        s.commit()

        s.add(
            ProcessedWebhookEvent(
                event_id=evt_id,
                event_type="checkout.session.completed",
                idempotency_outcome="noop",
            )
        )
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()


def test_estimator_state_persists_and_updates(engine, Session):
    """ADR 0024 P0: estimator state must round-trip per (account_id, scope)."""
    with Session() as s:
        s.execute(
            text("DELETE FROM accounts WHERE email = 'a2-estimator@example.test'")
        )
        s.commit()
        account = Account(id=uuid.uuid4(), email="a2-estimator@example.test")
        s.add(account)
        s.commit()

        s.add(
            EstimatorState(
                account_id=account.id,
                scope="global",
                state_blob=b"\x01\x02\x03",
                last_stability="0.7234",
            )
        )
        s.commit()

        row = (
            s.query(EstimatorState)
            .filter_by(account_id=account.id, scope="global")
            .one()
        )
        assert row.state_blob == b"\x01\x02\x03"
        assert float(row.last_stability) == pytest.approx(0.7234, rel=1e-3)
