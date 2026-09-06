"""Telemetry Celery tasks (E70-B2).

Moves the per-request `telemetry_events` INSERT off the web worker's
request path. Durability is preserved: the task performs the same
synchronous write `record()` used to, just on a worker instead of
inside a request. Retry on transient failure; events are idempotent
via the caller-supplied dedup key when provided.
"""

from backend.tasks.celery_app import app


@app.task(bind=True, max_retries=3, default_retry_delay=5)
def record_telemetry_event(
    self,
    event_type: str,
    metadata: dict | None = None,
    request_path: str | None = None,
    stability: float | None = None,
    selected_state_id: str | None = None,
    decision_reason: str | None = None,
    max_complexity: int | None = None,
) -> str:
    from backend.services.telemetry import _record_sync

    try:
        ev = _record_sync(
            event_type,
            metadata,
            request_path=request_path,
            stability=stability,
            selected_state_id=selected_state_id,
            decision_reason=decision_reason,
            max_complexity=max_complexity,
        )
        return str(ev.get("id"))
    except Exception as exc:
        raise self.retry(exc=exc)
