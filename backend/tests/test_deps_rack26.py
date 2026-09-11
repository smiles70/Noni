"""Rack 2.6: FastAPI dependency layer branch coverage backfill."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from backend.api import deps
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.services.auth_provider import AuthClaims, UserProfile


def _auth_user_id(email: str) -> uuid.UUID:
    from backend.services.mock_parser import MOCK_NAMESPACE

    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


def _db():
    return SessionLocal()


def _create_account(**kwargs):
    db = _db()
    try:
        account = Account(**kwargs)
        db.add(account)
        db.commit()
        db.refresh(account)
        db.expunge(account)
        return account
    finally:
        db.close()


# ---------------------------------------------------------------------------
# _parse_bearer
# ---------------------------------------------------------------------------


def test_parse_bearer_rejects_empty_token():
    # Two spaces so split(None, 1) yields ['Bearer', '']
    assert deps._parse_bearer("Bearer  ") is None


# ---------------------------------------------------------------------------
# get_optional_account
# ---------------------------------------------------------------------------


def test_get_optional_account_staff_token_returns_none():
    db = _db()
    try:
        assert deps.get_optional_account("Bearer staff.anything", db) is None
    finally:
        db.close()


def test_get_optional_account_invalid_token_returns_none():
    db = _db()
    try:
        assert deps.get_optional_account("Bearer not-mock", db) is None
    finally:
        db.close()


def test_get_optional_account_creates_account():
    db = _db()
    try:
        account = deps.get_optional_account(
            "Bearer mock:rack26-optional@example.com", db
        )
        assert account is not None
        assert account.email == "rack26-optional@example.com"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# _upsert_account
# ---------------------------------------------------------------------------


class _FakeProvider:
    def __init__(self, profile: UserProfile | None = None):
        self._profile = profile

    def verify_credential(self, credential: str):
        raise NotImplementedError

    def fetch_user_profile(self, subject: str, credential=None):
        return self._profile


def test_upsert_account_updates_email_and_display_name():
    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-update@example.com"),
        email="rack26-update@example.com",
        display_name="Old",
    )
    db = _db()
    try:
        claims = AuthClaims(
            auth_user_id=account.auth_user_id,
            email="rack26-update-new@example.com",
            display_name="New",
            subject="sub",
        )
        updated, changed = deps._upsert_account(db, claims, _FakeProvider())
        assert changed is True
        assert updated.email == "rack26-update-new@example.com"
        assert updated.display_name == "New"
    finally:
        db.close()


def test_upsert_account_updates_updated_at_when_stale():
    old = datetime.now(timezone.utc) - timedelta(seconds=90)
    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-stale@example.com"),
        email="rack26-stale@example.com",
        updated_at=old,
    )
    db = _db()
    try:
        claims = AuthClaims(
            auth_user_id=account.auth_user_id,
            email="rack26-stale@example.com",
            subject="sub",
        )
        updated, changed = deps._upsert_account(db, claims, _FakeProvider())
        assert changed is True
        assert updated.updated_at > old
    finally:
        db.close()


def test_upsert_account_fetches_profile_when_email_missing():
    db = _db()
    try:
        auth_id = uuid.uuid4()
        claims = AuthClaims(
            auth_user_id=auth_id,
            subject="rack26-subject",
        )
        provider = _FakeProvider(
            UserProfile(email="rack26-fetched@example.com", display_name="Fetched")
        )
        account, changed = deps._upsert_account(db, claims, provider, "token")
        assert changed is True
        assert account is not None
        assert account.email == "rack26-fetched@example.com"
        assert account.display_name == "Fetched"
    finally:
        db.close()


def test_upsert_account_returns_none_when_no_email_and_no_profile():
    db = _db()
    try:
        auth_id = uuid.uuid4()
        claims = AuthClaims(auth_user_id=auth_id, subject="rack26-no-profile")
        account, changed = deps._upsert_account(db, claims, _FakeProvider())
        assert account is None
        assert changed is False
    finally:
        db.close()


def test_upsert_account_returns_new_account_when_no_conflict():
    db = _db()
    try:
        auth_id = uuid.uuid4()
        claims = AuthClaims(
            auth_user_id=auth_id,
            email="rack26-new@example.com",
            subject="sub",
        )
        account, changed = deps._upsert_account(db, claims, _FakeProvider())
        assert changed is True
        assert account is not None
        assert account.email == "rack26-new@example.com"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# get_current_account
# ---------------------------------------------------------------------------


def test_get_current_account_requires_account():
    with pytest.raises(HTTPException) as exc_info:
        deps.get_current_account(None)
    assert exc_info.value.status_code == 401


def test_get_current_account_rejects_suspended():
    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-suspended@example.com"),
        email="rack26-suspended@example.com",
        suspended_at=datetime.now(timezone.utc),
    )
    with pytest.raises(HTTPException) as exc_info:
        deps.get_current_account(account)
    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# org_fair_share
# ---------------------------------------------------------------------------


def test_org_fair_share_enforces_quota(monkeypatch):
    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-quota@example.com"),
        email="rack26-quota@example.com",
    )
    db = _db()
    try:
        monkeypatch.setattr(
            "backend.services.org_quota.resolve_org_id",
            lambda _db, _account_id: str(account.id),
        )
        monkeypatch.setattr(
            "backend.services.org_quota.org_admission_allowed",
            lambda _org_id: False,
        )
        with pytest.raises(HTTPException) as exc_info:
            deps.org_fair_share(account, db)
        assert exc_info.value.status_code == 429
        assert exc_info.value.headers.get("Retry-After") == "10"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# require_staff / require_admin
# ---------------------------------------------------------------------------


def test_require_staff_allows_allowlisted_account(monkeypatch):
    from backend.core.config import settings

    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-staff@example.com"),
        email="rack26-staff@example.com",
    )
    monkeypatch.setattr(settings, "ADMIN_ACCOUNT_IDS", str(account.id))
    db = _db()
    try:
        result = deps.require_staff(authorization=None, db=db, account=account)
        assert result.id == account.id
    finally:
        db.close()


def test_require_admin_rejects_support_role(monkeypatch):
    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-support@example.com"),
        email="rack26-support@example.com",
        staff_role="support",
    )
    with pytest.raises(HTTPException) as exc_info:
        deps.require_admin(account=account)
    assert exc_info.value.status_code == 403


def test_require_entitlement_branches(monkeypatch):
    from backend.services import entitlements

    monkeypatch.setattr(
        entitlements, "has_active", lambda _db, _account_id, _code: False
    )
    dep = deps.require_entitlement("paid-bundle")

    # No account -> sign-in or purchase
    with pytest.raises(HTTPException) as exc_info:
        dep(account=None, db=None)
    assert exc_info.value.status_code == 402
    assert "billing.signin_or_purchase_required" in str(exc_info.value.detail)

    # Account but no grant -> purchase required
    account = _create_account(
        id=uuid.uuid4(),
        auth_user_id=_auth_user_id("rack26-ent@example.com"),
        email="rack26-ent@example.com",
    )
    with pytest.raises(HTTPException) as exc_info:
        dep(account=account, db=None)
    assert exc_info.value.status_code == 402
    assert "billing.purchase_required" in str(exc_info.value.detail)
