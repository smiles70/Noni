"""HTTP route tests via FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert "version" in body
    assert "environment" in body


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "version" in r.json()


def test_curriculum_what_is_ai(client):
    r = client.get("/api/curriculum/what-is-ai")
    assert r.status_code == 200
    body = r.json()
    assert "ui_state" in body
    assert "stability" in body
    page = body["ui_state"]
    for key in ("id", "title", "content", "complexity"):
        assert key in page
    assert isinstance(page["content"], list)
    assert page["complexity"] >= 1


def test_signals_user_action(client):
    # Sprint 22 I2: signals now require auth.
    client.headers["Authorization"] = "Bearer mock:test@example.com"
    r = client.post(
        "/api/signals/user-action",
        json={"user_id": "test_user", "action_type": "TASK_COMPLETE"},
    )
    assert r.status_code == 200
    signals = r.json()["signals"]
    for key in ("mastery", "strain", "load"):
        assert 0.0 <= signals[key] <= 1.0


def test_signals_user_action_rejects_unknown_type(client):
    # Sprint 22 I2: signals now require auth.
    client.headers["Authorization"] = "Bearer mock:test@example.com"
    r = client.post(
        "/api/signals/user-action",
        json={"user_id": "u", "action_type": "NOT_A_REAL_TYPE"},
    )
    assert r.status_code == 422


def test_signals_telemetry(client):
    # Sprint 22 I2: signals now require auth.
    client.headers["Authorization"] = "Bearer mock:test@example.com"
    r = client.post(
        "/api/signals/telemetry",
        json={"type": "ROUTE_TEST", "payload": {"x": 1}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["event"] == "ROUTE_TEST"
    assert body["metadata"] == {"x": 1}
