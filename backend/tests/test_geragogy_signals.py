"""Tests for the Geragogy signal model."""
from backend.core.geragogy_engine.cognitive_model import GeragogySignalModel
from backend.models.user import UserAction


def _action(action_type):
    return UserAction(user_id="u1", action_type=action_type)


class TestGeragogySignalModel:
    def test_initial_state(self):
        m = GeragogySignalModel()
        s = m.update(_action("PAGE_VIEW"))  # no-op branch -> state unchanged
        assert s["mastery"] == 0.2
        assert s["strain"] == 0.2
        assert s["load"] == 0.2

    def test_task_complete_raises_mastery_lowers_strain_and_load(self):
        m = GeragogySignalModel()
        s = m.update(_action("TASK_COMPLETE"))
        assert s["mastery"] > 0.2
        assert s["strain"] < 0.2
        assert s["load"] < 0.2

    def test_error_raises_strain_and_load(self):
        m = GeragogySignalModel()
        s = m.update(_action("ERROR"))
        assert s["strain"] > 0.2
        assert s["load"] > 0.2

    def test_clipping_to_unit_interval(self):
        m = GeragogySignalModel()
        for _ in range(20):
            m.update(_action("ERROR"))
        s = m.update(_action("ERROR"))
        assert 0.0 <= s["mastery"] <= 1.0
        assert 0.0 <= s["strain"] <= 1.0
        assert 0.0 <= s["load"] <= 1.0
        assert s["strain"] == 1.0
        assert s["load"] == 1.0
