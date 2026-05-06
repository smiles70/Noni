"""ISCS - Stability metric."""

import numpy as np


def compute_stability(cov) -> float:
    return float(max(np.linalg.eigvals(cov)).real)
