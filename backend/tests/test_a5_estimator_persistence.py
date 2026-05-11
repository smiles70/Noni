"""Sprint A5 — estimator state persistence per (account, scope).

Closes the architect-review P0 in ADR 0024.
"""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings
from backend.models.accounts import Account
from backend.services.estimator_state import (
    DEFAULT_SCOPE,
    get_last_stability,
    load_state,
    save_state,
)

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A5 persistence tests require Postgres.",
)


@pytest.fixture(scope="module")
def DbSession():  # noqa: N802
    engine = create_engine(settings.DATABASE_URL, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _make_account(db, email: str) -> Account:
    db.execute(text("DELETE FROM accounts WHERE email = :e"), {"e": email})
    db.commit()
    a = Account(id=uuid.uuid4(), email=email)
    db.add(a)
    db.commit()
    return a


def test_load_returns_none_when_absent(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a5-absent@example.test")
        assert load_state(db, account.id) is None


def test_save_then_load_round_trip(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a5-roundtrip@example.test")
        account_id = account.id
        state = {"covariance": [[1.0, 0.0], [0.0, 1.0]], "last_obs": 0.42}
        save_state(db, account_id, state, last_stability=0.7234)
        db.commit()

    with DbSession() as db2:
        loaded = load_state(db2, account_id)
        assert loaded == state
        assert get_last_stability(db2, account_id) == pytest.approx(0.7234, rel=1e-3)


def test_save_then_save_updates_in_place(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a5-update@example.test")
        account_id = account.id
        save_state(db, account_id, {"v": 1}, last_stability=0.5)
        save_state(db, account_id, {"v": 2}, last_stability=0.6)
        db.commit()

    with DbSession() as db2:
        assert load_state(db2, account_id) == {"v": 2}
        assert get_last_stability(db2, account_id) == pytest.approx(0.6, rel=1e-3)


def test_scope_isolates_state(DbSession):
    with DbSession() as db:
        account = _make_account(db, "a5-scope@example.test")
        account_id = account.id
        save_state(db, account_id, {"s": "global"}, scope=DEFAULT_SCOPE)
        save_state(db, account_id, {"s": "unit_x"}, scope="unit_x")
        db.commit()

    with DbSession() as db2:
        assert load_state(db2, account_id, scope=DEFAULT_SCOPE) == {"s": "global"}
        assert load_state(db2, account_id, scope="unit_x") == {"s": "unit_x"}
