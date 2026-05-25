"""Stage 1 telemetry — Prometheus-based observability.



Sprint 22 S2: migrated from in-memory defaultdict counters to

prometheus_client Counter + Histogram. Metrics are exposed on

`/metrics` for scraping by Grafana / Fly Metrics.

"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Awaitable, Callable

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("noni.telemetry")


# ---------------------------------------------------------------------------

# Prometheus metrics

# ---------------------------------------------------------------------------


_auth_session_outcomes = Counter(
    "noni_auth_session_outcomes_total",
    "Outcome counts for /auth/session* responses",
    ["code"],
)


_account_materialize_attempts = Counter(
    "noni_account_materialize_attempts_total",
    "Result counts for AccountMaterializer materialize() calls",
    ["result"],
)


_email_collisions = Counter(
    "noni_email_collision_observed_total",
    "Count of observed email collisions during materialization",
)


_auth_latency = Histogram(
    "noni_auth_session_latency_seconds",
    "Latency of /auth/session* responses",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


_request_latency = Histogram(
    "noni_request_latency_seconds",
    "HTTP request latency by path",
    ["path", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


# ---------------------------------------------------------------------------

# Public recording helpers — call these from routes/services.

# ---------------------------------------------------------------------------


def record_auth_session_outcome(code: str, latency_ms: int | None = None) -> None:
    """Record one /auth/session* outcome by discriminated reason code (B5)."""

    _auth_session_outcomes.labels(code=code).inc()

    if latency_ms is not None:

        _auth_latency.observe(latency_ms / 1000.0)

    logger.info("auth.session.outcome", extra={"code": code, "latency_ms": latency_ms})


def record_materialize_attempt(result: str) -> None:
    """Record one AccountMaterializer attempt."""

    _account_materialize_attempts.labels(result=result).inc()

    logger.info("account.materialize.attempt", extra={"result": result})


def record_email_collision() -> None:
    """Record one observed email collision during materialization (B8)."""

    _email_collisions.inc()

    logger.warning("account.email_collision_observed")


def snapshot() -> dict[str, dict[str, int] | list[int]]:
    """Return a point-in-time snapshot of all counters (for /metrics + tests)."""

    return {
        "auth_session_outcomes_total": {
            s.labels["code"]: s.value
            for s in _auth_session_outcomes.collect()[0].samples
        },
        "account_materialize_attempts_total": {
            s.labels["result"]: s.value
            for s in _account_materialize_attempts.collect()[0].samples
        },
        "email_collision_observed_total": {
            "count": sum(s.value for s in _email_collisions.collect()[0].samples),
        },
        "auth_session_latency_ms_recent": [],
    }


def reset_for_tests() -> None:
    """Test-only: Prometheus counters are cumulative; tests should assert on delta."""

    pass


# ---------------------------------------------------------------------------

# Middleware — latency + status observation per request.

# ---------------------------------------------------------------------------


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Records per-request latency and status for observability.



    Never reads headers or bodies. Specific business outcomes are emitted

    by route handlers via `record_auth_session_outcome`.

    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:

        start = time.perf_counter()

        response = await call_next(request)

        duration_sec = time.perf_counter() - start

        path = request.url.path

        status = str(response.status_code)

        request_id = getattr(request.state, "request_id", None)

        logger.info(
            "request.complete",
            extra={
                "path": path,
                "status": status,
                "latency_ms": int(duration_sec * 1000),
                "request_id": request_id,
            },
        )

        _request_latency.labels(path=path, status=status).observe(duration_sec)

        if path.startswith("/auth/session"):

            _auth_latency.observe(duration_sec)

        return response


# ---------------------------------------------------------------------------

# Metrics endpoint handler (mounted in main.py)

# ---------------------------------------------------------------------------


def metrics_handler() -> Response:
    """Return Prometheus exposition format for scraping."""

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ---------------------------------------------------------------------------
# Sprint 22 S4: structured JSON logging setup
# ---------------------------------------------------------------------------


def _setup_json_logging() -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(path)s %(status)s %(latency_ms)s",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp",
        },
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


_setup_json_logging()


# ---------------------------------------------------------------------------
# Sprint 22 S3: Request ID tracing middleware
# ---------------------------------------------------------------------------


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Accept or generate X-Request-ID and echo it back on responses.

    Stores the ID in request.state.request_id so downstream handlers
    and the TelemetryMiddleware can include it in logs.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id")
        if not request_id:
            request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
