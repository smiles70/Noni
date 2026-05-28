"""Sprint A3 — authentication integration tests (Bearer model, ADR 0024).

Covers:
  - happy-path: Bearer mock:<email> materializes via /auth/session/init,
    then /auth/session reads back the account
  - missing Authorization header -> 401 auth.no_credential
  - malformed Authorization (wrong scheme, no token) -> 401
  - invalid mock credential body -> 401
  - sign-out is purely client-side (drop the header) -> next call is 401
  - repeated sign-in for the same email returns the same account_id

Requires Postgres (UUID / CITEXT / INET types).

What changed from the cookie/session era:
  - No /auth/callback (gone): the Bearer is verified per request.
  - No /auth/signout (gone): the frontend handles it via clerk.signOut()
    or by clearing the mock localStorage key. The backend has no
    sign-out endpoint to test.
  - No tampered-cookie test: with no cookie there's nothing to tamper
    with at the transport layer. JWT signature tampering for the Clerk
    provider is covered separately under the Clerk provider unit
    tests.
  - /auth/whoami removed (Safe Yellow sprint): tests now use the
    redesigned /auth/session + /auth/session/init flow.
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


def _bearer(email: str) -> dict:
    """Authorization header for a mock provider sign-in.

    `Bearer mock:<email>` is parsed by `get_optional_account`, which
    strips the `Bearer ` prefix and hands `mock:<email>` to the
    MockAuthProvider's `verify_credential`. Same surface area as the
    Clerk provider receives in production.
    """
    return {"Authorization": f"Bearer mock:{email}"}


def test_session_with_bearer_materializes_then_reads(client):
    # STEP 1: materialize the account (POST /auth/session/init).
    r_init = client.post(
        "/api/v1/auth/session/init",
        headers=_bearer("a3-new@example.test"),
    )
    assert r_init.status_code == 200, r_init.text
    # STEP 2: read back the materialized account (GET /auth/session).
    r = client.get("/api/v1/auth/session", headers=_bearer("a3-new@example.test"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["materialized"] is True
    assert body["email"] == "a3-new@example.test"
    # No Set-Cookie in the Bearer model.
    assert settings.SESSION_COOKIE_NAME not in r.cookies


def test_session_without_header_returns_401(client):
    r = client.get("/api/v1/auth/session")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.no_credential"


def test_session_with_malformed_header_returns_401(client):
    # Wrong scheme.
    r1 = client.get("/api/v1/auth/session", headers={"Authorization": "Basic mock:x@y.z"})
    assert r1.status_code == 401
    # Bearer but no token.
    r2 = client.get("/api/v1/auth/session", headers={"Authorization": "Bearer "})
    assert r2.status_code == 401
    # Just the word "Bearer" with nothing else.
    r3 = client.get("/api/v1/auth/session", headers={"Authorization": "Bearer"})
    assert r3.status_code == 401


def test_session_with_invalid_credential_returns_401(client):
    r = client.get("/api/v1/auth/session", headers={"Authorization": "Bearer not-a-mock-token"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "auth.malformed"


def test_dropping_header_signs_out(client):
    """Bearer model: 'sign out' on the server == 'stop sending the token'."""
    headers = _bearer("a3-signout@example.test")
    # Materialize first.
    client.post("/api/v1/auth/session/init", headers=headers)
    r1 = client.get("/api/v1/auth/session", headers=headers)
    assert r1.status_code == 200
    # Same client, no header on the next call -> looks signed-out.
    r2 = client.get("/api/v1/auth/session")
    assert r2.status_code == 401


def test_repeat_signin_for_same_email_reuses_account(client):
    headers = _bearer("a3-repeat@example.test")
    # Idempotent materialization: two POSTs return the same account_id.
    r1 = client.post("/api/v1/auth/session/init", headers=headers)
    id1 = r1.json()["account_id"]
    r2 = client.post("/api/v1/auth/session/init", headers=headers)
    id2 = r2.json()["account_id"]
    assert id1 == id2, "auth_user_id is deterministic from email in mock provider"


def test_callback_endpoint_is_gone(client):
    """ADR 0024 explicitly removed the session-exchange endpoint."""
    r = client.post("/auth/callback", json={"credential": "mock:a3-gone@example.test"})
    assert r.status_code in (404, 405)


def test_signout_endpoint_is_gone(client):
    """ADR 0024 explicitly removed the server-side signout endpoint."""
    r = client.post("/auth/signout")
    assert r.status_code in (404, 405)
