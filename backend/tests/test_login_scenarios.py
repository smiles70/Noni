"""Login scenario regression tests — anchors the 5 simulations from the
2026-05-24 enterprise audit so an 80-year-old user never gets stuck on a
silent failure.

The 5 scenarios:

  S1  Happy path — first-time signup materialises an account and reaches
      READY in one round-trip pair (/auth/session 404→ /auth/session/init).
  S2  Returning user — pre-existing account row resolves on a single
      /auth/session call; no INSERT.
  S3  Transient backend failure — DB blip during /auth/session must surface
      `auth.transient_db_unavailable` (sticky signed-in on FE, retryable),
      NOT a hard rejection.
  S4  Tampered / expired tokens — three sub-cases (no-credential, malformed
      token, Clerk-side signature failure) all return discriminated 401s
      with a closed-set error code and no information leak.
  S5  Soft-deleted account — terminal. Both /auth/session and
      /auth/session/init must return `auth.account_deleted`; no resurrection
      path via login.

Run hermetically:

    pytest backend/tests/test_login_scenarios.py -v

Run only this file with the project's standard config:

    pytest -k "login_scenarios" -v

Postgres is required (UUID / CITEXT / INET types). The conftest pins
AUTH_PROVIDER=mock so most scenarios use the mock verifier; S4's
Clerk-specific failure modes are covered by monkeypatching
`verify_token` directly in the route module — that gives us deterministic
coverage of the AuthError taxonomy without standing up a JWKS fixture.
"""

from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from backend.api.routes import auth as auth_route_module
from backend.app.main import app
from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.services.auth_verifier import AuthError

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="Login scenario tests require Postgres (UUID/CITEXT types).",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db_session():
    """A direct DB session for arrange/assert outside the FastAPI request."""
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def _bearer(email: str) -> dict:
    """Mock-mode credential. Same surface area as a real Clerk Bearer."""
    return {"Authorization": f"Bearer mock:{email}"}


def _unique_email(slug: str) -> str:
    """Email-per-test so suite reruns don't collide on the unique index."""
    return f"login-scen-{slug}-{uuid.uuid4().hex[:8]}@example.test"


def _envelope_code(response) -> str:
    """Extract the discriminated error code from a 4xx envelope.

    Backend returns either `{"detail": {"error": {"code": ...}}}` (the
    new `auth_error()` helper) or `{"detail": {"envelope_id": ...}}` (the
    legacy /auth/whoami path). Tests under Stage-2+ should only see the
    first shape.
    """
    body = response.json()
    detail = body.get("detail", {})
    if isinstance(detail, dict):
        if "error" in detail and isinstance(detail["error"], dict):
            return detail["error"].get("code", "")
        if "envelope_id" in detail:
            return detail["envelope_id"]
    return ""


# ===========================================================================
# Scenario 1 — Happy path: first-time signup
# ===========================================================================


class TestScenario1HappyPath:
    """S1: a fresh user signs in, gets an account row, reaches READY.

    Backend invariant: /auth/session reports materialized=False on the
    first call, /auth/session/init creates the row, the very next
    /auth/session reports materialized=True with the same account_id.
    """

    def test_first_session_call_reports_unmaterialized(self, client):
        email = _unique_email("s1a")
        r = client.get("/auth/session", headers=_bearer(email))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["materialized"] is False
        assert body["account_id"] is None

    def test_init_creates_row_and_is_idempotent(self, client, db_session):
        email = _unique_email("s1b")
        # First /init: creates.
        r1 = client.post("/auth/session/init", headers=_bearer(email))
        assert r1.status_code == 200, r1.text
        account_id = r1.json()["account_id"]
        assert account_id

        # Row exists in DB.
        row = (
            db_session.query(Account).filter(Account.id == uuid.UUID(account_id)).one()
        )
        assert row.deleted_at is None

        # Second /init: returns the SAME id (idempotent).
        r2 = client.post("/auth/session/init", headers=_bearer(email))
        assert r2.status_code == 200
        assert r2.json()["account_id"] == account_id

    def test_full_handshake_session_then_init_then_session(self, client):
        email = _unique_email("s1c")
        r1 = client.get("/auth/session", headers=_bearer(email))
        assert r1.json()["materialized"] is False

        r2 = client.post("/auth/session/init", headers=_bearer(email))
        assert r2.status_code == 200
        account_id = r2.json()["account_id"]

        r3 = client.get("/auth/session", headers=_bearer(email))
        assert r3.status_code == 200
        body = r3.json()
        assert body["materialized"] is True
        assert body["account_id"] == account_id


# ===========================================================================
# Scenario 2 — Returning user: existing row, single round-trip
# ===========================================================================


class TestScenario2ReturningUser:
    """S2: a user signed in yesterday opens a new tab today.

    Backend invariant: /auth/session reaches materialized=True on the
    first call and DOES NOT INSERT. We assert no new row is created by
    counting before/after.
    """

    def test_session_reports_materialized_without_writing(self, client, db_session):
        email = _unique_email("s2")
        # Arrange: simulate "yesterday's signup".
        client.post("/auth/session/init", headers=_bearer(email))

        before = db_session.query(Account).count()
        r = client.get("/auth/session", headers=_bearer(email))
        after = db_session.query(Account).count()

        assert r.status_code == 200
        assert r.json()["materialized"] is True
        assert before == after, "GET /auth/session must never INSERT (B4)"


# ===========================================================================
# Scenario 3 — Transient backend failure must NOT evict the user
# ===========================================================================


class TestScenario3TransientFailure:
    """S3: DB hiccup during /auth/session.

    Backend invariant: surface `auth.transient_db_unavailable` (B5/I-A).
    Frontend invariant (verified manually): state goes TRANSIENT_ERROR,
    NOT REJECTED — user stays signed in, reload retries.
    """

    def test_db_failure_returns_transient_code(self, client, monkeypatch):
        email = _unique_email("s3")
        # Make the SELECT inside /auth/session blow up. The handler
        # wraps the query in try/except Exception → auth.transient_db_unavailable.
        original = auth_route_module.Account

        class _ExplodingQuery:
            def filter(self, *a, **kw):
                raise RuntimeError("simulated DB outage")

        class _ExplodingAccount:
            # Only the .query path matters; the handler does
            # db.query(Account).filter(...).one_or_none()
            pass

        # Patch the symbol used inside the route module so db.query(Account)
        # is fed our exploding replacement. The cleanest hook is to patch
        # the bound name directly.
        def _exploding_query(model):
            if model is original:
                return _ExplodingQuery()
            raise AssertionError("unexpected query target in test")

        # We can't easily intercept the SQLAlchemy session method without
        # a deeper fixture. Instead, monkeypatch verify_token to succeed
        # but make the query raise via a lambda on the route's db
        # reference. The simplest hermetic path: monkeypatch verify_token
        # to raise the transient code itself, which is what the handler
        # would have produced if the SELECT failed.
        from backend.services.auth_verifier import AuthClaims

        def _fake_verify(_token):
            # Pretend the verifier succeeded; force the transient via a
            # second monkeypatch on the DB call below.
            return AuthClaims(
                auth_user_id=uuid.uuid5(uuid.NAMESPACE_URL, email),
                email=email,
                display_name=None,
                subject=email,
            )

        # Replace verify_token in the route's namespace.
        monkeypatch.setattr(auth_route_module, "verify_token", _fake_verify)

        # Replace the route's Account.query path: monkeypatch the Session
        # instance that the dependency yields. We do this by overriding
        # the `get_db` dependency via FastAPI's dependency_overrides.
        from backend.api.deps import get_db as get_db_dep

        class _ExplodingSession:
            def query(self, _model):
                raise RuntimeError("simulated DB outage")

            def close(self):
                pass

        def _override_get_db():
            yield _ExplodingSession()

        app.dependency_overrides[get_db_dep] = _override_get_db
        # Also need to override the canonical core.database.get_db that
        # routes/auth.py imports.
        from backend.core.database import get_db as core_get_db

        app.dependency_overrides[core_get_db] = _override_get_db

        try:
            r = client.get("/auth/session", headers=_bearer(email))
        finally:
            app.dependency_overrides.pop(get_db_dep, None)
            app.dependency_overrides.pop(core_get_db, None)

        assert r.status_code == 401, r.text
        assert _envelope_code(r) == "auth.transient_db_unavailable"


# ===========================================================================
# Scenario 4 — Tampered / expired tokens (closed-set codes only)
# ===========================================================================


class TestScenario4TamperedTokens:
    """S4: every illegitimate token returns a discriminated 401 with a
    closed-set code. No raw stack traces, no information leak about
    which specific check failed beyond the error code itself.
    """

    def test_no_authorization_header_returns_no_credential(self, client):
        r = client.get("/auth/session")
        assert r.status_code == 401
        assert _envelope_code(r) == "auth.no_credential"

    def test_malformed_bearer_returns_no_credential(self, client):
        # `Bearer ` with no token → parse_bearer returns None → no_credential
        r = client.get("/auth/session", headers={"Authorization": "Bearer "})
        assert r.status_code == 401
        assert _envelope_code(r) == "auth.no_credential"

    def test_wrong_scheme_returns_no_credential(self, client):
        r = client.get("/auth/session", headers={"Authorization": "Basic mock:a@b.c"})
        assert r.status_code == 401
        assert _envelope_code(r) == "auth.no_credential"

    def test_mock_token_without_email_returns_malformed(self, client):
        # `mock:` without an email body → MockAuthProvider rejects → malformed
        r = client.get("/auth/session", headers={"Authorization": "Bearer mock:"})
        assert r.status_code == 401
        assert _envelope_code(r) == "auth.malformed"

    def test_clerk_expired_token_maps_to_auth_expired(self, client, monkeypatch):
        """Simulate Clerk-mode ExpiredSignatureError → auth.expired."""

        def _fake_verify(_token):
            raise AuthError("auth.expired", "auth.expired")

        monkeypatch.setattr(auth_route_module, "verify_token", _fake_verify)
        r = client.get(
            "/auth/session",
            headers={"Authorization": "Bearer eyJfake.fake.fake"},
        )
        assert r.status_code == 401
        assert _envelope_code(r) == "auth.expired"

    def test_clerk_forged_signature_maps_to_signature_invalid(
        self, client, monkeypatch
    ):
        def _fake_verify(_token):
            raise AuthError("auth.signature_invalid", "auth.signature_invalid")

        monkeypatch.setattr(auth_route_module, "verify_token", _fake_verify)
        r = client.get(
            "/auth/session",
            headers={"Authorization": "Bearer eyJforged.payload.sig"},
        )
        assert r.status_code == 401
        assert _envelope_code(r) == "auth.signature_invalid"

    def test_no_stack_trace_in_error_body(self, client):
        """Defence-in-depth: no Python tracebacks should leak in 401s."""
        r = client.get("/auth/session")
        body_text = r.text.lower()
        for forbidden in ("traceback", 'file "/', '.py", line '):
            assert (
                forbidden not in body_text
            ), f"401 body leaked debug content: {forbidden!r}"


# ===========================================================================
# Scenario 5 — Soft-deleted account is terminal
# ===========================================================================


class TestScenario5SoftDeletedTerminal:
    """S5: once an account is soft-deleted, neither /auth/session nor
    /auth/session/init may resurrect it. Both must return
    `auth.account_deleted`. GDPR Art. 17 + B7/I-E invariant.
    """

    @pytest.fixture()
    def deleted_account_email(self, client, db_session):
        email = _unique_email("s5")
        # Arrange: create then soft-delete the account.
        r = client.post("/auth/session/init", headers=_bearer(email))
        account_id = r.json()["account_id"]
        row = (
            db_session.query(Account).filter(Account.id == uuid.UUID(account_id)).one()
        )
        row.deleted_at = datetime.now(timezone.utc)
        db_session.commit()
        return email

    def test_session_get_rejects_with_account_deleted(
        self, client, deleted_account_email
    ):
        r = client.get("/auth/session", headers=_bearer(deleted_account_email))
        assert r.status_code == 401, r.text
        assert _envelope_code(r) == "auth.account_deleted"

    def test_session_init_rejects_with_account_deleted(
        self, client, deleted_account_email
    ):
        """The bypass path: attacker hits /init directly, expecting it
        to recreate the row. Must NOT happen."""
        r = client.post("/auth/session/init", headers=_bearer(deleted_account_email))
        assert r.status_code == 401, r.text
        assert _envelope_code(r) == "auth.account_deleted"


# ===========================================================================
# UX timing budget — "no 80-year-old should ever be left staring at a spinner"
# ===========================================================================


class TestUxTimingBudget:
    """All hot-path auth endpoints must respond within an 80-year-old's
    patience window. NN/g recommends < 1s feedback for any UI action;
    Krug's "Don't Make Me Think" says 0.4s for routine actions. We pick
    1.0s as the hard ceiling for the in-process TestClient (no network).
    """

    HARD_CEILING_SECONDS = 1.0

    def _time(self, fn):
        t0 = time.perf_counter()
        r = fn()
        return r, time.perf_counter() - t0

    def test_auth_config_under_budget(self, client):
        r, dt = self._time(lambda: client.get("/auth/config"))
        assert r.status_code == 200
        assert dt < self.HARD_CEILING_SECONDS, f"/auth/config took {dt:.3f}s"

    def test_auth_session_unmaterialized_under_budget(self, client):
        email = _unique_email("ux1")
        r, dt = self._time(lambda: client.get("/auth/session", headers=_bearer(email)))
        assert r.status_code == 200
        assert dt < self.HARD_CEILING_SECONDS, f"/auth/session took {dt:.3f}s"

    def test_auth_session_init_under_budget(self, client):
        email = _unique_email("ux2")
        r, dt = self._time(
            lambda: client.post("/auth/session/init", headers=_bearer(email))
        )
        assert r.status_code == 200
        assert dt < self.HARD_CEILING_SECONDS, f"/auth/session/init took {dt:.3f}s"
