"""Shared-account detection — passive signal, never a verdict.

Reads Progress rows (velocity + confidence oscillation) and returns a
flag for human outreach. No device fingerprinting, no session data —
deliberately weaker-but-dignified signals consistent with our privacy
posture. Output feeds org_audit_log + support email only; it never
blocks or restricts an account.

Signature theory (validated by synthetic test):
  - One learner: confidence_post tracks upward or holds steady;
    completion pace is days-per-unit for this audience.
  - Two+ learners sharing: confidence oscillates (different people
    start from different baselines) and pace can exceed any single
    55+ learner's plausible rate.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

VELOCITY_FLAG = 5          # completions/day — beyond plausible solo pace
OSCILLATION_MIN_ROWS = 6   # need this many confidence points to judge
OSCILLATION_FLAG = 1.5     # stdev of post scores above this = mixed hands


def detect_sharing(rows: list, now: datetime | None = None) -> dict:
    """rows: Progress-like objects with status, completed_at, confidence_*.
    Returns {"flag": bool, "reasons": [...]}. Read-only."""
    now = now or datetime.now(timezone.utc)
    reasons = []

    completed = [r for r in rows if getattr(r, "status", None) == "completed" and getattr(r, "completed_at", None)]
    if len(completed) >= VELOCITY_FLAG * 2:
        completed.sort(key=lambda r: r.completed_at)
        span = max((completed[-1].completed_at - completed[0].completed_at), timedelta(hours=1))
        per_day = len(completed) / (span.days or 1)
        if per_day >= VELOCITY_FLAG:
            reasons.append(f"velocity:{round(per_day,1)}/day")

    posts = [r.confidence_post for r in rows if getattr(r, "confidence_post", None) is not None]
    if len(posts) >= OSCILLATION_MIN_ROWS:
        mean = sum(posts) / len(posts)
        var = sum((p - mean) ** 2 for p in posts) / len(posts)
        sd = var ** 0.5
        # alternating pattern check: count sign flips in successive deltas
        diffs = [posts[i + 1] - posts[i] for i in range(len(posts) - 1)]
        flips = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i - 1] < 0)
        if sd >= OSCILLATION_FLAG or flips >= len(diffs) * 0.6:
            reasons.append(f"confidence_oscillation:sd={round(sd,2)},flips={flips}")

    return {"flag": bool(reasons), "reasons": reasons}
