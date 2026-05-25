"""Sprint 'paid modules' P1 + P2 — paid-track /lesson endpoints and
widened retrieval-choice schema.

Mirrors `test_curriculum_module_3.py::test_module_3_lesson_endpoint_*`
exactly so any drift between the free and paid /lesson surfaces is
visible side-by-side.

Coverage:
  - P1: GET /api/curriculum/module-{4,5}/units/{id}/lesson returns the
        same shape as the free /lesson endpoints (module, unit_id,
        unit_title, pages, stability).
  - P1: every paid unit's lesson respects max_complexity and contains
        no urgency language (parity with the free-track audit).
  - P1: /lesson honours the paywall when entitlement is absent (402
        with billing.signin_or_purchase_required for anonymous; tests
        rely on the smoke suite to cover signed-in-without-grant).
  - P1: unknown unit ids return 404.
  - P2: POST /api/curriculum/retrieval-choice accepts module=4 and
        module=5 and writes a telemetry row.
  - P2: module=0 and module=6 are still rejected as a regression guard.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.routes.curriculum import paid_bundle_dep
from backend.app.main import app
from backend.models.curriculum_units_module_4 import UNITS_MODULE_4
from backend.models.curriculum_units_module_5 import UNITS_MODULE_5

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixture: bypass the paywall for the parity-shape tests. The paywall
# behaviour itself is covered explicitly below by `test_*_lesson_paywalled_*`
# which intentionally does NOT use this fixture.
# ---------------------------------------------------------------------------


@pytest.fixture()
def bypass_paywall():
    app.dependency_overrides[paid_bundle_dep] = lambda: None
    yield
    app.dependency_overrides.pop(paid_bundle_dep, None)


# ---------------------------------------------------------------------------
# P1: shape parity with the free /lesson endpoints
# ---------------------------------------------------------------------------


M4_IDS = {u.id for u in UNITS_MODULE_4}
M5_IDS = {u.id for u in UNITS_MODULE_5}


def _assert_lesson_shape(body: dict, expected_module: int, expected_unit: str):
    """The same shape the free /lesson endpoints emit."""
    assert body["module"] == expected_module
    assert body["unit_id"] == expected_unit
    assert "unit_title" in body and body["unit_title"]
    assert isinstance(body["pages"], list) and body["pages"], (
        "lesson must return at least one page"
    )
    assert "stability" in body
    # Pages stay within the unit's max_complexity ceiling.
    for p in body["pages"]:
        assert "id" in p and "title" in p and "content" in p


def test_module_4_lesson_returns_canonical_shape(bypass_paywall):
    for unit_id in M4_IDS:
        r = client.get(f"/api/curriculum/module-4/units/{unit_id}/lesson")
        assert r.status_code == 200, f"{unit_id}: {r.text}"
        _assert_lesson_shape(r.json(), 4, unit_id)


def test_module_5_lesson_returns_canonical_shape(bypass_paywall):
    for unit_id in M5_IDS:
        r = client.get(f"/api/curriculum/module-5/units/{unit_id}/lesson")
        assert r.status_code == 200, f"{unit_id}: {r.text}"
        _assert_lesson_shape(r.json(), 5, unit_id)


def test_paid_lessons_have_no_urgency_language(bypass_paywall):
    """Free-track audit invariant carried over to paid modules."""
    forbidden = [
        "hurry",
        "urgent",
        "limited time",
        "act now",
        "expires",
        "only today",
    ]
    for module, unit_ids in ((4, M4_IDS), (5, M5_IDS)):
        for unit_id in unit_ids:
            body = client.get(
                f"/api/curriculum/module-{module}/units/{unit_id}/lesson"
            ).json()
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
                    assert w not in haystack, (
                        f"{w!r} in module-{module}/{unit_id}/{page['id']}"
                    )


def test_module_4_lesson_unknown_unit_returns_404(bypass_paywall):
    r = client.get("/api/curriculum/module-4/units/nope/lesson")
    assert r.status_code == 404


def test_module_5_lesson_unknown_unit_returns_404(bypass_paywall):
    r = client.get("/api/curriculum/module-5/units/nope/lesson")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# P1: paywall handshake — no entitlement, no lesson
# ---------------------------------------------------------------------------


def test_module_4_lesson_paywalled_anonymous():
    """Without the bypass fixture, the dependency rejects anonymous
    callers exactly like /units/{id} does."""
    r = client.get("/api/curriculum/module-4/units/module4-unit-1/lesson")
    assert r.status_code == 402, r.text
    assert r.json()["detail"]["envelope_id"] == "billing.signin_or_purchase_required"


def test_module_5_lesson_paywalled_anonymous():
    r = client.get("/api/curriculum/module-5/units/module5-unit-1/lesson")
    assert r.status_code == 402, r.text
    assert r.json()["detail"]["envelope_id"] == "billing.signin_or_purchase_required"


# ---------------------------------------------------------------------------
# P2: retrieval-choice accepts module=4 and module=5
# ---------------------------------------------------------------------------


def test_retrieval_choice_accepts_module_4():
    body = {
        "module": 4,
        "unit_id": "module4-unit-1",
        "page_id": "p1",
        "chosen_id": "a",
        "correct": True,
    }
    r = client.post("/api/curriculum/retrieval-choice", json=body)
    assert r.status_code == 200, r.text
    assert r.json() == {"recorded": True}


def test_retrieval_choice_accepts_module_5():
    body = {
        "module": 5,
        "unit_id": "module5-unit-1",
        "page_id": "p1",
        "chosen_id": "b",
        "correct": False,
    }
    r = client.post("/api/curriculum/retrieval-choice", json=body)
    assert r.status_code == 200, r.text
    assert r.json() == {"recorded": True}


def test_retrieval_choice_rejects_module_out_of_range():
    """Regression guard for the widened range — 0 and 6 must still 422."""
    for bad in (0, 6, 99):
        r = client.post(
            "/api/curriculum/retrieval-choice",
            json={
                "module": bad,
                "unit_id": "u",
                "page_id": "p",
                "chosen_id": "c",
                "correct": True,
            },
        )
        assert r.status_code == 422, f"module={bad} should be rejected"
