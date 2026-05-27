"""Tests for Module 0 (Introduction to AI) data and endpoints.

Mirrors the test style used for Modules 1-3: integrity checks on the
unit list (ids unique, every retrieval correct_id matches a choice,
every example unit carries an ExampleBlock, no page exceeds its unit's
max_complexity), and a small set of route smoke tests against the
catalog / single-page / lesson endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.models.curriculum_units_module_0 import (
    UNITS_MODULE_0,
    get_module_0_unit,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestModule0Data:
    def test_six_units_present(self):
        ids = {u.id for u in UNITS_MODULE_0}
        assert ids == {
            "module0-unit-1",
            "module0-unit-2",
            "module0-unit-3",
            "module0-unit-4",
            "module0-unit-5",
            "module0-unit-6",
        }

    def test_every_unit_has_four_pages(self):
        for u in UNITS_MODULE_0:
            assert len(u.pages) == 4, f"{u.id} should have 4 pages, has {len(u.pages)}"

    def test_no_page_exceeds_unit_max_complexity(self):
        for u in UNITS_MODULE_0:
            for p in u.pages:
                assert (
                    p.complexity <= u.max_complexity
                ), f"{u.id}/{p.id} complexity {p.complexity} > unit max {u.max_complexity}"

    def test_page_ids_unique_within_unit(self):
        for u in UNITS_MODULE_0:
            ids = [p.id for p in u.pages]
            assert len(ids) == len(set(ids)), f"{u.id} has duplicate page ids"

    def test_every_example_page_has_example_block(self):
        for u in UNITS_MODULE_0:
            for p in u.pages:
                if p.page_type == "example":
                    assert p.example is not None, f"{u.id}/{p.id} missing ExampleBlock"

    def test_every_retrieval_page_has_valid_block(self):
        for u in UNITS_MODULE_0:
            for p in u.pages:
                if p.page_type == "retrieval":
                    assert p.retrieval is not None, f"{u.id}/{p.id} missing RetrievalBlock"
                    choice_ids = {c.id for c in p.retrieval.choices}
                    assert (
                        p.retrieval.correct_id in choice_ids
                    ), f"{u.id}/{p.id} correct_id not in choices"

    def test_first_unit_opens_with_context(self):
        # Convention: the very first lesson of a module uses `context`
        # rather than `recap` because there is nothing to recap yet.
        first = UNITS_MODULE_0[0]
        assert first.pages[0].page_type == "context"

    def test_subsequent_units_open_with_recap(self):
        for u in UNITS_MODULE_0[1:]:
            assert u.pages[0].page_type == "recap", (
                f"{u.id} should open with a recap page"
            )

    def test_get_module_0_unit_helper(self):
        assert get_module_0_unit("module0-unit-1").title == (
            "What people mean when they say AI"
        )
        assert get_module_0_unit("does-not-exist") is None


class TestModule0Routes:
    def test_list_module_0_units(self, client):
        r = client.get("/api/curriculum/module-0/units")
        assert r.status_code == 200
        body = r.json()
        assert body["module"] == 0
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

    def test_get_module_0_unit_page(self, client):
        r = client.get("/api/curriculum/module-0/units/module0-unit-1")
        assert r.status_code == 200
        body = r.json()
        assert body["module"] == 0
        assert body["unit_id"] == "module0-unit-1"
        assert "ui_state" in body and "stability" in body

    def test_get_module_0_lesson(self, client):
        r = client.get("/api/curriculum/module-0/units/module0-unit-1/lesson")
        assert r.status_code == 200
        body = r.json()
        assert body["module"] == 0
        assert body["unit_id"] == "module0-unit-1"
        assert len(body["pages"]) == 4

    def test_unknown_module_0_unit_returns_404(self, client):
        r = client.get("/api/curriculum/module-0/units/module0-unit-999")
        assert r.status_code == 404

    def test_lesson_menu_includes_module_0_first(self, client):
        r = client.get("/api/curriculum/menu")
        assert r.status_code == 200
        body = r.json()
        assert body["modules"][0]["id"] == 0
        assert "Module 0" in body["modules"][0]["title"]
        assert len(body["modules"][0]["units"]) == 6

    def test_retrieval_choice_accepts_module_0(self, client):
        r = client.post(
            "/api/curriculum/retrieval-choice",
            json={
                "module": 0,
                "unit_id": "module0-unit-1",
                "page_id": "m0u1-retrieval",
                "chosen_id": "a",
                "correct": True,
            },
        )
        assert r.status_code == 200
        assert r.json() == {"recorded": True}
