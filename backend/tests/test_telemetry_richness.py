"""Sprint 10 / ADR 0009: verify ISCS decisions are captured with promoted audit columns."""

from fastapi import Depends
from fastapi.testclient import TestClient

from backend.api.deps import get_current_account
from backend.api.routes.telemetry_export import _require_admin
from backend.app.main import app
from backend.models.accounts import Account


def _mock_require_admin(account: Account = Depends(get_current_account)) -> Account:
    return account


app.dependency_overrides[_require_admin] = _mock_require_admin
client = TestClient(app)
client.headers["Authorization"] = "Bearer mock:test@example.com"


def _export() -> list[dict]:
    res = client.get("/api/telemetry/export")
    assert res.status_code == 200
    return res.json()["events"]


def test_what_is_ai_records_iscs_decision_with_audit_columns():
    # `_export()` orders by id DESC (newest first), and other test files
    # share the global telemetry store, so we must filter by request_path
    # rather than indexing by position.
    before = len(_export())
    res = client.get("/api/curriculum/what-is-ai")
    assert res.status_code == 200

    rows = _export()
    assert len(rows) == before + 1
    matches = [r for r in rows if r.get("request_path") == "/api/curriculum/what-is-ai"]
    assert matches, "expected at least one telemetry row for what-is-ai"
    row = matches[0]  # newest first
    assert row["event"] == "iscs_decision"
    assert row["request_path"] == "/api/curriculum/what-is-ai"
    assert isinstance(row["stability"], (int, float))
    assert row["selected_state_id"] in {"ai-1", "ai-2"}
    assert row["decision_reason"] == "approved"
    assert row["max_complexity"] == 2


def test_unit_get_records_iscs_decision_for_that_unit():
    res = client.get("/api/curriculum/units/unit-2")
    assert res.status_code == 200

    rows = _export()
    matches = [
        r for r in rows if r.get("request_path") == "/api/curriculum/units/unit-2"
    ]
    assert matches, "expected at least one telemetry row for unit-2"
    row = matches[0]  # newest first
    assert row["event"] == "iscs_decision"
    assert row["decision_reason"] == "approved"
    assert isinstance(row["stability"], (int, float))
    assert row["selected_state_id"] is not None


def test_next_unit_records_recommendation():
    res = client.get("/api/curriculum/next-unit")
    assert res.status_code == 200

    rows = _export()
    matches = [r for r in rows if r["event"] == "iscs_recommendation"]
    assert matches
    row = matches[0]  # newest first
    assert row["request_path"] == "/api/curriculum/next-unit"
    assert row["decision_reason"] == "linear-walk"
    assert row["selected_state_id"] is not None


def test_csv_export_includes_audit_columns():
    res = client.get("/api/telemetry/export.csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    header = res.text.splitlines()[0]
    for col in [
        "request_path",
        "stability",
        "selected_state_id",
        "decision_reason",
        "max_complexity",
    ]:
        assert col in header, f"CSV header missing column {col!r}"
