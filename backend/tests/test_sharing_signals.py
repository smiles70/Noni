"""Synthetic signature test: does the detector separate shared vs solo?"""
from datetime import datetime, timedelta, timezone

from backend.services.sharing_signals import detect_sharing


def _row(status="completed", days_ago=0, pre=None, post=None):
    class R:
        pass
    r = R()
    r.status = status
    r.completed_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    r.confidence_pre = pre
    r.confidence_post = post
    return r


def test_solo_learner_does_not_flag():
    rows = [_row(days_ago=40 - i * 5, pre=2, post=4) for i in range(8)]
    assert detect_sharing(rows)["flag"] is False


def test_shared_account_flags_on_oscillation_and_velocity():
    # two hands alternating: A confident (4-5), B not (1-2), fast pace
    rows = []
    for i in range(10):
        hi = i % 2 == 0
        rows.append(_row(days_ago=i // 3, post=5 if hi else 1))
    res = detect_sharing(rows)
    assert res["flag"] is True
    assert res["reasons"]


def test_few_confidence_points_do_not_flag():
    rows = [_row(days_ago=i * 7, post=5 if i % 2 else 1) for i in range(4)]
    assert detect_sharing(rows)["flag"] is False


def test_deterministic_same_input_same_output():
    rows = [_row(days_ago=i, post=(i % 5) + 1) for i in range(12)]
    assert detect_sharing(rows) == detect_sharing(rows)
