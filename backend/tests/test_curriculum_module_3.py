"""Sprint 18: Module 3 curriculum (long-term judgment & autonomy)."""

import json

from fastapi import Depends
from fastapi.testclient import TestClient

from backend.api.deps import get_current_account
from backend.api.routes.telemetry_export import _require_admin
from backend.app.main import app
from backend.models.accounts import Account
from backend.models.curriculum_units_module_3 import UNITS_MODULE_3


def _mock_require_admin(account: Account = Depends(get_current_account)) -> Account:
    return account


app.dependency_overrides[_require_admin] = _mock_require_admin
client = TestClient(app)
client.headers["Authorization"] = "Bearer mock:test@example.com"

EXPECTED_IDS = {
    "module3-unit-1",
    "module3-unit-2",
    "module3-unit-3",
    "module3-unit-4",
}


def test_module_3_units_catalog_has_all_four():
    body = client.get("/api/curriculum/module-3/units").json()
    assert body["module"] == 3
    assert {u["id"] for u in body["units"]} == EXPECTED_IDS


def test_each_module_3_unit_returns_an_approved_page():
    for unit_id in EXPECTED_IDS:
        body = client.get(f"/api/curriculum/module-3/units/{unit_id}").json()
        assert body["module"] == 3
        assert body["unit_id"] == unit_id
        assert body["ui_state"]["content"], f"empty content for {unit_id}"


def test_module_3_unknown_unit_returns_404():
    assert client.get("/api/curriculum/module-3/units/nope").status_code == 404


def test_module_3_next_returns_one_of_the_four():
    body = client.get("/api/curriculum/module-3/next").json()
    assert body["module"] == 3
    assert body["unit_id"] in EXPECTED_IDS


def test_module_3_units_have_telemetry_requirements_in_range():
    for u in UNITS_MODULE_3:
        assert u.telemetry_requirements, f"{u.id} missing telemetry_requirements"
        for k, v in u.telemetry_requirements.items():
            assert 0.0 <= v <= 1.0


def test_module_3_content_no_urgency_language():
    forbidden = ["hurry", "urgent", "limited time", "act now", "expires", "only today"]
    catalog = client.get("/api/curriculum/module-3/units").text.lower()
    for w in forbidden:
        assert w not in catalog
    for unit_id in EXPECTED_IDS:
        page = client.get(f"/api/curriculum/module-3/units/{unit_id}").text.lower()
        for w in forbidden:
            assert w not in page, f"{w!r} in {unit_id}"


def test_module_3_lesson_endpoint_returns_four_page_shape():
    """S25.3: every Module 3 unit serves a four-page lesson
    (recap / principle / example / retrieval). All pages held at
    complexity=1 to respect each unit's max_complexity=1 ceiling.
    """
    for unit_id in EXPECTED_IDS:
        r = client.get(f"/api/curriculum/module-3/units/{unit_id}/lesson")
        assert r.status_code == 200, f"{unit_id}: /lesson endpoint failed"
        body = r.json()
        assert body["module"] == 3
        assert body["unit_id"] == unit_id
        pages = body["pages"]
        assert len(pages) == 4, f"{unit_id}: expected 4 pages, got {len(pages)}"
        assert pages[0]["page_type"] == "recap"
        assert pages[-1]["page_type"] == "retrieval"
        for p in pages:
            assert p["complexity"] == 1, (
                f"{unit_id}/{p['id']}: Module 3 caps complexity at 1, "
                f"got {p['complexity']}"
            )


def test_module_3_lesson_pages_have_no_urgency_language():
    """S25.3: walk every page in every Module 3 lesson for urgency words."""
    forbidden = ["hurry", "urgent", "limited time", "act now", "expires", "only today"]
    for unit_id in EXPECTED_IDS:
        body = client.get(f"/api/curriculum/module-3/units/{unit_id}/lesson").json()
        for page in body["pages"]:
            haystack = (
                " ".join(page.get("content", []))
                + " "
                + (page.get("principle") or "")
                + " "
                + str(page.get("example") or "")
                + " "
                + str(page.get("retrieval") or "")
            ).lower()
            for w in forbidden:
                assert w not in haystack, f"{w!r} in {unit_id}/{page['id']}"


def test_module_3_decision_recorded_with_audit_columns():
    client.get("/api/curriculum/module-3/units/module3-unit-1")
    rows = client.get("/api/telemetry/export").json()["events"]
    matches = [
        r
        for r in rows
        if r.get("request_path") == "/api/curriculum/module-3/units/module3-unit-1"
    ]
    assert matches
    row = matches[-1]
    assert row["event"] == "iscs_decision"
    assert row["decision_reason"] == "approved"
    md = row.get("event_metadata") or {}
    if isinstance(md, str):
        md = json.loads(md)
    assert "telemetry_requirements" in md
