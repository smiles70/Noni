"""ISCS - State Estimator (uncertainty-constrained)."""
import numpy as np

class InterfaceStateEstimator:
    def __init__(self, dim: int = 3) -> None:
        self.state = np.zeros(dim)
        self.covariance = np.eye(dim) * 0.1

    def update(self, telemetry):
        telemetry = np.array(telemetry)
        self.state = 0.9 * self.state + 0.1 * telemetry
        self.covariance = self.covariance + np.eye(len(self.state)) * 0.01
        return self.state, self.covariance
