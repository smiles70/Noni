"""Rack 2.9: gifts, entitlements, and org quota branch coverage backfill."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.models.organizations import AccessCode, OrgLicense, Organization
from backend.services import entitlements, org_quota
from backend.services.gifts import (
    GiftClaimError,
    _hash,
    claim,
    issue_token,
    lookup_for_redemption,
)
from backend.services.mock_parser import MOCK_NAMESPACE


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


def _issue_token_for(purchase: Purchase) -> str:
    db = SessionLocal()
    try:
        db.add(purchase)
        token = issue_token(db, purchase)
        db.commit()
        return token
    finally:
        db.close()


# ---------------------------------------------------------------------------
# gifts.issue_token / claim / lookup_for_redemption
# ---------------------------------------------------------------------------


def test_claim_rejects_empty_token():
    account = _create_account("rack29-empty-token@example.com")
    db = SessionLocal()
    try:
        with pytest.raises(GiftClaimError, match="empty_token"):
            claim(db, raw_token="", beneficiary_account=account)
    finally:
        db.close()


def test_claim_rejects_unknown_token():
    account = _create_account("rack29-not-found@example.com")
    db = SessionLocal()
    try:
        with pytest.raises(GiftClaimError, match="not_found"):
            claim(db, raw_token="not-a-token", beneficiary_account=account)
    finally:
        db.close()


def test_claim_rejects_unpaid_purchase():
    product = _create_product("rack29-unpaid")
    buyer = _create_account("rack29-unpaid-buyer@example.com")
    beneficiary = _create_account("rack29-unpaid-ben@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        beneficiary_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
    )
    token = _issue_token_for(purchase)

    db = SessionLocal()
    try:
        with pytest.raises(GiftClaimError, match="unpaid_purchase"):
            claim(db, raw_token=token, beneficiary_account=beneficiary)
    finally:
        db.close()


def test_claim_rejects_already_claimed():
    product = _create_product("rack29-claimed")
    buyer = _create_account("rack29-claimed-buyer@example.com")
    beneficiary = _create_account("rack29-claimed-ben@example.com")
    raw = "already-claimed-token"
    _create_purchase(
        buyer_account_id=buyer.id,
        beneficiary_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        gift_claim_token_hash=_hash(raw),
        gift_claimed_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        with pytest.raises(GiftClaimError, match="already_claimed"):
            claim(db, raw_token=raw, beneficiary_account=beneficiary)
    finally:
        db.close()


def test_claim_rejects_refunded_purchase():
    product = _create_product("rack29-refunded")
    buyer = _create_account("rack29-refunded-buyer@example.com")
    beneficiary = _create_account("rack29-refunded-ben@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        beneficiary_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="refunded",
        refunded_at=datetime.now(timezone.utc),
    )
    token = _issue_token_for(purchase)

    db = SessionLocal()
    try:
        with pytest.raises(GiftClaimError, match="refunded"):
            claim(db, raw_token=token, beneficiary_account=beneficiary)
    finally:
        db.close()


def test_claim_rejects_refunded_but_paid_purchase():
    product = _create_product("rack29-refunded-paid")
    buyer = _create_account("rack29-refunded-paid-buyer@example.com")
    beneficiary = _create_account("rack29-refunded-paid-ben@example.com")
    raw = "refunded-paid-token"
    _create_purchase(
        buyer_account_id=buyer.id,
        beneficiary_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        gift_claim_token_hash=_hash(raw),
        refunded_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        with pytest.raises(GiftClaimError, match="refunded"):
            claim(db, raw_token=raw, beneficiary_account=beneficiary)
    finally:
        db.close()


def test_claim_succeeds_and_grants_entitlement():
    product = _create_product("rack29-success")
    buyer = _create_account("rack29-success-buyer@example.com")
    beneficiary = _create_account("rack29-success-ben@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        beneficiary_account_id=None,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    token = _issue_token_for(purchase)

    db = SessionLocal()
    try:
        claimed = claim(db, raw_token=token, beneficiary_account=beneficiary)
        db.commit()
        assert claimed.beneficiary_account_id == beneficiary.id
        assert claimed.gift_claimed_at is not None
        assert claimed.gift_claim_token_hash is None
        assert entitlements.has_active(db, beneficiary.id, product.code) is True
    finally:
        db.close()


# ---------------------------------------------------------------------------
# lookup_for_redemption
# ---------------------------------------------------------------------------


def test_lookup_for_redemption_no_match():
    db = SessionLocal()
    try:
        assert lookup_for_redemption(db, "nope") is None
    finally:
        db.close()


def test_lookup_for_redemption_unpaid():
    product = _create_product("rack29-lookup-unpaid")
    buyer = _create_account("rack29-lookup-unpaid-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="pending",
    )
    token = _issue_token_for(purchase)

    db = SessionLocal()
    try:
        assert lookup_for_redemption(db, token) is None
    finally:
        db.close()


def test_lookup_for_redemption_already_claimed():
    product = _create_product("rack29-lookup-claimed")
    buyer = _create_account("rack29-lookup-claimed-buyer@example.com")
    raw = "lookup-claimed-token"
    _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        gift_claim_token_hash=_hash(raw),
        gift_claimed_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        assert lookup_for_redemption(db, raw) is None
    finally:
        db.close()


def test_lookup_for_redemption_refunded():
    product = _create_product("rack29-lookup-refunded")
    buyer = _create_account("rack29-lookup-refunded-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="refunded",
        refunded_at=datetime.now(timezone.utc),
    )
    token = _issue_token_for(purchase)

    db = SessionLocal()
    try:
        assert lookup_for_redemption(db, token) is None
    finally:
        db.close()


def test_lookup_for_redemption_refunded_but_paid():
    product = _create_product("rack29-lookup-refunded-paid")
    buyer = _create_account("rack29-lookup-refunded-paid-buyer@example.com")
    raw = "lookup-refunded-paid-token"
    _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
        gift_claim_token_hash=_hash(raw),
        refunded_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    try:
        assert lookup_for_redemption(db, raw) is None
    finally:
        db.close()


def test_lookup_for_redemption_success():
    product = _create_product("rack29-lookup-success")
    buyer = _create_account("rack29-lookup-success-buyer@example.com")
    purchase = _create_purchase(
        buyer_account_id=buyer.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    token = _issue_token_for(purchase)

    db = SessionLocal()
    try:
        found = lookup_for_redemption(db, token)
        assert found is not None
        assert found.product_code == product.code
    finally:
        db.close()


# ---------------------------------------------------------------------------
# entitlements
# ---------------------------------------------------------------------------


def test_entitlement_idempotent_for_active_grant():
    product = _create_product("rack29-active-twice")
    account = _create_account("rack29-active-twice@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    db = SessionLocal()
    try:
        first = entitlements.grant(
            db,
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
        )
        second = entitlements.grant(
            db,
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
        )
        assert first.account_id == second.account_id
        assert first.product_code == second.product_code
        assert second.revoked_at is None
    finally:
        db.close()


def test_entitlement_reactivates_revoked_grant():
    product = _create_product("rack29-reactivate")
    account = _create_account("rack29-reactivate@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    db = SessionLocal()
    try:
        ent = entitlements.grant(
            db,
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
        )
        ent.revoked_at = datetime.now(timezone.utc)
        ent.revocation_reason = "refund"
        db.flush()
        reactivated = entitlements.grant(
            db,
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
        )
        assert reactivated.revoked_at is None
        assert reactivated.revocation_reason is None
    finally:
        db.close()


def test_entitlement_grant_raises_on_unknown_product():
    account = _create_account("rack29-unknown-prod@example.com")
    db = SessionLocal()
    try:
        with pytest.raises(ValueError, match="unknown product_code"):
            entitlements.grant(
                db,
                account_id=account.id,
                product_code="does-not-exist",
                granted_by_purchase_id=uuid.uuid4(),
            )
    finally:
        db.close()


def test_revoke_noop_without_entitlement():
    account = _create_account("rack29-no-entitlement@example.com")
    db = SessionLocal()
    try:
        result = entitlements.revoke(
            db, account_id=account.id, product_code="does-not-exist"
        )
        assert result is None
    finally:
        db.close()


def test_revoke_noop_already_revoked():
    product = _create_product("rack29-revoke-twice")
    account = _create_account("rack29-revoke-twice@example.com")
    purchase = _create_purchase(
        buyer_account_id=account.id,
        beneficiary_account_id=account.id,
        product_code=product.code,
        amount_cents=product.price_cents,
        currency=product.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    db = SessionLocal()
    try:
        entitlements.grant(
            db,
            account_id=account.id,
            product_code=product.code,
            granted_by_purchase_id=purchase.id,
        )
        entitlements.revoke(db, account_id=account.id, product_code=product.code)
        second = entitlements.revoke(
            db, account_id=account.id, product_code=product.code
        )
        assert second is not None
        assert second.revoked_at is not None
    finally:
        db.close()


# ---------------------------------------------------------------------------
# org_quota
# ---------------------------------------------------------------------------


class _FakeRedis:
    def __init__(self, get_value=None, eval_result=None, raise_on=None):
        self._get_value = get_value
        self._eval_result = eval_result
        self._raise_on = raise_on or set()
        self._store = {}

    def get(self, key):
        if "get" in self._raise_on:
            raise RuntimeError("redis down")
        return self._store.get(key, self._get_value)

    def setex(self, key, ttl, value):
        if "setex" in self._raise_on:
            raise RuntimeError("redis down")
        self._store[key] = value

    def eval(self, script, numkeys, *args):
        if "eval" in self._raise_on:
            raise RuntimeError("redis down")
        return self._eval_result


def _patch_redis_client(monkeypatch, fake):
    """Both org_quota and rate_limit import _get_redis_client from rate_limit."""
    monkeypatch.setattr("backend.services.rate_limit._get_redis_client", lambda: fake)
    monkeypatch.setattr("backend.services.org_quota._get_redis_client", lambda: fake)


def test_resolve_org_id_uses_redis_cache(monkeypatch):
    account = _create_account("rack29-org-cache@example.com")
    product = _create_product("rack29-org-cache-prod")
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
            name="Cached Org",
            contact_email="org@example.com",
            admin_email="admin@example.com",
        )
        db.add(org)
        db.flush()
        license = OrgLicense(
            organization_id=org.id,
            product_code=product.code,
            purchase_id=purchase.id,
        )
        db.add(license)
        db.flush()
        code = AccessCode(
            code_hash="CACHED01",
            license_id=license.id,
            claimed_by_account_id=account.id,
            claimed_at=datetime.now(timezone.utc),
        )
        db.add(code)
        db.commit()
        org_id = str(org.id)
    finally:
        db.close()

    fake = _FakeRedis(get_value=org_id)
    _patch_redis_client(monkeypatch, fake)

    db = SessionLocal()
    try:
        resolved = org_quota.resolve_org_id(db, account.id)
        assert resolved == org_id
    finally:
        db.close()


def test_resolve_org_id_caches_negative_and_setex_swallows_error(monkeypatch):
    account = _create_account("rack29-org-neg@example.com")
    fake = _FakeRedis(get_value=None)
    _patch_redis_client(monkeypatch, fake)

    db = SessionLocal()
    try:
        result = org_quota.resolve_org_id(db, account.id)
        assert result is None
    finally:
        db.close()

    # setex exception should be swallowed and the function still returns None.
    fake2 = _FakeRedis(get_value=None, raise_on={"setex"})
    _patch_redis_client(monkeypatch, fake2)
    db = SessionLocal()
    try:
        result = org_quota.resolve_org_id(db, account.id)
        assert result is None
    finally:
        db.close()


def test_resolve_org_id_swallows_redis_get_exception(monkeypatch):
    account = _create_account("rack29-org-redis-get-err@example.com")
    fake = _FakeRedis(get_value=None, raise_on={"get"})
    _patch_redis_client(monkeypatch, fake)

    db = SessionLocal()
    try:
        result = org_quota.resolve_org_id(db, account.id)
        assert result is None
    finally:
        db.close()


def test_org_admission_allowed_uses_redis_token_bucket(monkeypatch):
    fake = _FakeRedis(eval_result=1)
    _patch_redis_client(monkeypatch, fake)
    assert org_quota.org_admission_allowed("org-001") is True

    fake2 = _FakeRedis(eval_result=0)
    _patch_redis_client(monkeypatch, fake2)
    assert org_quota.org_admission_allowed("org-001") is False

    fake3 = _FakeRedis(eval_result=0, raise_on={"eval"})
    _patch_redis_client(monkeypatch, fake3)
    assert org_quota.org_admission_allowed("org-001") is True
