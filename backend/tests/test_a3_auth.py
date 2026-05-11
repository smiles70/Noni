"""Sprint A3 — authentication and session integration tests.

Covers:
  - happy-path sign-in via mock provider
  - whoami requires session
  - sign-out revokes session row + clears cookie
  - tampered cookie is rejected
  - revoked session does not authenticate
  - invalid credential returns 401 with auth.signed_out envelope id

Requires Postgres (UUID / CITEXT / INET types).
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.core.config import settings

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A3 auth tests require Postgres.",
)


@pytest.fixture()
def client():
    return TestClient(app)


def _mock_credential(email: str) -> str:
    return f"mock:{email}"


def test_callback_creates_account_and_session(client):
    r = client.post(
        "/auth/callback", json={"credential": _mock_credential("a3-new@example.test")}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == "a3-new@example.test"
    assert settings.SESSION_COOKIE_NAME in r.cookies


def test_whoami_returns_account_after_callback(client):
    client.post(
        "/auth/callback",
        json={"credential": _mock_credential("a3-whoami@example.test")},
    )
    r = client.get("/auth/whoami")
    assert r.status_code == 200
    assert r.json()["email"] == "a3-whoami@example.test"


def test_whoami_without_cookie_returns_401(client):
    r = client.get("/auth/whoami")
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_signout_revokes_session_and_clears_cookie(client):
    client.post(
        "/auth/callback",
        json={"credential": _mock_credential("a3-signout@example.test")},
    )
    r = client.post("/auth/signout")
    assert r.status_code == 200
    assert r.json()["signed_out"] is True
    # Whoami must now reject.
    r2 = client.get("/auth/whoami")
    assert r2.status_code == 401


def test_invalid_credential_returns_401(client):
    r = client.post("/auth/callback", json={"credential": "not-a-mock-token"})
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_tampered_cookie_is_rejected(client):
    client.post(
        "/auth/callback",
        json={"credential": _mock_credential("a3-tamper@example.test")},
    )
    raw = client.cookies.get(settings.SESSION_COOKIE_NAME)
    assert raw and "." in raw
    # Flip a byte in the signature half.
    head, _, sig = raw.rpartition(".")
    tampered = head + "." + ("A" if sig[0] != "A" else "B") + sig[1:]
    client.cookies.set(settings.SESSION_COOKIE_NAME, tampered)
    r = client.get("/auth/whoami")
    assert r.status_code == 401


def test_repeat_signin_for_same_email_reuses_account(client):
    cred = _mock_credential("a3-repeat@example.test")
    r1 = client.post("/auth/callback", json={"credential": cred})
    id1 = r1.json()["account_id"]
    client.post("/auth/signout")
    client.cookies.clear()
    r2 = client.post("/auth/callback", json={"credential": cred})
    id2 = r2.json()["account_id"]
    assert id1 == id2, "auth_user_id is deterministic from email in mock provider"
