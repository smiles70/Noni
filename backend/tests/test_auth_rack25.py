"""Rack 2.5: auth routes and auth-provider/verifier branch coverage backfill."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.services import auth_verifier
from backend.services.auth_provider import (
    AuthClaims,
    MagicAuthProvider,
    MockAuthProvider,
    UserProfile,
    get_auth_provider,
)
from backend.services.mock_parser import MOCK_NAMESPACE


def _auth_user_id(email: str) -> uuid.UUID:
    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


def _create_account(
    *,
    email: str,
    display_name: str | None = None,
    deleted_at: datetime | None = None,
    auth_user_id: uuid.UUID | None = None,
) -> Account:
    db = SessionLocal()
    try:
        account = Account(
            id=uuid.uuid4(),
            auth_user_id=auth_user_id or _auth_user_id(email),
            email=email,
            display_name=display_name,
            deleted_at=deleted_at,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        db.expunge(account)
        return account
    finally:
        db.close()


def _auth(email: str) -> dict:
    return {"Authorization": f"Bearer mock:{email}"}


# ---------------------------------------------------------------------------
# /api/v1/auth/session
# ---------------------------------------------------------------------------


def test_auth_session_missing_header(client):
    r = client.get("/api/v1/auth/session")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.no_credential"


def test_auth_session_malformed_token(client):
    r = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer mock:bad"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.malformed"


def test_auth_session_missing_subject(client, monkeypatch):
    import backend.api.routes.auth as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "verify_token",
        lambda _token: AuthClaims(auth_user_id=None),  # type: ignore[arg-type]
    )
    r = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer mock:any@example.com"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.subject_missing"


def test_auth_session_deleted_account(client):
    account = _create_account(
        email="rack25-deleted@example.com",
        deleted_at=datetime.now(timezone.utc),
    )
    r = client.get("/api/v1/auth/session", headers=_auth(account.email))
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.account_deleted"


def test_auth_session_unmaterialized(client):
    r = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer mock:rack25-new@example.com"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["materialized"] is False
    assert body["subject"] == "rack25-new@example.com"


def test_auth_session_materialized(client):
    account = _create_account(email="rack25-session@example.com")
    r = client.get("/api/v1/auth/session", headers=_auth(account.email))
    assert r.status_code == 200
    body = r.json()
    assert body["materialized"] is True
    assert body["account_id"] == str(account.id)
    assert body["email"] == account.email


# ---------------------------------------------------------------------------
# /api/v1/auth/session/init
# ---------------------------------------------------------------------------


def test_auth_session_init_missing_header(client):
    r = client.post("/api/v1/auth/session/init")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.no_credential"


def test_auth_session_init_malformed_token(client):
    r = client.post(
        "/api/v1/auth/session/init",
        headers={"Authorization": "Bearer mock:bad"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.malformed"


def test_auth_session_init_missing_subject(client, monkeypatch):
    import backend.api.routes.auth as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "verify_token",
        lambda _token: AuthClaims(auth_user_id=None),  # type: ignore[arg-type]
    )
    r = client.post(
        "/api/v1/auth/session/init",
        headers={"Authorization": "Bearer mock:any@example.com"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.subject_missing"


def test_auth_session_init_existing_account(client):
    account = _create_account(email="rack25-init-existing@example.com")
    r = client.post("/api/v1/auth/session/init", headers=_auth(account.email))
    assert r.status_code == 200
    assert r.json()["account_id"] == str(account.id)


def test_auth_session_init_existing_deleted_account(client):
    account = _create_account(
        email="rack25-init-deleted@example.com",
        deleted_at=datetime.now(timezone.utc),
    )
    r = client.post("/api/v1/auth/session/init", headers=_auth(account.email))
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.account_deleted"


def test_auth_session_init_creates_new_account(client):
    r = client.post(
        "/api/v1/auth/session/init",
        headers={"Authorization": "Bearer mock:rack25-init-new@example.com"},
    )
    assert r.status_code == 200
    assert "account_id" in r.json()


def test_auth_session_init_race_recovery(client):
    email = "rack25-race@example.com"
    auth_id = _auth_user_id(email)
    account = _create_account(email=email, auth_user_id=auth_id)
    # Same auth_user_id will trigger IntegrityError on insert, then recovery.
    r = client.post(
        "/api/v1/auth/session/init",
        headers={"Authorization": f"Bearer mock:{email}"},
    )
    assert r.status_code == 200
    assert r.json()["account_id"] == str(account.id)


def test_auth_session_init_magic_fetches_profile(client, monkeypatch):
    """Cover the `if not claims.email` branch in auth_session_init."""
    import backend.api.routes.auth as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "verify_token",
        lambda _token: AuthClaims(
            auth_user_id=uuid.uuid5(MOCK_NAMESPACE, "magic-sub"),
            email=None,
            subject="magic-sub",
        ),  # type: ignore[arg-type]
    )
    monkeypatch.setattr(
        auth_routes,
        "get_auth_provider",
        lambda: MagicAuthProvider(),
    )
    monkeypatch.setattr(
        MagicAuthProvider,
        "fetch_user_profile",
        lambda _self, _subject, _credential: UserProfile(
            email="rack25-magic@example.com"
        ),
    )

    r = client.post(
        "/api/v1/auth/session/init",
        headers={"Authorization": "Bearer did:abc"},
    )
    assert r.status_code == 200
    assert "account_id" in r.json()


def test_auth_session_init_magic_profile_unavailable(client, monkeypatch):
    """Cover the transient verifier failure branch when profile fetch fails."""
    import backend.api.routes.auth as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "verify_token",
        lambda _token: AuthClaims(
            auth_user_id=uuid.uuid5(MOCK_NAMESPACE, "magic-sub2"),
            email=None,
            subject="magic-sub2",
        ),  # type: ignore[arg-type]
    )
    monkeypatch.setattr(
        auth_routes,
        "get_auth_provider",
        lambda: MagicAuthProvider(),
    )
    monkeypatch.setattr(
        MagicAuthProvider,
        "fetch_user_profile",
        lambda _self, _subject, _credential: None,
    )

    r = client.post(
        "/api/v1/auth/session/init",
        headers={"Authorization": "Bearer did:abc"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.transient_verifier_unavailable"


# ---------------------------------------------------------------------------
# auth_provider
# ---------------------------------------------------------------------------


def test_get_auth_provider_unsupported(monkeypatch):
    from backend.core.config import settings

    monkeypatch.setattr(settings, "AUTH_PROVIDER", "clerk")
    try:
        get_auth_provider()
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "Unsupported AUTH_PROVIDER" in str(exc)


def test_mock_provider_invalid_credential():
    assert MockAuthProvider().verify_credential("not-mock") is None
    assert MockAuthProvider().verify_credential("mock:") is None


def test_mock_provider_fetch_user_profile_returns_none():
    assert MockAuthProvider().fetch_user_profile("any") is None


def test_magic_provider_verify_credential_returns_none(monkeypatch):
    monkeypatch.setattr(
        "backend.services.auth_provider.validate_did_token", lambda _token: None
    )
    assert MagicAuthProvider().verify_credential("did:bad") is None


def test_magic_provider_verify_credential_missing_sub(monkeypatch):
    monkeypatch.setattr(
        "backend.services.auth_provider.validate_did_token",
        lambda _token: {"sub": ""},
    )
    assert MagicAuthProvider().verify_credential("did:missing-sub") is None


def test_magic_provider_fetch_user_profile_missing_credential():
    assert MagicAuthProvider().fetch_user_profile("sub", "") is None


def test_magic_provider_fetch_user_profile_missing_email(monkeypatch):
    monkeypatch.setattr(
        "backend.services.auth_provider.fetch_user_profile_by_token",
        lambda _token: {"email": ""},
    )
    assert MagicAuthProvider().fetch_user_profile("sub", "did:abc") is None


# ---------------------------------------------------------------------------
# auth_verifier
# ---------------------------------------------------------------------------


def test_auth_error_rejects_unknown_code():
    try:
        auth_verifier.AuthError("unknown.code")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Unknown AuthError code" in str(exc)


def test_parse_bearer_rejects_malformed_headers():
    assert auth_verifier.parse_bearer(None) is None
    assert auth_verifier.parse_bearer("Basic foo") is None
    assert auth_verifier.parse_bearer("Bearer") is None
    assert auth_verifier.parse_bearer("Bearer ") is None


def test_verify_token_no_credential():
    for token in (None, ""):
        try:
            auth_verifier.verify_token(token)  # type: ignore[arg-type]
            assert False, "expected AuthError"
        except auth_verifier.AuthError as err:
            assert err.code == "auth.no_credential"


def test_verify_token_unsupported_provider(monkeypatch):
    from backend.core.config import settings

    monkeypatch.setattr(settings, "AUTH_PROVIDER", "clerk")
    try:
        auth_verifier.verify_token("mock:test@example.com")
        assert False, "expected AuthError"
    except auth_verifier.AuthError as err:
        assert err.code == "auth.transient_verifier_unavailable"


def test_verify_token_magic_signature_invalid(monkeypatch):
    from backend.core.config import settings

    monkeypatch.setattr(settings, "AUTH_PROVIDER", "magic")
    monkeypatch.setattr(
        MagicAuthProvider,
        "verify_credential",
        lambda _self, _credential: None,
    )
    try:
        auth_verifier.verify_token("did:invalid")
        assert False, "expected AuthError"
    except auth_verifier.AuthError as err:
        assert err.code == "auth.signature_invalid"
