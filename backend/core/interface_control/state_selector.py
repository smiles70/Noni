"""ISCS - State selector. Sole UI complexity decision point."""

from typing import Dict, List


def select_ui_state(
    candidates: List[Dict], stability: float, threshold: float = 1.0
) -> Dict:
    max_complexity = max(1, int(3 - stability))
    safe = [c for c in candidates if c["complexity"] <= max_complexity]
    return safe[0] if safe else candidates[0]
