"""Rack 2.11: organization maintenance and email task coverage."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.models.governance import AccountFlag, OrgAuditLog
from backend.models.learning import Progress, Unit
from backend.models.organizations import Organization, OrgLicense
from backend.services import email as email_service
from backend.services.mock_parser import MOCK_NAMESPACE
from backend.tasks.email_tasks import send_gift_claimed, send_gift_receipt
from backend.tasks.org_tasks import license_renewal_reminders, sharing_pattern_scan


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
# email service
# ---------------------------------------------------------------------------


class _FakeHttpx:
    def __init__(self, status_code=200, text="ok", raise_on_post=False):
        self.status_code = status_code
        self.text = text
        self.raise_on_post = raise_on_post
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.raise_on_post:
            raise RuntimeError("network down")
        resp = MagicMock()
        resp.status_code = self.status_code
        resp.text = self.text
        return resp


def test_email_send_no_api_key(monkeypatch):
    monkeypatch.setattr(settings, "RESEND_API_KEY", "")
    monkeypatch.setattr(settings, "EMAIL_OVERRIDE_TO", "")
    assert email_service.send("to@example.com", "subject", "text") is False


def test_email_send_override_to_and_success(monkeypatch):
    fake = _FakeHttpx(status_code=200)
    monkeypatch.setattr(settings, "RESEND_API_KEY", "re_123")
    monkeypatch.setattr(settings, "EMAIL_OVERRIDE_TO", "override@example.com")
    monkeypatch.setattr(email_service, "httpx", fake)
    assert email_service.send("to@example.com", "subject", "text") is True
    assert fake.calls[0][1]["json"]["to"] == ["override@example.com"]


def test_email_send_rejected(monkeypatch):
    fake = _FakeHttpx(status_code=400, text="bad request")
    monkeypatch.setattr(settings, "RESEND_API_KEY", "re_123")
    monkeypatch.setattr(settings, "EMAIL_OVERRIDE_TO", "")
    monkeypatch.setattr(email_service, "httpx", fake)
    assert email_service.send("to@example.com", "subject", "text") is False


def test_email_send_exception(monkeypatch):
    fake = _FakeHttpx(raise_on_post=True)
    monkeypatch.setattr(settings, "RESEND_API_KEY", "re_123")
    monkeypatch.setattr(settings, "EMAIL_OVERRIDE_TO", "")
    monkeypatch.setattr(email_service, "httpx", fake)
    assert email_service.send("to@example.com", "subject", "text") is False


# ---------------------------------------------------------------------------
# gift email tasks
# ---------------------------------------------------------------------------


def test_send_gift_receipt_no_purchase():
    result = send_gift_receipt.delay(str(uuid.uuid4()))
    assert result.get() == "noop"


def test_send_gift_receipt_no_buyer_email():
    product = _create_product("rack211-gift")
    buyer = _create_account("rack211-gift-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        buyer_email=None,
    )
    # Now delete the buyer so _buyer_email cannot resolve an address.
    db = SessionLocal()
    try:
        db.delete(db.merge(buyer))
        db.commit()
    finally:
        db.close()

    result = send_gift_receipt.delay(str(purchase.id))
    assert result.get() == "noop"


def test_send_gift_receipt_uses_buyer_email_and_sends():
    product = _create_product("rack211-gift-email")
    purchase = _create_purchase(
        buyer_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        buyer_email="gifter@example.com",
    )

    fake = _FakeHttpx(status_code=200)
    with pytest.MonkeyPatch().context() as m:
        m.setattr(settings, "RESEND_API_KEY", "re_123")
        m.setattr(email_service, "httpx", fake)
        result = send_gift_receipt.delay(str(purchase.id))
        assert result.get() == "sent"


def test_send_gift_claimed_unclaimed():
    product = _create_product("rack211-claimed")
    buyer = _create_account("rack211-claimed-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    result = send_gift_claimed.delay(str(purchase.id))
    assert result.get() == "noop"


def test_send_gift_claimed_no_email():
    product = _create_product("rack211-claimed-noemail")
    buyer = _create_account("rack211-claimed-noemail-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        gift_claimed_at=datetime.now(timezone.utc),
    )
    # Delete the buyer so _buyer_email cannot resolve an address.
    db = SessionLocal()
    try:
        db.delete(db.merge(buyer))
        db.commit()
    finally:
        db.close()

    result = send_gift_claimed.delay(str(purchase.id))
    assert result.get() == "noop"


def test_send_gift_claimed_sends():
    product = _create_product("rack211-claimed-send")
    buyer = _create_account("rack211-claimed-send-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        gift_claimed_at=datetime.now(timezone.utc),
    )

    fake = _FakeHttpx(status_code=200)
    with pytest.MonkeyPatch().context() as m:
        m.setattr(settings, "RESEND_API_KEY", "re_123")
        m.setattr(email_service, "httpx", fake)
        result = send_gift_claimed.delay(str(purchase.id))
        assert result.get() == "sent"


# ---------------------------------------------------------------------------
# org tasks: license renewal reminders
# ---------------------------------------------------------------------------


def _make_license() -> tuple[uuid.UUID, uuid.UUID, str, Purchase]:
    tag = uuid.uuid4().hex[:8]
    product = _create_product(f"rack211-license-{tag}")
    account = _create_account(f"rack211-org-admin-{tag}@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        org = Organization(
            name="Renewal Org",
            contact_email="contact@example.com",
            admin_email="admin@example.com",
        )
        db.add(org)
        db.flush()
        license = OrgLicense(
            organization_id=org.id,
            product_code=product.code,
            purchase_id=purchase.id,
            total_seats=10,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(license)
        db.flush()
        org_id = org.id
        lic_id = license.id
        lic_expires = license.expires_at.date().isoformat()
        db.commit()
        return org_id, lic_id, lic_expires, purchase
    finally:
        db.close()


def test_license_renewal_reminders_flags_and_emails():
    _make_license()
    result = license_renewal_reminders.delay()
    body = result.get()
    assert body["expiring"] >= 1
    assert body["flagged"] >= 1


def test_license_renewal_reminders_idempotent():
    org_id, lic_id, lic_expires, _ = _make_license()
    db = SessionLocal()
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        db.add(
            OrgAuditLog(
                id=uuid.uuid4(),
                organization_id=org_id,
                action="license.expiring_soon",
                detail=f"license={lic_id} expires={lic_expires} reminder_date={today}",
            )
        )
        db.commit()
    finally:
        db.close()

    result = license_renewal_reminders.delay()
    body = result.get()
    assert body["flagged"] == 0


# ---------------------------------------------------------------------------
# org tasks: sharing pattern scan
# ---------------------------------------------------------------------------


def _create_completed_progress(
    account_id: uuid.UUID, unit_id: str, when: datetime, confidence: int
):
    db = SessionLocal()
    try:
        row = Progress(
            account_id=account_id,
            unit_id=unit_id,
            status="completed",
            completed_at=when,
            confidence_post=confidence,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()


def test_sharing_pattern_scan_no_signal():
    account = _create_account("rack211-no-share@example.com")
    product = _create_product("rack211-no-share")
    _create_purchase(
        buyer_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        unit = Unit(
            id="rack211-u1",
            module_code="m0",
            unit_index=1,
            title="Unit 1",
        )
        db.add(unit)
        db.commit()
    finally:
        db.close()

    _create_completed_progress(
        account.id,
        "rack211-u1",
        datetime.now(timezone.utc) - timedelta(days=1),
        3,
    )
    result = sharing_pattern_scan.delay()
    body = result.get()
    assert body["scanned"] >= 1
    assert body["flagged"] == 0


def test_sharing_pattern_scan_flags_and_idempotent():
    account = _create_account("rack211-share@example.com")
    product = _create_product("rack211-share")
    _create_purchase(
        buyer_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        for i in range(15):
            unit = Unit(
                id=f"rack211-share-u{i}",
                module_code="m0",
                unit_index=i,
                title=f"Unit {i}",
            )
            db.add(unit)
        db.commit()
    finally:
        db.close()

    now = datetime.now(timezone.utc)
    for i in range(12):
        _create_completed_progress(
            account.id,
            f"rack211-share-u{i}",
            now - timedelta(hours=i),
            2 + (i % 3),  # oscillating confidence
        )

    result = sharing_pattern_scan.delay()
    body = result.get()
    assert body["scanned"] >= 1
    assert body["flagged"] >= 1

    # Second run with pre-existing flag for today should be idempotent.
    today = datetime.now(timezone.utc).date().isoformat()
    db = SessionLocal()
    try:
        db.add(
            AccountFlag(
                id=uuid.uuid4(),
                account_id=account.id,
                flag="sharing_signal",
                detail=f"date={today} reasons=velocity:12.0/day",
            )
        )
        db.commit()
    finally:
        db.close()

    result = sharing_pattern_scan.delay()
    body = result.get()
    assert body["flagged"] == 0
