"""Sprint A7 — application-level rate limiter (defense-in-depth)."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings
from backend.services.rate_limit import (
    RateLimit,
    _check_redis_token_bucket,
    check_and_increment,
)

pytestmark = pytest.mark.skipif(
    "sqlite" in (os.environ.get("DATABASE_URL") or settings.DATABASE_URL),
    reason="A7 tests require Postgres.",
)


@pytest.fixture(scope="module")
def DbSession():  # noqa: N802
    engine = create_engine(settings.DATABASE_URL, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _clear_counters(DbSession):
    with DbSession() as db:
        db.execute(text("DELETE FROM rate_limit_counters"))
        db.commit()
    yield


def test_allows_up_to_max(DbSession):
    limit = RateLimit(action="t_allow", max_per_window=3, window_seconds=60)
    with DbSession() as db:
        for _ in range(3):
            assert check_and_increment(db, limit, "ident-A") is True
        db.commit()


def test_blocks_over_max(DbSession):
    limit = RateLimit(action="t_block", max_per_window=2, window_seconds=60)
    with DbSession() as db:
        assert check_and_increment(db, limit, "ident-B") is True
        assert check_and_increment(db, limit, "ident-B") is True
        assert check_and_increment(db, limit, "ident-B") is False
        db.commit()


def test_isolation_by_identifier(DbSession):
    limit = RateLimit(action="t_isolate", max_per_window=1, window_seconds=60)
    with DbSession() as db:
        assert check_and_increment(db, limit, "ident-C") is True
        assert check_and_increment(db, limit, "ident-D") is True
        assert check_and_increment(db, limit, "ident-C") is False
        assert check_and_increment(db, limit, "ident-D") is False
        db.commit()


def test_isolation_by_action(DbSession):
    a = RateLimit(action="t_act_a", max_per_window=1, window_seconds=60)
    b = RateLimit(action="t_act_b", max_per_window=1, window_seconds=60)
    with DbSession() as db:
        assert check_and_increment(db, a, "ident-E") is True
        assert check_and_increment(db, b, "ident-E") is True
        assert check_and_increment(db, a, "ident-E") is False
        assert check_and_increment(db, b, "ident-E") is False
        db.commit()


def test_redis_token_bucket_blocks_after_capacity(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.remaining = 2

        def eval(self, *args):
            if self.remaining <= 0:
                return 0
            self.remaining -= 1
            return 1

    fake = FakeRedis()
    monkeypatch.setattr("backend.services.rate_limit._get_redis_client", lambda: fake)
    limit = RateLimit(action="t_redis", max_per_window=2, window_seconds=60)

    assert _check_redis_token_bucket(limit, "ident-R") is True
    assert _check_redis_token_bucket(limit, "ident-R") is True
    assert _check_redis_token_bucket(limit, "ident-R") is False
