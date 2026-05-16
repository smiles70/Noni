"""Tests for Units 2-4 endpoints and data integrity."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.models.curriculum_units import UNITS, get_unit


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestUnitData:
    def test_three_units_present(self):
        ids = {u.id for u in UNITS}
        assert ids == {"unit-2", "unit-3", "unit-4", "unit-5", "unit-6", "unit-7"}

    def test_each_unit_has_at_least_one_page(self):
        for u in UNITS:
            assert len(u.pages) >= 1, f"{u.id} has no pages"

    def test_no_page_exceeds_unit_max_complexity(self):
        for u in UNITS:
            for p in u.pages:
                assert (
                    p.complexity <= u.max_complexity
                ), f"{u.id}/{p.id} complexity {p.complexity} > unit max {u.max_complexity}"

    def test_get_unit_helper(self):
        assert get_unit("unit-2").title == "What Is Claude"
        assert get_unit("does-not-exist") is None


class TestUnitsRoute:
    def test_list_units(self, client):
        r = client.get("/api/curriculum/units")
        assert r.status_code == 200
        body = r.json()
        assert len(body["units"]) == 6
        for u in body["units"]:
            for k in (
                "id",
                "title",
                "description",
                "max_complexity",
                "stability_threshold",
            ):
                assert k in u

    def test_get_unit_page_returns_iscs_approved(self, client):
        r = client.get("/api/curriculum/units/unit-3")
        assert r.status_code == 200
        body = r.json()
        assert body["unit_id"] == "unit-3"
        assert "ui_state" in body and "stability" in body
        page = body["ui_state"]
        for k in ("id", "title", "content", "complexity"):
            assert k in page
        assert page["complexity"] <= 2  # unit-3 max

    def test_get_unknown_unit_returns_404(self, client):
        r = client.get("/api/curriculum/units/unit-999")
        assert r.status_code == 404

    def test_next_unit_contract(self, client):
        r = client.get("/api/curriculum/next-unit")
        assert r.status_code == 200
        body = r.json()
        for k in ("unit_id", "title", "stability", "reason"):
            assert k in body
        assert body["unit_id"] in {
            "unit-2",
            "unit-3",
            "unit-4",
            "unit-5",
            "unit-6",
            "unit-7",
        }


class TestLessonRoute:
    """Curriculum-expansion Phase 1: `/lesson` endpoint contract.

    Returns ALL pages for a unit in author order (not ISCS-selected).
    The legacy `/units/{id}` path is unchanged and tested above; that
    test must remain green so external consumers and the existing
    single-page renderer keep working.
    """

    def test_lesson_returns_ordered_pages(self, client):
        r = client.get("/api/curriculum/units/unit-3/lesson")
        assert r.status_code == 200
        body = r.json()
        assert body["module"] == 1
        assert body["unit_id"] == "unit-3"
        assert body["unit_title"]
        assert isinstance(body["pages"], list)
        assert len(body["pages"]) >= 1
        # Author order preserved.
        ids = [p["id"] for p in body["pages"]]
        assert ids == sorted(ids, key=ids.index)
        # Every page respects the unit's complexity ceiling.
        for p in body["pages"]:
            assert p["complexity"] <= 2  # unit-3.max_complexity

    def test_lesson_legacy_pages_omit_none_blocks(self, client):
        """Pages authored under the legacy schema should not leak `null`
        retrieval/example/principle fields onto the wire."""
        r = client.get("/api/curriculum/units/unit-3/lesson")
        assert r.status_code == 200
        for p in r.json()["pages"]:
            assert "example" not in p or p["example"] is not None
            assert "retrieval" not in p or p["retrieval"] is not None
            assert "principle" not in p or p["principle"] is not None

    def test_lesson_unknown_unit_404(self, client):
        r = client.get("/api/curriculum/units/unit-999/lesson")
        assert r.status_code == 404

    def test_legacy_units_endpoint_still_returns_iscs_single_page(self, client):
        """Regression guard: the legacy single-page route must keep working."""
        r = client.get("/api/curriculum/units/unit-3")
        assert r.status_code == 200
        body = r.json()
        assert "ui_state" in body
        assert isinstance(body["ui_state"], dict)
        for k in ("id", "title", "content", "complexity"):
            assert k in body["ui_state"]


class TestRetrievalChoiceRoute:
    """POST /retrieval-choice records the learner's pick as telemetry.

    Free-track endpoint (no entitlement check). Body shape is closed:
    extras are rejected at validation.
    """

    def _body(self, **overrides):
        base = {
            "module": 1,
            "unit_id": "unit-2",
            "page_id": "u2-retrieval",
            "chosen_id": "a",
            "correct": True,
        }
        base.update(overrides)
        return base

    def test_records_choice_returns_recorded_true(self, client):
        r = client.post("/api/curriculum/retrieval-choice", json=self._body())
        assert r.status_code == 200
        assert r.json() == {"recorded": True}

    def test_rejects_extra_fields(self, client):
        body = self._body()
        body["smuggled_signal"] = 0.7
        r = client.post("/api/curriculum/retrieval-choice", json=body)
        assert r.status_code == 422

    def test_rejects_out_of_range_module(self, client):
        r = client.post(
            "/api/curriculum/retrieval-choice",
            json=self._body(module=99),
        )
        assert r.status_code == 422

    def test_rejects_missing_required_field(self, client):
        body = self._body()
        del body["chosen_id"]
        r = client.post("/api/curriculum/retrieval-choice", json=body)
        assert r.status_code == 422
