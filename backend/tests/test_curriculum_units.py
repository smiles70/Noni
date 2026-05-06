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
        assert ids == {"unit-2", "unit-3", "unit-4"}

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
        assert len(body["units"]) == 3
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
        assert body["unit_id"] in {"unit-2", "unit-3", "unit-4"}
