"""Sprint A6 — telemetry retention policy + GDPR account deletion."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.core.config import settings
from backend.models.accounts import Account
from backend.models.auth import Session as SessionRow
from backend.services.deletion import (
    cancel_deletion,
    execute_deletion,
    request_deletion,
)
from backend.services.telemetry_retention import (
    DEFAULT_RETENTION_DAYS,
    RETENTION_DAYS,
    expires_at_for,
)

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A6 tests require Postgres.",
)


@pytest.fixture(scope="module")
def DbSession():  # noqa: N802
    engine = create_engine(settings.DATABASE_URL, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    return TestClient(app)


# ---------- retention policy ----------


def test_default_retention_for_unknown_event():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    expected = now + timedelta(days=DEFAULT_RETENTION_DAYS)
    assert expires_at_for("never_heard_of_this", now=now) == expected


def test_known_event_uses_table():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    got = expires_at_for("iscs_decision", now=now)
    expected_days = RETENTION_DAYS["iscs_decision"]
    assert (got - now).days == expected_days


def test_prefix_match_purchases():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    got = expires_at_for("purchase_completed", now=now)
    assert (got - now).days == RETENTION_DAYS["purchase_"]


# ---------- deletion flow ----------


def _make_account(db, email: str) -> Account:
    # deletion_requests is intentionally not ON DELETE CASCADE (audit
    # retention per ADR 0023). Clean dependents first so test reruns
    # don't trip the FK constraint.
    db.execute(
        text(
            "DELETE FROM deletion_requests "
            "WHERE account_id IN (SELECT id FROM accounts WHERE email = :e)"
        ),
        {"e": email},
    )
    db.execute(text("DELETE FROM accounts WHERE email = :e"), {"e": email})
    db.commit()
    a = Account(id=uuid.uuid4(), email=email)
    db.add(a)
    db.commit()
    return a


def test_request_deletion_marks_account_and_revokes_sessions(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a6-request@example.test")
        # Active session
        db.add(
            SessionRow(
                account_id=account.id,
                session_token_hash="a6-session-hash-1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        db.commit()
        req = request_deletion(db, account)
        db.commit()
        assert req.status == "requested"
        db.refresh(account)
        assert account.deleted_at is not None
        active = (
            db.query(SessionRow)
            .filter(
                SessionRow.account_id == account.id, SessionRow.revoked_at.is_(None)
            )
            .count()
        )
        assert active == 0


def test_request_deletion_is_idempotent(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a6-idempotent@example.test")
        req1 = request_deletion(db, account)
        db.commit()
        req2 = request_deletion(db, account)
        db.commit()
        assert req1.id == req2.id


def test_cancel_deletion_within_grace_restores_account(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a6-cancel@example.test")
        request_deletion(db, account)
        db.commit()
        cancelled = cancel_deletion(db, account)
        db.commit()
        assert cancelled is not None
        assert cancelled.status == "cancelled"
        db.refresh(account)
        assert account.deleted_at is None


def test_execute_deletion_zeroes_pii(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a6-execute@example.test")
        account.display_name = "Real Name"
        account.auth_user_id = uuid.uuid4()
        db.commit()
        request_deletion(db, account)
        db.commit()
        done = execute_deletion(db, account)
        db.commit()
        assert done is not None
        assert done.status == "completed"
        db.refresh(account)
        assert "Real Name" != account.display_name
        assert account.display_name is None
        assert account.auth_user_id is None
        assert "deleted+" in account.email


# ---------- HTTP endpoint smoke ----------


def test_me_delete_requires_session(client):
    r = client.post("/me/delete")
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_me_delete_after_signin_returns_pending(client):
    """ADR 0024 Bearer flow: deletion request returns 202 with the
    scheduled timestamp. There is no cookie to clear server-side; the
    frontend calls clerk.signOut() / clears its mock token after a
    successful 202 (covered in the frontend tests)."""
    client.headers["Authorization"] = "Bearer mock:a6-http@example.test"
    r = client.post("/me/delete")
    assert r.status_code == 202
    body = r.json()
    assert body["status"] == "requested"
    assert "scheduled_for" in body
    # No Set-Cookie header on the response.
    assert settings.SESSION_COOKIE_NAME not in r.cookies
