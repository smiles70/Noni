"""Sprint 19: Module 4 curriculum (building Claude Skills).

The paid-bundle entitlement gate (Sprint A10) is overridden here so these
tests stay focused on content/ISCS behavior. Gate enforcement itself is
tested by `test_a10_smoke.py`.
"""

import json

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.api.routes.curriculum import paid_bundle_dep
from backend.models.curriculum_units_module_4 import UNITS_MODULE_4


@pytest.fixture(autouse=True)
def _bypass_paywall():
    """Skip the paid-bundle gate so these tests can focus on content/ISCS.

    Scoped per-test and cleaned up so it does not leak into the A10 smoke
    suite, which exercises the gate intentionally.
    """
    app.dependency_overrides[paid_bundle_dep] = lambda: None
    yield
    app.dependency_overrides.pop(paid_bundle_dep, None)


client = TestClient(app)

EXPECTED_IDS = {
    "module4-unit-1",
    "module4-unit-2",
    "module4-unit-3",
    "module4-unit-4",
    "module4-unit-5",
    "module4-unit-6",
}


def test_module_4_units_catalog_has_all_six():
    body = client.get("/api/curriculum/module-4/units").json()
    assert body["module"] == 4
    assert {u["id"] for u in body["units"]} == EXPECTED_IDS


def test_each_module_4_unit_returns_an_approved_page():
    for unit_id in EXPECTED_IDS:
        body = client.get(f"/api/curriculum/module-4/units/{unit_id}").json()
        assert body["module"] == 4
        assert body["unit_id"] == unit_id
        assert body["ui_state"]["content"], f"empty content for {unit_id}"


def test_module_4_unknown_unit_returns_404():
    assert client.get("/api/curriculum/module-4/units/nope").status_code == 404


def test_module_4_next_returns_one_of_the_six():
    body = client.get("/api/curriculum/module-4/next").json()
    assert body["module"] == 4
    assert body["unit_id"] in EXPECTED_IDS


def test_module_4_units_have_telemetry_requirements_in_range():
    for u in UNITS_MODULE_4:
        assert u.telemetry_requirements, f"{u.id} missing telemetry_requirements"
        for k, v in u.telemetry_requirements.items():
            assert 0.0 <= v <= 1.0


def test_module_4_content_no_urgency_language():
    forbidden = ["hurry", "urgent", "limited time", "act now", "expires", "only today"]
    catalog = client.get("/api/curriculum/module-4/units").text.lower()
    for w in forbidden:
        assert w not in catalog
    for unit_id in EXPECTED_IDS:
        page = client.get(f"/api/curriculum/module-4/units/{unit_id}").text.lower()
        for w in forbidden:
            assert w not in page, f"{w!r} in {unit_id}"


def test_module_4_decision_recorded_with_audit_columns():
    client.get("/api/curriculum/module-4/units/module4-unit-1")
    rows = client.get("/api/telemetry/export").json()["events"]
    matches = [
        r
        for r in rows
        if r.get("request_path") == "/api/curriculum/module-4/units/module4-unit-1"
    ]
    assert matches
    row = matches[-1]
    assert row["event"] == "iscs_decision"
    assert row["decision_reason"] == "approved"
    md = row.get("event_metadata") or {}
    if isinstance(md, str):
        md = json.loads(md)
    assert "telemetry_requirements" in md
