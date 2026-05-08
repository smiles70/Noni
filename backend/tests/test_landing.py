"""Tests for the Golden Landing Flow contract."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.models.landing import LANDING_STEPS, get_step


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestLandingData:
    def test_eight_steps_present(self):
        assert len(LANDING_STEPS) == 8

    def test_sequences_are_zero_through_seven_in_order(self):
        seqs = [s.sequence for s in LANDING_STEPS]
        assert seqs == list(range(8))

    def test_ids_are_unique_and_well_formed(self):
        ids = [s.id for s in LANDING_STEPS]
        assert len(set(ids)) == 8
        for s in LANDING_STEPS:
            assert s.id == f"step-{s.sequence}"

    def test_exit_always_safe_is_true_for_every_step(self):
        for s in LANDING_STEPS:
            assert s.exit_always_safe is True, f"{s.id} exit_always_safe must be True"

    def test_no_user_action_required_before_step_4(self):
        for s in LANDING_STEPS:
            if s.sequence < 4:
                assert (
                    s.requires_user_action is False
                ), f"{s.id} (sequence {s.sequence}) must not require user action"

    def test_step_4_is_first_explicit_action(self):
        step_4 = get_step("step-4")
        assert step_4 is not None
        assert step_4.requires_user_action is True

    def test_no_display_copy_finalized_yet(self):
        # Per spec: copy finalization is explicitly out of scope for this sprint.
        for s in LANDING_STEPS:
            assert (
                s.display_title is None
            ), f"{s.id} display_title must be None until copy sprint"
            assert (
                s.display_body is None
            ), f"{s.id} display_body must be None until copy sprint"
            assert (
                s.action_label is None
            ), f"{s.id} action_label must be None until copy sprint"

    def test_get_step_helper(self):
        assert get_step("step-0").name == "Arrival"
        assert get_step("does-not-exist") is None


class TestLandingRoutes:
    def test_list_steps(self, client):
        r = client.get("/api/landing/steps")
        assert r.status_code == 200
        body = r.json()
        assert len(body["steps"]) == 8
        for k in ("id", "sequence", "name", "exit_safety", "requires_user_action"):
            assert k in body["steps"][0]

    def test_get_one_step(self, client):
        r = client.get("/api/landing/steps/step-3")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == "step-3"
        assert body["sequence"] == 3
        assert body["requires_user_action"] is False

    def test_get_unknown_step_returns_404(self, client):
        r = client.get("/api/landing/steps/step-999")
        assert r.status_code == 404
