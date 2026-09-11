"""Rack 2.8: webhook handler and Celery webhook task branch coverage backfill."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import ProcessedWebhookEvent, Product, Purchase
from backend.models.governance import DeletionRequest
from backend.services.mock_parser import MOCK_NAMESPACE
from backend.services.payment_provider import WebhookEvent
from backend.services.webhook_handler import process_event
from backend.tasks.webhook_tasks import (
    cleanup_deleted_accounts,
    export_telemetry_csv,
    process_stripe_webhook,
)


def _auth_user_id(email: str) -> uuid.UUID:
    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


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


def _create_product(code: str) -> Product:
    db = SessionLocal()
    try:
        product = Product(
            code=code,
            display_name="Test",
            price_cents=100,
            currency="usd",
            active=True,
            content_version=1,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        db.expunge(product)
        return product
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
# process_event
# ---------------------------------------------------------------------------


def test_process_event_returns_duplicate_for_known_event_id():
    product = _create_product("rack28-dup")
    account = _create_account("rack28-dup@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
        stripe_checkout_session_id="cs_dup_001",
    )
    event = WebhookEvent(
        event_id="evt_dup_001",
        event_type="checkout.session.completed",
        payload={
            "id": "cs_dup_001",
            "payment_intent": "pi_dup_001",
            "metadata": {"purchase_id": str(purchase.id), "is_gift": "false"},
        },
    )

    db = SessionLocal()
    try:
        assert process_event(db, event) == "granted"
        db.commit()
        assert process_event(db, event) == "duplicate"
    finally:
        db.close()


def test_process_event_unknown_event_type_is_noop():
    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_unknown_001",
            event_type="invoice.paid",
            payload={},
        )
        assert process_event(db, event) == "noop"
        db.commit()
    finally:
        db.close()


def test_process_event_catches_handler_exception_and_records_error(monkeypatch):
    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_err_001",
            event_type="checkout.session.completed",
            payload={},
        )
        monkeypatch.setattr(
            "backend.services.webhook_handler._on_checkout_completed",
            lambda _db, _event: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        assert process_event(db, event) == "error"
        db.commit()
    finally:
        db.close()


def test_process_event_handles_race_on_processed_event_insert():
    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_race_001",
            event_type="invoice.paid",
            payload={},
        )

        def _first_flush_raises():
            raise IntegrityError("race", "", "")

        with patch.object(db, "flush", _first_flush_raises):
            assert process_event(db, event) == "duplicate"
    finally:
        db.close()


def test_on_checkout_completed_noop_when_purchase_not_found():
    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_no_purchase_001",
            event_type="checkout.session.completed",
            payload={"id": "cs_missing"},
        )
        assert process_event(db, event) == "noop"
        db.commit()
    finally:
        db.close()


def test_on_checkout_completed_noop_when_already_paid():
    product = _create_product("rack28-paid")
    account = _create_account("rack28-paid@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        stripe_checkout_session_id="cs_paid_001",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_paid_001",
            event_type="checkout.session.completed",
            payload={
                "id": "cs_paid_001",
                "metadata": {"purchase_id": str(purchase.id), "is_gift": "false"},
            },
        )
        assert process_event(db, event) == "noop"
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# charge.refunded
# ---------------------------------------------------------------------------


def test_on_charge_refunded_noop_when_purchase_not_found():
    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_refund_no_purchase_001",
            event_type="charge.refunded",
            payload={},
        )
        assert process_event(db, event) == "noop"
        db.commit()
    finally:
        db.close()


def test_on_charge_refunded_noop_when_already_refunded():
    product = _create_product("rack28-refunded")
    account = _create_account("rack28-refunded@example.com")
    _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="refunded",
        refunded_at=datetime.now(timezone.utc),
        stripe_payment_intent_id="pi_refunded_001",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_refunded_001",
            event_type="charge.refunded",
            payload={"payment_intent": "pi_refunded_001"},
        )
        assert process_event(db, event) == "noop"
        db.commit()
    finally:
        db.close()


def test_on_charge_refunded_revokes_entitlement():
    product = _create_product("rack28-refund-grant")
    account = _create_account("rack28-refund-grant@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        stripe_payment_intent_id="pi_refund_grant_001",
    )
    db = SessionLocal()
    try:
        from backend.services import entitlements

        entitlements.grant(
            db,
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
        )
        db.commit()
    finally:
        db.close()

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_refund_grant_001",
            event_type="charge.refunded",
            payload={"payment_intent": "pi_refund_grant_001"},
        )
        assert process_event(db, event) == "refunded"
        db.commit()
        active = entitlements.has_active(db, account.id, product.code)
        assert active is False
    finally:
        db.close()


# ---------------------------------------------------------------------------
# _resolve_purchase resolution order
# ---------------------------------------------------------------------------


def test_resolve_purchase_falls_back_to_payment_intent():
    product = _create_product("rack28-pi")
    account = _create_account("rack28-pi@example.com")
    _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
        stripe_payment_intent_id="pi_fallback_001",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_pi_001",
            event_type="checkout.session.completed",
            payload={
                "metadata": {"purchase_id": "not-a-uuid"},
                "payment_intent": "pi_fallback_001",
            },
        )
        assert process_event(db, event) == "granted"
        db.commit()
    finally:
        db.close()


def test_resolve_purchase_falls_back_to_checkout_session_id():
    product = _create_product("rack28-cs")
    account = _create_account("rack28-cs@example.com")
    _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
        stripe_checkout_session_id="cs_fallback_001",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_cs_001",
            event_type="checkout.session.completed",
            payload={
                "metadata": {"purchase_id": "not-a-uuid"},
                "id": "cs_fallback_001",
            },
        )
        assert process_event(db, event) == "granted"
        db.commit()
    finally:
        db.close()


def test_resolve_purchase_purchase_id_not_found_falls_through():
    product = _create_product("rack28-pid-fall")
    account = _create_account("rack28-pid-fall@example.com")
    _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
        stripe_payment_intent_id="pi_pid_fall_001",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_pid_fall_001",
            event_type="checkout.session.completed",
            payload={
                "metadata": {
                    "purchase_id": str(uuid.uuid4()),
                    "is_gift": "false",
                },
                "payment_intent": "pi_pid_fall_001",
            },
        )
        assert process_event(db, event) == "granted"
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Celery webhook tasks
# ---------------------------------------------------------------------------


def test_process_stripe_webhook_task_returns_duplicate():
    db = SessionLocal()
    try:
        db.add(
            ProcessedWebhookEvent(
                event_id="evt_task_dup_001",
                event_type="checkout.session.completed",
                idempotency_outcome="noop",
            )
        )
        db.commit()
    finally:
        db.close()

    result = process_stripe_webhook.delay(
        "evt_task_dup_001", "checkout.session.completed", {}
    )
    assert result.get() == "duplicate"


def test_process_stripe_webhook_task_retries_on_handler_failure(monkeypatch):
    from celery.exceptions import Retry

    monkeypatch.setattr(
        "backend.tasks.webhook_tasks.process_event",
        lambda _db, _event: (_ for _ in ()).throw(RuntimeError("task boom")),
    )
    with pytest.raises((Retry, RuntimeError)):
        process_stripe_webhook.delay(
            "evt_task_fail_001", "checkout.session.completed", {}
        )


def test_export_telemetry_csv_task():
    result = export_telemetry_csv.delay("2024-01-01", "2024-01-02", "admin@example.com")
    assert result.get() == "not_implemented"


def test_cleanup_deleted_accounts_isolates_failures(monkeypatch):
    account = _create_account("rack28-del@example.com")
    db = SessionLocal()
    try:
        req = DeletionRequest(
            id=uuid.uuid4(),
            account_id=account.id,
            scheduled_for=datetime.now(timezone.utc) - timedelta(seconds=1),
            status="requested",
        )
        db.add(req)
        db.commit()
    finally:
        db.close()

    def _boom(_db, _account):
        raise RuntimeError("deletion failed")

    monkeypatch.setattr("backend.services.deletion.execute_deletion", _boom)
    result = cleanup_deleted_accounts.delay()
    body = result.get()
    assert body["failed"] == 1
    assert body["due"] >= 1


def test_on_charge_refunded_noop_without_beneficiary():
    product = _create_product("rack28-refund-no-ben")
    account = _create_account("rack28-refund-no-ben@example.com")
    _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        stripe_payment_intent_id="pi_no_ben_001",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_no_ben_001",
            event_type="charge.refunded",
            payload={"payment_intent": "pi_no_ben_001"},
        )
        assert process_event(db, event) == "refunded"
        db.commit()
    finally:
        db.close()


def test_resolve_purchase_skips_unmatched_payment_intent():
    product = _create_product("rack28-cs-fallback2")
    account = _create_account("rack28-cs-fallback2@example.com")
    _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
        stripe_checkout_session_id="cs_fallback_002",
    )

    db = SessionLocal()
    try:
        event = WebhookEvent(
            event_id="evt_cs_fallback_002",
            event_type="checkout.session.completed",
            payload={
                "metadata": {"purchase_id": "not-a-uuid"},
                "payment_intent": "pi_no_match",
                "id": "cs_fallback_002",
            },
        )
        assert process_event(db, event) == "granted"
        db.commit()
    finally:
        db.close()
