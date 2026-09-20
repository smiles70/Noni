"""Rack 2.4: account profile/session validation route coverage backfill."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.services import auth_verifier
from backend.services.auth_provider import AuthClaims
from backend.services.mock_parser import MOCK_NAMESPACE


def _auth_user_id(email: str) -> uuid.UUID:
    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


def _create_account(
    *,
    email: str,
    display_name: str | None = None,
    preferences: str | None = None,
    deleted_at=None,
) -> Account:
    db = SessionLocal()
    try:
        account = Account(
            id=uuid.uuid4(),
            auth_user_id=_auth_user_id(email),
            email=email,
            display_name=display_name,
            preferences=preferences,
            deleted_at=deleted_at,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        db.expunge(account)
        return account
    finally:
        db.close()


# ---------------------------------------------------------------------------
# /api/v1/account/profile
# ---------------------------------------------------------------------------


def test_update_profile_requires_authorization(client):
    r = client.put(
        "/api/v1/account/profile", json={"displayName": "x", "preferences": {}}
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.no_credential"


def test_update_profile_rejects_malformed_token(client):
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "x", "preferences": {}},
        headers={"Authorization": "Bearer mock:not-an-email"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.malformed"


def test_update_profile_rejects_missing_subject(client, monkeypatch):
    monkeypatch.setattr(
        auth_verifier,
        "verify_token",
        lambda _token: AuthClaims(auth_user_id=None),  # type: ignore[arg-type]
    )
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "x", "preferences": {}},
        headers={"Authorization": "Bearer mock:anything@example.com"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.subject_missing"


def test_update_profile_returns_404_for_unknown_account(client):
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "x", "preferences": {}},
        headers={"Authorization": "Bearer mock:unknown-rack24@example.com"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "account.not_found"


def test_update_profile_returns_404_for_deleted_account(client):
    account = _create_account(
        email="rack24-deleted@example.com",
        display_name="Old",
        deleted_at=datetime.now(timezone.utc),
    )
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "New", "preferences": {}},
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "account.not_found"


def test_update_profile_success_and_empty_preferences(client):
    account = _create_account(email="rack24-empty@example.com")
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "  Rack 24  ", "preferences": {}},
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["account_id"] == str(account.id)
    assert body["display_name"] == "Rack 24"
    assert body["preferences"] == {}


def test_update_profile_persists_preferences(client):
    _create_account(email="rack24-prefs@example.com")
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "Prefs", "preferences": {"theme": "dark"}},
        headers={"Authorization": "Bearer mock:rack24-prefs@example.com"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["display_name"] == "Prefs"
    assert body["preferences"] == {"theme": "dark"}


def test_update_profile_handles_invalid_preferences_json(client):
    account = _create_account(
        email="rack24-bad-prefs@example.com", preferences="not-json"
    )
    r = client.put(
        "/api/v1/account/profile",
        json={"displayName": "New Name", "preferences": {}},
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["display_name"] == "New Name"
    assert body["preferences"] == {}


# ---------------------------------------------------------------------------
# /api/v1/account/onboarding-status
# ---------------------------------------------------------------------------


def test_onboarding_status_requires_authorization(client):
    r = client.get("/api/v1/account/onboarding-status")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.no_credential"


def test_onboarding_status_rejects_malformed_token(client):
    r = client.get(
        "/api/v1/account/onboarding-status",
        headers={"Authorization": "Bearer mock:bad"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.malformed"


def test_onboarding_status_returns_404_for_unknown_account(client):
    r = client.get(
        "/api/v1/account/onboarding-status",
        headers={"Authorization": "Bearer mock:unknown-rack24@example.com"},
    )
    assert r.status_code == 404


def test_onboarding_status_incomplete(client):
    account = _create_account(email="rack24-incomplete@example.com")
    r = client.get(
        "/api/v1/account/onboarding-status",
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["account_id"] == str(account.id)
    assert body["onboarding_complete"] is False
    assert body["preferences_set"] is False


def test_onboarding_status_complete(client):
    account = _create_account(
        email="rack24-complete@example.com",
        display_name="Complete",
        preferences='{"theme":"light"}',
    )
    r = client.get(
        "/api/v1/account/onboarding-status",
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["onboarding_complete"] is True
    assert body["preferences_set"] is True
    assert body["display_name"] == "Complete"


# ---------------------------------------------------------------------------
# /api/v1/session/validate
# ---------------------------------------------------------------------------


def test_session_validate_missing_header(client):
    r = client.get("/api/v1/session/validate")
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert body["account_id"] is None


def test_session_validate_malformed_token(client):
    r = client.get(
        "/api/v1/session/validate",
        headers={"Authorization": "Bearer mock:bad"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False


def test_session_validate_missing_subject(client, monkeypatch):
    monkeypatch.setattr(
        auth_verifier,
        "verify_token",
        lambda _token: AuthClaims(auth_user_id=None),  # type: ignore[arg-type]
    )
    r = client.get(
        "/api/v1/session/validate",
        headers={"Authorization": "Bearer mock:any@example.com"},
    )
    assert r.status_code == 200
    assert r.json()["valid"] is False


def test_session_validate_unknown_account(client):
    r = client.get(
        "/api/v1/session/validate",
        headers={"Authorization": "Bearer mock:unknown-rack24@example.com"},
    )
    assert r.status_code == 200
    assert r.json()["valid"] is False


def test_session_validate_deleted_account(client):
    account = _create_account(
        email="rack24-session-deleted@example.com",
        deleted_at=datetime.now(timezone.utc),
    )
    r = client.get(
        "/api/v1/session/validate",
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 200
    assert r.json()["valid"] is False


def test_session_validate_success(client):
    account = _create_account(email="rack24-session@example.com")
    r = client.get(
        "/api/v1/session/validate",
        headers={"Authorization": f"Bearer mock:{account.email}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["account_id"] == str(account.id)
    assert body["expires_in"] == 30 * 60
