"""Sprint 19: Module 4 curriculum (building Claude Skills).

The paid-bundle entitlement gate (Sprint A10) is overridden here so these
tests stay focused on content/ISCS behavior. Gate enforcement itself is
tested by `test_a10_smoke.py`.
"""

import json

import pytest
from fastapi.testclient import TestClient

from backend.api.routes.curriculum import paid_bundle_dep
from backend.app.main import app
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


def test_module_4_content_has_full_lesson_structure(_bypass_paywall):
    """P10: every unit must have 4 pages (recap/principle/example/retrieval)
    with at least one ExampleBlock and one RetrievalBlock."""
    for unit_id in EXPECTED_IDS:
        body = client.get(f"/api/curriculum/module-4/units/{unit_id}/lesson").json()
        pages = body["pages"]
        assert len(pages) >= 4, f"{unit_id} has only {len(pages)} pages"
        page_types = {p.get("page_type") for p in pages}
        assert "recap" in page_types, f"{unit_id} missing recap page"
        assert "principle" in page_types, f"{unit_id} missing principle page"
        assert "example" in page_types, f"{unit_id} missing example page"
        assert "retrieval" in page_types, f"{unit_id} missing retrieval page"
        assert any(p.get("example") for p in pages), f"{unit_id} missing ExampleBlock"
        assert any(
            p.get("retrieval") for p in pages
        ), f"{unit_id} missing RetrievalBlock"


def test_module_4_content_preserves_human_authority(_bypass_paywall):
    """Module 4's defining contract: Skills assist, learner decides."""
    control_markers = [
        "review",
        "stop",
        "pause",
        "decide",
        "judgment",
        "your rules",
        "your boundaries",
        "your thinking",
        "in control",
        "you choose",
        "you can",
    ]
    for unit_id in EXPECTED_IDS:
        body = client.get(f"/api/curriculum/module-4/units/{unit_id}/lesson").json()
        all_content = []
        for page in body["pages"]:
            all_content.extend(page.get("content", []))
            if page.get("principle"):
                all_content.append(page["principle"])
            if page.get("example"):
                ex = page["example"]
                all_content.extend(
                    [
                        ex.get("situation", ""),
                        ex.get("claude_says", ""),
                        ex.get("takeaway", ""),
                    ]
                )
            if page.get("retrieval"):
                r = page["retrieval"]
                all_content.extend([r.get("prompt", ""), r.get("explanation", "")])
        content = " ".join(all_content).lower()
        assert any(
            m in content for m in control_markers
        ), f"{unit_id} missing human-control marker"
