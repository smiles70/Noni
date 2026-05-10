"""Sprint 17: Module 2 curriculum (sustained Claude use over time)."""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.models.curriculum_units_module_2 import UNITS_MODULE_2

client = TestClient(app)

EXPECTED_IDS = {
    "module2-unit-1",
    "module2-unit-2",
    "module2-unit-3",
    "module2-unit-4",
    "module2-unit-5",
}


def test_module_2_units_catalog_has_all_five():
    res = client.get("/api/curriculum/module-2/units")
    assert res.status_code == 200
    body = res.json()
    assert body["module"] == 2
    ids = {u["id"] for u in body["units"]}
    assert ids == EXPECTED_IDS


def test_each_module_2_unit_returns_an_approved_page():
    for unit_id in EXPECTED_IDS:
        res = client.get(f"/api/curriculum/module-2/units/{unit_id}")
        assert res.status_code == 200
        body = res.json()
        assert body["module"] == 2
        assert body["unit_id"] == unit_id
        assert body["ui_state"]["content"], f"empty content for {unit_id}"


def test_module_2_unknown_unit_returns_404():
    assert client.get("/api/curriculum/module-2/units/nope").status_code == 404


def test_module_2_next_returns_one_of_the_five():
    body = client.get("/api/curriculum/module-2/next").json()
    assert body["module"] == 2
    assert body["unit_id"] in EXPECTED_IDS


def test_module_2_units_have_telemetry_requirements_in_range():
    for u in UNITS_MODULE_2:
        assert u.telemetry_requirements, f"{u.id} missing telemetry_requirements"
        for k, v in u.telemetry_requirements.items():
            assert 0.0 <= v <= 1.0, f"{u.id} {k}={v} out of range"


def test_module_2_content_no_urgency_language():
    forbidden = ["hurry", "urgent", "limited time", "act now", "expires", "only today"]
    catalog = client.get("/api/curriculum/module-2/units").text.lower()
    for w in forbidden:
        assert w not in catalog
    for unit_id in EXPECTED_IDS:
        page = client.get(f"/api/curriculum/module-2/units/{unit_id}").text.lower()
        for w in forbidden:
            assert w not in page, f"{w!r} in {unit_id}"


def test_module_2_decision_recorded_with_audit_columns():
    client.get("/api/curriculum/module-2/units/module2-unit-1")
    rows = client.get("/api/telemetry/export").json()["events"]
    matches = [
        r
        for r in rows
        if r.get("request_path") == "/api/curriculum/module-2/units/module2-unit-1"
    ]
    assert matches
    row = matches[-1]
    assert row["event"] == "iscs_decision"
    assert row["decision_reason"] == "approved"
    # metadata may be a dict or a JSON string depending on the export shape;
    # what matters is that the telemetry_requirements payload is recorded.
    import json

    md = row.get("event_metadata") or {}
    if isinstance(md, str):
        md = json.loads(md)
    assert "telemetry_requirements" in md
