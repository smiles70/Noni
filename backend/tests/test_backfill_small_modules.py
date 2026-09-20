"""Backfill tests for small, uncovered backend modules.

Rack 1.5/2.1 of TEST-MATURITY-004: raises source coverage by exercising
previously un-tested helpers and edge modules without changing product
behavior.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import uuid
from unittest.mock import patch

import httpx
import pytest

from backend.api.routes.betterstack_onboarding import (
    BetterStackOnboardingClient,
    get_betterstack_client,
)
from backend.api.routes.onboarding_telemetry import track_onboarding_event
from backend.content.curriculum_loader import CurriculumLoader
from backend.core.claude_engine.claude_client import request_claude
from backend.core.config import settings
from backend.core.diagnostic_engine.graph_analyzer import analyze_graph
from backend.core.nlu_engine.interpreter import interpret_text
from backend.core.projects.projects import PROJECTS
from backend.core.security import (
    generate_session_token,
    verify_session_cookie,
)
from backend.models.accounts import Account
from backend.models.agent import GraphEdge, GraphNode, ProgramGraph
from backend.models.auth import Session as SessionRow
from backend.services.account_materializer import materialize
from backend.services.auth_provider import AuthClaims
from backend.services.auth_verifier import AuthError
from backend.services.sessions import (
    _coerce_ip,
    create_session,
    find_or_create_account_for_claims,
    lookup_session,
    revoke_session,
)
from backend.tasks.telemetry_tasks import record_telemetry_event

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_betterstack_singleton():
    """Each test starts with a fresh BetterStack client singleton."""
    import backend.api.routes.betterstack_onboarding as bso

    bso._betterstack_client = None
    yield
    bso._betterstack_client = None


# ---------------------------------------------------------------------------
# backend/core/security.py
# ---------------------------------------------------------------------------


def test_generate_session_token_roundtrip():
    raw, cookie, token_hash = generate_session_token()
    assert raw in cookie
    assert "." in cookie
    assert token_hash == hashlib.sha256(raw.encode("ascii")).hexdigest()
    assert verify_session_cookie(cookie) == token_hash


def test_verify_session_cookie_fails_closed():
    assert verify_session_cookie("") is None
    assert verify_session_cookie("no-dot") is None
    assert verify_session_cookie("raw.") is None
    assert verify_session_cookie(".sig") is None
    assert verify_session_cookie("raw.wrong_sig") is None


# ---------------------------------------------------------------------------
# backend/services/sessions.py
# ---------------------------------------------------------------------------


def test_coerce_ip_valid_and_invalid():
    assert _coerce_ip("127.0.0.1") == "127.0.0.1"
    assert _coerce_ip("::1") == "::1"
    assert _coerce_ip("testclient") is None
    assert _coerce_ip("") is None
    assert _coerce_ip(None) is None


def test_find_or_create_account_for_claims(db_session):
    claims = AuthClaims(
        auth_user_id=uuid.uuid5(uuid.NAMESPACE_DNS, "sessions@example.test"),
        email="sessions@example.test",
        display_name="Session Tester",
        subject="sessions@example.test",
    )
    account = find_or_create_account_for_claims(db_session, claims)
    assert account.email == "sessions@example.test"

    # Idempotent: same auth_user_id updates email/display_name.
    claims2 = AuthClaims(
        auth_user_id=claims.auth_user_id,
        email="sessions2@example.test",
        display_name="Updated",
        subject="sessions@example.test",
    )
    account2 = find_or_create_account_for_claims(db_session, claims2)
    assert account2.id == account.id
    assert account2.email == "sessions2@example.test"
    assert account2.display_name == "Updated"


def test_create_and_lookup_session(db_session):
    claims = AuthClaims(
        auth_user_id=uuid.uuid5(uuid.NAMESPACE_DNS, "session-lookup@example.test"),
        email="session-lookup@example.test",
    )
    account = find_or_create_account_for_claims(db_session, claims)
    row, cookie = create_session(
        db_session,
        account,
        last_ip="127.0.0.1",
        last_user_agent="pytest",
    )
    assert isinstance(row, SessionRow)
    assert row.last_ip == "127.0.0.1"

    found = lookup_session(db_session, cookie)
    assert found is not None
    assert found.id == row.id


def test_lookup_session_fails_closed(db_session):
    assert lookup_session(db_session, "") is None
    assert lookup_session(db_session, "not.a.cookie") is None

    claims = AuthClaims(
        auth_user_id=uuid.uuid5(uuid.NAMESPACE_DNS, "revoked@example.test"),
        email="revoked@example.test",
    )
    account = find_or_create_account_for_claims(db_session, claims)
    row, cookie = create_session(db_session, account, ttl_days=-1)
    assert lookup_session(db_session, cookie) is None  # expired

    row2, cookie2 = create_session(db_session, account)
    revoke_session(db_session, row2, reason="test_revoke")
    assert lookup_session(db_session, cookie2) is None  # revoked


# ---------------------------------------------------------------------------
# backend/services/account_materializer.py
# ---------------------------------------------------------------------------


def _claims(email: str, seed: str) -> AuthClaims:
    return AuthClaims(
        auth_user_id=uuid.uuid5(uuid.NAMESPACE_DNS, seed),
        email=email,
        display_name="Materializer",
    )


def test_materialize_creates_account(db_session):
    claims = _claims("mat@example.test", "mat@example.test")
    account = materialize(db_session, claims)
    assert account.auth_user_id == claims.auth_user_id
    assert account.email == claims.email


def test_materialize_idempotent(db_session):
    claims = _claims("mat-idem@example.test", "mat-idem@example.test")
    a1 = materialize(db_session, claims)
    a2 = materialize(db_session, claims)
    assert a1.id == a2.id


def test_materialize_email_collision(db_session):
    email = "collision@example.test"
    auth1 = uuid.uuid5(uuid.NAMESPACE_DNS, "coll-1@example.test")
    auth2 = uuid.uuid5(uuid.NAMESPACE_DNS, "coll-2@example.test")
    materialize(db_session, AuthClaims(auth_user_id=auth1, email=email))
    materialize(db_session, AuthClaims(auth_user_id=auth2, email=email))

    account = db_session.query(Account).filter(Account.auth_user_id == auth2).one()
    assert account.email == email


def test_materialize_deleted_account_blocked(db_session):
    claims = _claims("deleted@example.test", "deleted@example.test")
    account = materialize(db_session, claims)
    account.deleted_at = dt.datetime.now(dt.timezone.utc)
    db_session.flush()

    with pytest.raises(AuthError):
        materialize(db_session, claims)


# ---------------------------------------------------------------------------
# backend/content/curriculum_loader.py
# ---------------------------------------------------------------------------


def test_curriculum_loader_returns_none_without_files():
    assert CurriculumLoader.get_unit(1, "anything") is None
    assert CurriculumLoader.list_units(1) == []
    assert CurriculumLoader.get_standalone_pages("what-is-ai") is None


def test_curriculum_loader_reads_json(tmp_path, monkeypatch):
    import backend.content.curriculum_loader as cl

    monkeypatch.setattr(cl, "_CONTENT_DIR", tmp_path)
    module_file = tmp_path / "module_1.json"
    module_file.write_text(
        json.dumps(
            {
                "units": [
                    {"unit_id": "u1", "title": "Unit One"},
                    {"unit_id": "u2", "title": "Unit Two"},
                ]
            }
        )
    )
    standalone_file = tmp_path / "standalone.json"
    standalone_file.write_text(
        json.dumps({"what-is-ai": [{"page_id": "p1", "title": "AI"}]})
    )

    assert CurriculumLoader.list_units(1) == [
        {"unit_id": "u1", "title": "Unit One"},
        {"unit_id": "u2", "title": "Unit Two"},
    ]
    assert CurriculumLoader.get_unit(1, "u2") == {
        "unit_id": "u2",
        "title": "Unit Two",
    }
    assert CurriculumLoader.get_standalone_pages("what-is-ai") == [
        {"page_id": "p1", "title": "AI"}
    ]


# ---------------------------------------------------------------------------
# Tiny diagnostic / content / NLU modules
# ---------------------------------------------------------------------------


def test_request_claude_returns_confirmation():
    result = request_claude("hello")
    assert "Claude suggests" in result["proposed_text"]
    assert result["requires_confirmation"] is True


def test_graph_analyzer_orphan_detection():
    graph = ProgramGraph(
        nodes=[GraphNode(id="a", label="A"), GraphNode(id="b", label="B")],
        edges=[GraphEdge(source="a", target="b")],
    )
    assert analyze_graph(graph) == []

    graph.nodes.append(GraphNode(id="c", label="C"))
    insights = analyze_graph(graph)
    assert len(insights) == 1
    assert insights[0]["type"] == "GRAPH_ORPHAN"


def test_graph_analyzer_no_orphans_for_single_node():
    graph = ProgramGraph(nodes=[GraphNode(id="a", label="A")])
    assert analyze_graph(graph) == []


def test_interpret_text_intents():
    assert interpret_text("add a note")["intent"] == "ADD_REQUEST"
    assert interpret_text("delete item")["intent"] == "REMOVE_REQUEST"
    assert interpret_text("hello")["intent"] == "UNKNOWN"


def test_projects_catalog():
    assert isinstance(PROJECTS, list)
    assert len(PROJECTS) >= 1
    assert all(p.get("id") for p in PROJECTS)


# ---------------------------------------------------------------------------
# backend/tasks/telemetry_tasks.py
# ---------------------------------------------------------------------------


def _boom(*args, **kwargs):
    raise RuntimeError("boom")


def test_record_telemetry_event_happy_path(monkeypatch):
    monkeypatch.setattr(
        "backend.services.telemetry._record_sync",
        lambda *a, **k: {"id": "test-uuid"},
    )
    result = record_telemetry_event.apply(
        kwargs={"event_type": "test.event", "metadata": {}}
    ).get()
    assert result == "test-uuid"


def test_record_telemetry_event_retries_on_failure(monkeypatch):
    monkeypatch.setattr(
        "backend.services.telemetry._record_sync",
        _boom,
    )
    with pytest.raises(Exception):
        record_telemetry_event.apply(kwargs={"event_type": "test.event"}).get()


# ---------------------------------------------------------------------------
# backend/api/routes/betterstack_onboarding.py (shared client)
# ---------------------------------------------------------------------------


def test_betterstack_client_disabled_without_key():
    client = BetterStackOnboardingClient()
    assert client.enabled is False
    assert client.send_event({"event": "x"}) is False


def test_betterstack_client_success(monkeypatch):
    monkeypatch.setattr(settings, "BETTERSTACK_API_KEY", "test-key")
    monkeypatch.setattr(settings, "BETTERSTACK_ONBOARDING_SOURCE_NAME", "test")

    class FakeResponse:
        status_code = 200

    with patch("httpx.post", return_value=FakeResponse()):
        client = BetterStackOnboardingClient()
        assert client.enabled is True
        assert client.send_event({"event": "x"}) is True


def test_betterstack_client_api_error(monkeypatch):
    monkeypatch.setattr(settings, "BETTERSTACK_API_KEY", "test-key")

    class FakeResponse:
        status_code = 500

    with patch("httpx.post", return_value=FakeResponse()):
        client = BetterStackOnboardingClient()
        assert client.send_event({"event": "x"}) is False


def test_betterstack_client_httpx_exception(monkeypatch):
    monkeypatch.setattr(settings, "BETTERSTACK_API_KEY", "test-key")

    with patch("httpx.post", side_effect=httpx.ConnectError("nope")):
        client = BetterStackOnboardingClient()
        assert client.send_event({"event": "x"}) is False


def test_get_betterstack_client_caches():
    c1 = get_betterstack_client()
    c2 = get_betterstack_client()
    assert c1 is c2


# ---------------------------------------------------------------------------
# backend/api/routes/onboarding_telemetry.py
# ---------------------------------------------------------------------------


def test_track_onboarding_event_valid():
    from backend.api.routes.onboarding_telemetry import OnboardingTelemetryEvent

    class FakeDb:
        pass

    event = OnboardingTelemetryEvent(event="onboarding.welcome_view", timestamp=123)
    result = track_onboarding_event(event, FakeDb())
    assert result["status"] == "recorded"


def test_track_onboarding_event_empty_name():
    from fastapi import HTTPException

    from backend.api.routes.onboarding_telemetry import OnboardingTelemetryEvent

    class FakeDb:
        pass

    event = OnboardingTelemetryEvent(event="", timestamp=123)
    with pytest.raises(HTTPException) as exc:
        track_onboarding_event(event, FakeDb())
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# backend/app/telemetry.py helpers
# ---------------------------------------------------------------------------


def _raise(*args, **kwargs):
    raise RuntimeError("log fail")


def test_record_onboarding_event_runs():
    from backend.app.telemetry import record_onboarding_event

    # Should run without raising; BetterStack is disabled in tests.
    record_onboarding_event("onboarding.test_view")


def test_telemetry_functions_swallow_logger_failures(monkeypatch):
    from backend.app import telemetry

    monkeypatch.setattr(telemetry.logger, "info", _raise)
    monkeypatch.setattr(telemetry.logger, "warning", _raise)

    # Should not raise even though the logger is failing.
    telemetry.record_auth_session_outcome("test")
    telemetry.record_materialize_attempt("success")
    telemetry.record_email_collision()


def test_reset_for_tests_is_noop():
    from backend.app.telemetry import reset_for_tests

    reset_for_tests()  # covers the pass


# ---------------------------------------------------------------------------
# backend/services/telemetry.py sync and recent
# ---------------------------------------------------------------------------


def test_telemetry_record_and_recent():
    from backend.services.telemetry import _record_sync, recent

    ev = _record_sync("test.recent", {"x": 1})
    rows = recent(limit=10)
    ids = [r["id"] for r in rows]
    assert ev["id"] in ids
