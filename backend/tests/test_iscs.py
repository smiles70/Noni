"""Tests for the Interface State Control System (ISCS)."""

import numpy as np

from backend.core.interface_control.state_estimator import InterfaceStateEstimator
from backend.core.interface_control.stability_metric import compute_stability
from backend.core.interface_control.state_selector import select_ui_state


class TestStateEstimator:
    def test_initial_state_is_zero_with_unit_covariance(self):
        est = InterfaceStateEstimator(dim=3)
        assert np.allclose(est.state, np.zeros(3))
        assert est.covariance.shape == (3, 3)

    def test_update_moves_state_toward_telemetry(self):
        est = InterfaceStateEstimator(dim=3)
        state, _ = est.update([1.0, 1.0, 1.0])
        # Mixing weight 0.1 toward telemetry from zero -> 0.1
        assert np.allclose(state, [0.1, 0.1, 0.1])

    def test_covariance_grows_each_update(self):
        est = InterfaceStateEstimator(dim=3)
        _, cov0 = est.update([0.0, 0.0, 0.0])
        s0 = compute_stability(cov0)
        _, cov1 = est.update([0.0, 0.0, 0.0])
        s1 = compute_stability(cov1)
        assert s1 > s0


class TestStabilityMetric:
    def test_returns_max_eigenvalue(self):
        cov = np.diag([0.5, 0.2, 0.1])
        assert compute_stability(cov) == 0.5

    def test_handles_identity(self):
        assert compute_stability(np.eye(4)) == 1.0


class TestStateSelector:
    def _candidates(self):
        return [
            {"id": "a", "complexity": 1},
            {"id": "b", "complexity": 2},
            {"id": "c", "complexity": 3},
        ]

    def test_low_stability_picks_simplest(self):
        # max_complexity = max(1, int(3 - 0.1)) = 2; first match is complexity 1
        result = select_ui_state(self._candidates(), stability=0.1)
        assert result["id"] == "a"

    def test_high_stability_falls_back_when_no_safe_candidate(self):
        # max_complexity = max(1, int(3 - 5.0)) = 1; only "a" qualifies
        result = select_ui_state(self._candidates(), stability=5.0)
        assert result["id"] == "a"

    def test_returns_first_safe_candidate(self):
        result = select_ui_state(
            [{"id": "x", "complexity": 5}, {"id": "y", "complexity": 1}],
            stability=0.1,
        )
        assert result["id"] == "y"

    def test_falls_back_to_first_when_nothing_safe(self):
        result = select_ui_state([{"id": "z", "complexity": 9}], stability=0.0)
        assert result["id"] == "z"
