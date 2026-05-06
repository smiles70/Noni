"""Geragogy signal model. Emits mastery/strain/load; does NOT control UI."""
import numpy as np
from backend.models.user import UserAction

class GeragogySignalModel:
    def __init__(self) -> None:
        self.state = np.array([0.2, 0.2, 0.2])

    def update(self, action: UserAction) -> dict:
        if action.action_type == "TASK_COMPLETE":
            self.state[0] += 0.1
            self.state[1] -= 0.05
            self.state[2] -= 0.05
        elif action.action_type == "ERROR":
            self.state[1] += 0.1
            self.state[2] += 0.1
        self.state = np.clip(self.state, 0, 1)
        return {
            "mastery": float(self.state[0]),
            "strain": float(self.state[1]),
            "load": float(self.state[2]),
        }
