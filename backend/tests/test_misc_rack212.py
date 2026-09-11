"""Rack 2.12: misc remaining branch gaps."""

from __future__ import annotations

import json
import pickle
import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from backend.api.routes import session_validation as session_validation_module
from backend.app import main as app_main
from backend.content.curriculum_loader import CurriculumLoader
from backend.core.config import settings
from backend.models.accounts import Account
from backend.models.learning import EstimatorState
from backend.services.account_materializer import materialize
from backend.services.auth_provider import (
    AuthClaims,
    MagicAuthProvider,
    get_auth_provider,
)
from backend.services.auth_verifier import AuthError, verify_token
from backend.services.estimator_state import get_last_stability, load_state, save_state
from backend.services.mock_parser import MOCK_NAMESPACE


def _auth_user_id(email: str) -> uuid.UUID:
    return uuid.uuid5(MOCK_NAMESPACE, email.lower())


# ---------------------------------------------------------------------------
# me.py routes
# ---------------------------------------------------------------------------


def test_me_cancel_delete_returns_409_when_no_pending(client, auth_headers):
    client.headers.update(auth_headers("rack212-cancel@example.com"))
    resp = client.post("/api/v1/me/delete/cancel")
    assert resp.status_code == 409
    assert resp.json()["detail"]["envelope_id"] == "account.delete_not_pending"


# ---------------------------------------------------------------------------
# session validation
# ---------------------------------------------------------------------------


def test_session_validate_returns_false_for_missing_subject(client, monkeypatch):
    fake_claims = AuthClaims(
        auth_user_id=None,
        email="rack212-no-subject@example.com",
        display_name=None,
        subject="rack212-no-subject@example.com",
    )
    monkeypatch.setattr(
        session_validation_module, "verify_token", lambda _token: fake_claims
    )
    resp = client.get(
        "/api/v1/session/validate",
        headers={"Authorization": "Bearer anything"},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


# ---------------------------------------------------------------------------
# main app lifecycle / routes
# ---------------------------------------------------------------------------


def test_liveness_endpoint(client):
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "alive"


def test_security_headers_middleware_adds_hsts_in_production(client, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "Strict-Transport-Security" in resp.headers


def test_verify_production_secrets_raises_on_empty_secret(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "clerk")
    monkeypatch.setattr(settings, "SECRET_KEY", "")
    monkeypatch.setattr(
        settings, "SESSION_SECRET", "a-strong-random-key-32chars-xyzabc"
    )
    with pytest.raises(RuntimeError, match="is empty"):
        app_main._verify_production_secrets()


# ---------------------------------------------------------------------------
# auth verifier and provider
# ---------------------------------------------------------------------------


def test_verify_token_rejects_unsupported_provider(monkeypatch):
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "unknown")
    with pytest.raises(AuthError) as exc:
        verify_token("some-token")
    assert exc.value.code == "auth.transient_verifier_unavailable"


def test_verify_token_magic_returns_invalid_when_claims_none(monkeypatch):
    fake_provider = MagicMock()
    fake_provider.verify_credential.return_value = None
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "magic")
    monkeypatch.setattr(
        "backend.services.auth_provider.get_auth_provider", lambda: fake_provider
    )
    with pytest.raises(AuthError) as exc:
        verify_token("did:token")
    assert exc.value.code == "auth.signature_invalid"


def test_magic_auth_provider_fetch_user_profile_returns_none_when_token_fails(
    monkeypatch,
):
    monkeypatch.setattr(
        "backend.services.auth_provider.fetch_user_profile_by_token", lambda _t: None
    )
    provider = MagicAuthProvider()
    assert provider.fetch_user_profile("sub-1", credential="did-token") is None


def test_get_auth_provider_raises_for_unknown_provider(monkeypatch):
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "clerk")
    with pytest.raises(RuntimeError, match="Unsupported AUTH_PROVIDER"):
        get_auth_provider()


# ---------------------------------------------------------------------------
# curriculum loader
# ---------------------------------------------------------------------------


def test_curriculum_loader_get_unit_returns_none_when_not_found(tmp_path, monkeypatch):
    module_path = tmp_path / "module_0.json"
    module_path.write_text(json.dumps({"units": [{"unit_id": "u1"}]}))
    monkeypatch.setattr(
        "backend.content.curriculum_loader._CONTENT_DIR", tmp_path, raising=False
    )
    assert CurriculumLoader.get_unit(0, "u2") is None


def test_curriculum_loader_get_unit_returns_none_when_file_missing(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "backend.content.curriculum_loader._CONTENT_DIR", tmp_path, raising=False
    )
    assert CurriculumLoader.get_unit(0, "u1") is None


# ---------------------------------------------------------------------------
# estimator state
# ---------------------------------------------------------------------------


def test_load_state_returns_none_for_corrupted_blob(db_session):
    account_id = uuid.uuid4()
    db_session.add(
        Account(
            id=account_id,
            auth_user_id=account_id,
            email="rack212-estimator@example.com",
        )
    )
    db_session.add(
        EstimatorState(
            account_id=account_id,
            scope="global",
            state_blob=b"not a pickle",
            last_stability=None,
        )
    )
    db_session.commit()
    assert load_state(db_session, account_id) is None


def test_save_state_updates_existing_row(db_session):
    account_id = uuid.uuid4()
    db_session.add(
        Account(
            id=account_id,
            auth_user_id=account_id,
            email="rack212-estimator2@example.com",
        )
    )
    db_session.add(
        EstimatorState(
            account_id=account_id,
            scope="global",
            state_blob=pickle.dumps({"old": 1}),
            last_stability=Decimal("0.5"),
        )
    )
    db_session.commit()
    save_state(db_session, account_id, {"new": 2}, last_stability=0.9)
    db_session.commit()
    assert get_last_stability(db_session, account_id) == pytest.approx(0.9)


def test_get_last_stability_returns_none_for_missing(db_session):
    assert get_last_stability(db_session, uuid.uuid4()) is None


# ---------------------------------------------------------------------------
# account materializer
# ---------------------------------------------------------------------------


def test_materialize_records_email_collision(db_session):
    email = "rack212-collision@example.com"
    existing_id = _auth_user_id(email)
    existing = Account(
        id=uuid.uuid4(),
        auth_user_id=existing_id,
        email=email,
        display_name=None,
    )
    db_session.add(existing)
    db_session.commit()

    new_claims = AuthClaims(
        auth_user_id=uuid.uuid5(MOCK_NAMESPACE, "other"),
        email=email,
        display_name=None,
        subject="other",
    )
    account = materialize(db_session, new_claims)
    assert account is not None


def test_materialize_raises_when_no_row_after_insert(db_session, monkeypatch):
    # Force insert to no-op and query to return no row.
    monkeypatch.setattr(db_session, "execute", lambda _stmt: None)

    class _EmptyQuery:
        def filter(self, *args, **kwargs):
            return self

        def one_or_none(self):
            return None

    monkeypatch.setattr(db_session, "query", lambda *args: _EmptyQuery())
    monkeypatch.setattr(db_session, "flush", lambda: None)

    claims = AuthClaims(
        auth_user_id=uuid.uuid4(),
        email="rack212-conflict@example.com",
        display_name=None,
        subject="rack212-conflict@example.com",
    )
    with pytest.raises(AuthError) as exc:
        materialize(db_session, claims)
    assert exc.value.code == "auth.transient_db_unavailable"
