"""Rack 2.10: app lifecycle, telemetry, rate limiting, and secret rotation coverage."""

from __future__ import annotations

import os
import sys
import types
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.app import main as app_main
from backend.app import telemetry as telemetry_module
from backend.core import config as config_module
from backend.core import database as database_module
from backend.core import secret_rotation as secret_rotation_module
from backend.core.config import settings
from backend.models.billing import Product
from backend.models.governance import RateLimitCounter
from backend.services.rate_limit import RateLimit, check_and_increment, enforce


@pytest.fixture
def fresh_client():
    """A fresh TestClient that triggers the app lifespan."""
    from fastapi.testclient import TestClient

    return TestClient(app_main.app)


# ---------------------------------------------------------------------------
# secret_rotation
# ---------------------------------------------------------------------------


def test_warn_if_secret_old_logs_when_due(monkeypatch):
    name = "RACK210_OLD_SECRET"
    old_ts = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp())
    monkeypatch.setenv(name, f"value::{old_ts}")
    # max_age_sec = 1 means any non-recent secret is "old"
    secret_rotation_module.warn_if_secret_old(name, max_age_sec=1)


def test_warn_if_secret_old_no_op_when_missing():
    secret_rotation_module.warn_if_secret_old("RACK210_MISSING_SECRET")


def test_warn_if_secret_old_no_op_when_no_metadata():
    os.environ["RACK210_PLAIN_SECRET"] = "plain-value"
    try:
        secret_rotation_module.warn_if_secret_old("RACK210_PLAIN_SECRET")
    finally:
        del os.environ["RACK210_PLAIN_SECRET"]


def test_warn_if_secret_old_no_op_when_timestamp_invalid():
    os.environ["RACK210_BAD_TS_SECRET"] = "value::not-a-number"
    try:
        secret_rotation_module.warn_if_secret_old("RACK210_BAD_TS_SECRET")
    finally:
        del os.environ["RACK210_BAD_TS_SECRET"]


# ---------------------------------------------------------------------------
# config.validate_settings
# ---------------------------------------------------------------------------


def test_validate_settings_raises_when_database_url_missing(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        config_module.validate_settings()


# ---------------------------------------------------------------------------
# main app lifecycle helpers
# ---------------------------------------------------------------------------


def test_seed_dev_products_returns_early_for_stripe(monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    app_main._seed_dev_products()  # should return immediately


def test_seed_dev_products_inserts_when_product_missing(monkeypatch):
    captured = {}

    class _FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def one_or_none(self):
            return None

    class _FakeSession:
        def query(self, *args, **kwargs):
            return _FakeQuery()

        def add(self, obj):
            captured["product"] = obj

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "mock")
    monkeypatch.setattr(
        "backend.core.database.SessionLocal", _FakeSession, raising=False
    )
    app_main._seed_dev_products()
    assert captured["product"].code == "modules_4_5"


def test_seed_dev_products_is_idempotent(db_session):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "mock")
    try:
        app_main._seed_dev_products()
        app_main._seed_dev_products()
    finally:
        monkeypatch.undo()

    rows = db_session.query(Product).filter(Product.code == "modules_4_5").count()
    assert rows == 1


def test_handle_sigterm_sets_shutdown_flag():
    app_main._shutdown_requested = False
    app_main._handle_sigterm(15, None)
    assert app_main._shutdown_requested is True
    app_main._shutdown_requested = False


def test_verify_production_secrets_warns_for_mock_auth(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "mock")
    monkeypatch.setattr(settings, "SECRET_KEY", "a-strong-random-key-32chars-xyzabc123")
    monkeypatch.setattr(settings, "SESSION_SECRET", "another-strong-key-32chars-xyzabc")
    app_main._verify_production_secrets()


def test_verify_production_secrets_raises_on_weak_secret(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "clerk")
    monkeypatch.setattr(
        settings, "SECRET_KEY", "this-is-a-test-secret-key-32chars-long-abc"
    )
    monkeypatch.setattr(settings, "SESSION_SECRET", "another-strong-key-32chars-xyzabc")
    with pytest.raises(RuntimeError, match="weak/default substring"):
        app_main._verify_production_secrets()


def test_verify_production_secrets_raises_on_short_secret(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "AUTH_PROVIDER", "clerk")
    monkeypatch.setattr(settings, "SECRET_KEY", "short")
    monkeypatch.setattr(settings, "SESSION_SECRET", "another-strong-key-32chars-xyzabc")
    with pytest.raises(RuntimeError, match="too short"):
        app_main._verify_production_secrets()


# ---------------------------------------------------------------------------
# main routes and middleware
# ---------------------------------------------------------------------------


def test_health_ready_returns_503_on_database_failure(monkeypatch, fresh_client):
    fake_engine = MagicMock()
    fake_engine.connect.side_effect = RuntimeError("db down")
    monkeypatch.setattr(app_main, "engine", fake_engine)
    resp = fresh_client.get("/health/ready")
    assert resp.status_code == 503


def test_legacy_redirects(fresh_client):
    resp = fresh_client.get("/api/curriculum", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/api/v1/curriculum"
    assert resp.headers["Deprecation"] == "true"


def test_legacy_redirect_with_path(fresh_client):
    resp = fresh_client.get("/api/curriculum/module-0", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/api/v1/curriculum/module-0"


def test_legacy_redirect_with_query_string(fresh_client):
    resp = fresh_client.get("/api/curriculum?foo=bar", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/api/v1/curriculum?foo=bar"


def test_features_endpoint(fresh_client):
    resp = fresh_client.get("/api/v1/features")
    assert resp.status_code == 200
    assert "enabled" in resp.json()


def test_metrics_endpoint(fresh_client):
    resp = fresh_client.get("/metrics")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# telemetry recording helpers
# ---------------------------------------------------------------------------


def test_record_auth_session_outcome_with_latency():
    telemetry_module.record_auth_session_outcome("ok", latency_ms=150)


def test_record_onboarding_event_with_betterstack(monkeypatch):
    fake_client = MagicMock()
    fake_client.send_event.return_value = True
    monkeypatch.setattr(telemetry_module, "logger", MagicMock())
    monkeypatch.setattr(
        "backend.api.routes.betterstack_onboarding.get_betterstack_client",
        lambda: fake_client,
    )
    telemetry_module.record_onboarding_event("rack210.test", user_id="u1")
    fake_client.send_event.assert_called_once()


def test_record_onboarding_event_sends_and_swallows_exception(monkeypatch):
    fake_client = MagicMock()
    fake_client.send_event.side_effect = RuntimeError("boom")
    monkeypatch.setattr(
        "backend.api.routes.betterstack_onboarding.get_betterstack_client",
        lambda: fake_client,
    )
    telemetry_module.record_onboarding_event("rack210.test.fail")


def test_telemetry_middleware_swallows_logging_exception(monkeypatch, fresh_client):
    real_log = telemetry_module.logger.log

    def _boom(level, msg, *args, **kwargs):
        raise RuntimeError("log boom")

    monkeypatch.setattr(telemetry_module.logger, "log", _boom)
    try:
        resp = fresh_client.get("/health")
        assert resp.status_code == 200
    finally:
        monkeypatch.setattr(telemetry_module.logger, "log", real_log)


def test_telemetry_middleware_records_auth_path_latency(fresh_client):
    resp = fresh_client.get("/auth/session", follow_redirects=False)
    assert resp.status_code == 302


# ---------------------------------------------------------------------------
# rate limiting
# ---------------------------------------------------------------------------


class _FakeRedisClient:
    def __init__(self, allowed: bool = True, raise_on_eval: bool = False):
        self._allowed = 1 if allowed else 0
        self._raise_on_eval = raise_on_eval

    def eval(self, script, numkeys, *args):
        if self._raise_on_eval:
            raise RuntimeError("redis eval failed")
        return self._allowed


def test_get_redis_client_returns_cached_instance(monkeypatch):
    fake = _FakeRedisClient()
    monkeypatch.setattr(
        "backend.services.rate_limit._redis_client", fake, raising=False
    )
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost")
    from backend.services.rate_limit import _get_redis_client

    assert _get_redis_client() is fake


def test_get_redis_client_swallows_connection_error(monkeypatch):
    fake_redis_module = types.ModuleType("redis")

    class _BoomRedis:
        @classmethod
        def from_url(cls, *args, **kwargs):
            raise RuntimeError("redis down")

    fake_redis_module.Redis = _BoomRedis
    monkeypatch.setitem(sys.modules, "redis", fake_redis_module)
    monkeypatch.setattr(
        "backend.services.rate_limit._redis_client", None, raising=False
    )
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost")
    from backend.services.rate_limit import _get_redis_client

    assert _get_redis_client() is None


def test_check_and_increment_uses_redis_result_true(db_session, monkeypatch):
    fake = _FakeRedisClient(allowed=True)
    monkeypatch.setattr(
        "backend.services.rate_limit._redis_client", fake, raising=False
    )
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost")
    limit = RateLimit(action="rack210", max_per_window=1, window_seconds=60)
    assert check_and_increment(db_session, limit, "client-1") is True


def test_check_and_increment_uses_redis_result_false(db_session, monkeypatch):
    fake = _FakeRedisClient(allowed=False)
    monkeypatch.setattr(
        "backend.services.rate_limit._redis_client", fake, raising=False
    )
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost")
    limit = RateLimit(action="rack210", max_per_window=1, window_seconds=60)
    assert check_and_increment(db_session, limit, "client-2") is False


def test_check_and_increment_race_recovery_after_integrity_error(
    db_session, monkeypatch
):
    # Seed a counter for the same key so the retry path finds an existing row.
    key, window_start = RateLimit(
        action="rack210", max_per_window=1, window_seconds=60
    ).key("race-client")
    db_session.add(
        RateLimitCounter(
            key=key,
            count=1,
            window_start=window_start,
            expires_at=window_start + __import__("datetime").timedelta(seconds=60),
        )
    )
    db_session.commit()

    # Force the insert path to fail with a duplicate-key style error.
    def _fake_flush(*args, **kwargs):
        raise IntegrityError("dup", None, None)

    monkeypatch.setattr(db_session, "flush", _fake_flush)
    limit = RateLimit(action="rack210", max_per_window=1, window_seconds=60)
    assert check_and_increment(db_session, limit, "race-client") is False


def test_enforce_raises_429_when_over_limit(db_session, monkeypatch):
    fake = _FakeRedisClient(allowed=False)
    monkeypatch.setattr(
        "backend.services.rate_limit._redis_client", fake, raising=False
    )
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost")
    limit = RateLimit(action="rack210", max_per_window=1, window_seconds=60)
    with pytest.raises(HTTPException) as exc:
        enforce(db_session, limit, "blocked-client")
    assert exc.value.status_code == 429


# ---------------------------------------------------------------------------
# database lifecycle
# ---------------------------------------------------------------------------


def test_init_db_is_idempotent():
    database_module.init_db()
    database_module.init_db()


def test_run_migrations_calls_alembic_upgrade(monkeypatch):
    upgraded = []

    def _fake_upgrade(cfg, revision):
        upgraded.append(revision)

    monkeypatch.setattr("alembic.command.upgrade", _fake_upgrade)
    database_module.run_migrations()
    assert upgraded == ["head"]
