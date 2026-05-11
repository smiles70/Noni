"""Telemetry retention policy.

Default `expires_at` per event type. See ADR 0024.

Application sets `expires_at` at insert time; the pg_cron sweep job
defined in `supabase/migrations/0002_pg_cron_retention.sql` deletes
expired rows nightly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Retention in days, per event_type prefix.
# Match by exact event_type first; fall back to longest prefix match;
# fall back to DEFAULT_RETENTION_DAYS.
RETENTION_DAYS: dict[str, int] = {
    "iscs_decision": 90,
    "iscs_recommendation": 90,
    "envelope_served": 30,
    "unit_view": 90,
    "purchase_": 365,  # prefix match catches purchase_initiated/completed/refunded
    "auth_": 30,  # auth_signin, auth_signout, etc.
    "gift_": 365,
    "deletion_": 730,  # legally important; keep ~2y
}

DEFAULT_RETENTION_DAYS = 90


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def expires_at_for(event_type: str, *, now: datetime | None = None) -> datetime:
    """Return the default `expires_at` for a given event_type."""
    now = now or _utcnow()
    days = RETENTION_DAYS.get(event_type)
    if days is None:
        # Longest prefix match.
        best: int | None = None
        best_len = -1
        for prefix, d in RETENTION_DAYS.items():
            if (
                prefix.endswith("_")
                and event_type.startswith(prefix)
                and len(prefix) > best_len
            ):
                best = d
                best_len = len(prefix)
        days = best if best is not None else DEFAULT_RETENTION_DAYS
    return now + timedelta(days=days)
