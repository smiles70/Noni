"""Admin telemetry summary endpoint.

Sprint '2nd Safe Yellow' P22: exposes telemetry snapshot in a
human-readable JSON shape (complement to /metrics Prometheus format).

TODO: add admin-auth gate once admin role system is implemented.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.telemetry import snapshot

router = APIRouter(prefix="/admin/telemetry")


@router.get("/summary")
def telemetry_summary() -> dict:
    """Return a point-in-time snapshot of internal telemetry counters.

    This is a JSON view of the same data exposed on /metrics in
    Prometheus exposition format. Useful for quick health checks
    without a Prometheus scraper.
    """
    return snapshot()
