"""Test-suite environment defaults.

The Mynaani runtime container ships with `AUTH_PROVIDER=clerk` so the app
boots ready to verify real Clerk JWTs. The pytest suite, on the other
hand, uses the mock provider exclusively (`Bearer mock:<email>`); the
canonical Clerk JWT flow is covered by integration tests separately.

If a test process inherits `AUTH_PROVIDER=clerk` from the container env,
ClerkAuthProvider tries to RS256-verify a mock token and fails with
`DecodeError('Not enough segments')`. That manifests as every signed-in
test 401'ing, which is a confusing failure mode that has bitten us in
local Docker runs.

We pin the provider to "mock" at collection time so the test suite is
hermetic — independent of whatever the host shell or container env
happens to set. Clerk-specific values are blanked for the same reason
(`get_auth_provider` would otherwise raise if AUTH_PROVIDER=clerk and
CLERK_JWKS_URL=""). Tests that need the Clerk provider should override
these explicitly via monkeypatch.

This conftest also starts an embedded PostgreSQL server via
`embedded-postgres` so the integration suite can run without a local
Docker daemon or system Postgres installation.
"""

from __future__ import annotations

import atexit
import os
import tempfile

# Must run before `backend.core.config.settings` is imported by any test
# module. Pytest evaluates conftest.py first per `testpaths`, so setting
# os.environ here is sufficient — pydantic-settings reads env at Settings()
# instantiation time, which happens lazily inside the app modules.
os.environ.setdefault("AUTH_PROVIDER", "mock")
os.environ["AUTH_PROVIDER"] = "mock"  # override even if container set "clerk"
os.environ.setdefault("CLERK_JWKS_URL", "")
os.environ.setdefault("CLERK_ISSUER", "")
os.environ.setdefault("CLERK_SECRET_KEY", "")

# Suppress secret-age warnings in the test environment.
os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-characters")
os.environ.setdefault("SESSION_SECRET", "test-session-secret-at-least-32-characters")

# ---------------------------------------------------------------------------
# Embedded PostgreSQL for hermetic integration tests
# ---------------------------------------------------------------------------

import embedded_postgres  # noqa: E402

_pgdata = tempfile.mkdtemp(prefix="noni-pg-")
_pg_server = embedded_postgres.get_server(_pgdata, cleanup_mode="stop")
_pg_server.__enter__()
_pg_uri = _pg_server.get_uri()

os.environ.setdefault("DATABASE_URL", _pg_uri)
os.environ["DATABASE_URL"] = _pg_uri
os.environ.setdefault("DATABASE_URL_DIRECT", _pg_uri)
os.environ["DATABASE_URL_DIRECT"] = _pg_uri

# Ensure the embedded server is stopped when the pytest process exits.
atexit.register(_pg_server.cleanup)

# Sprint 27 H4 moved webhook/side-effect work onto a Celery+Redis queue.
# Import Celery *before* create_all so every model module is registered on
# Base.metadata. Tests assert synchronous effects and run without a broker —
# force eager execution so .delay() runs inline (standard Celery pattern).
from backend.tasks.celery_app import app as _celery_app  # noqa: E402

_celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)

# Create the schema from SQLAlchemy metadata so the test database has all
# launch tables without requiring the pgcrypto extension used by the
# production Alembic migration. CITEXT is used by several models, so we
# enable it explicitly before create_all.
from sqlalchemy import text  # noqa: E402
from backend.core.database import Base, engine as _global_engine  # noqa: E402

with _global_engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
    conn.commit()

Base.metadata.create_all(bind=_global_engine)


# =============================================================================
# Enterprise Test Fixtures (ET-1)
# =============================================================================


import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from backend.app.main import app  # noqa: E402
from backend.core.config import settings  # noqa: E402

# Safe test engine — isolated from production
_test_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=0,
    connect_args={"connect_timeout": 5, "options": "-c statement_timeout=10000"},
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Rollback-isolated DB session for direct SQLAlchemy assertions.

    Each test runs inside a transaction that is rolled back on teardown.
    No data leaks between tests or into the real database.
    """
    connection = _test_engine.connect()
    transaction = connection.begin()
    session = _TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Fresh TestClient per test (no shared state)."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return a factory for mock Bearer headers.

    Usage: headers = auth_headers("user@example.com")
    """

    def _make(email: str) -> dict:
        return {"Authorization": f"Bearer mock:{email}"}

    return _make


@pytest.fixture
def authenticated_client(client, auth_headers):
    """TestClient pre-configured with a mock Bearer token.

    The account row is materialized lazily on first request.
    """
    client.headers.update(auth_headers("enterprise-test@example.com"))
    return client
