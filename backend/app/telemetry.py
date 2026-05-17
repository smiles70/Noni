"""Stage 0 telemetry — E10 observability gate.

Source: docs/design/login-execution-playbook-2026-05-17.md (Section 2A).
Tag boundary: must be in place BEFORE Stage 1 (M1 migration) ships;
Stage 2 auth-redesign code MUST NOT land until staging dashboards show
these counters populating.

Constraints anchored:
  - B5  discriminated 401 outcomes are emitted per response
  - B10 no credential leakage in logs (we never read/print headers)
  - E10 telemetry signals exist before redesign can be measured
  - I-A / I-H observable transient-vs-definitive failure classes
  - I-G observable FE/BE auth-state disagreement (FE-emitted)

Design decisions:
  - In-memory counters today; the public API (`record_*`) is stable so
    a Prometheus exporter can be swapped in without touching call sites.
  - Routes emit auth outcomes explicitly via `record_auth_session_outcome`
    (not by middleware response-body sniffing, which is fragile for
    streaming responses and risks reading sensitive payloads).
  - The middleware adds latency + status observation per path; that is
    all it does. It NEVER reads request/response headers.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from threading import Lock
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("noni.telemetry")
# Ensure Stage 0 telemetry log lines are visible under uvicorn's default
# log config. Uvicorn does not configure root, so we attach our own
# StreamHandler at INFO and disable propagation so the line lands on
# stderr exactly once.
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            "%(levelname)s:%(name)s:%(message)s "
            "path=%(path)s status=%(status)s latency_ms=%(latency_ms)s",
            defaults={"path": "-", "status": "-", "latency_ms": "-"},
        )
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

# ---------------------------------------------------------------------------
# Counters (in-memory placeholders; replace with Prometheus client later).
# Keys are intentionally simple strings; structure them as dot-namespaces.
# ---------------------------------------------------------------------------

_lock = Lock()

auth_session_outcomes_total: dict[str, int] = defaultdict(int)
"""Outcome counts for /auth/session and /auth/session/init responses.

Key = discriminated reason code, e.g.:
  - "ok.materialized", "ok.unmaterialized"
  - "auth.no_credential", "auth.malformed",
    "auth.signature_invalid", "auth.expired",
    "auth.issuer_mismatch", "auth.subject_missing",
    "auth.account_deleted",
    "auth.transient_verifier_unavailable",
    "auth.transient_db_unavailable"
"""

account_materialize_attempts_total: dict[str, int] = defaultdict(int)
"""Result counts for AccountMaterializer.materialize() calls.

Key in {"success", "conflict", "deleted"}.
"""

email_collision_observed_total: dict[str, int] = defaultdict(int)
"""Count of observed email collisions during materialization.

Single key "count"; kept as a dict for symmetry / future labels.
"""

auth_session_latency_ms: list[int] = []
"""Coarse latency log for /auth/session* responses.

Bounded to the most recent 1024 samples to avoid unbounded growth.
Swap for a real histogram before production.
"""

_LATENCY_RING_SIZE = 1024


# ---------------------------------------------------------------------------
# Public recording helpers — call these from routes/services.
# ---------------------------------------------------------------------------


def record_auth_session_outcome(code: str, latency_ms: int | None = None) -> None:
    """Record one /auth/session* outcome by discriminated reason code (B5).

    Call from auth-session route handlers, including success paths.
    """
    with _lock:
        auth_session_outcomes_total[code] += 1
        if latency_ms is not None:
            auth_session_latency_ms.append(latency_ms)
            if len(auth_session_latency_ms) > _LATENCY_RING_SIZE:
                # Drop oldest; keep the ring bounded.
                del auth_session_latency_ms[
                    : len(auth_session_latency_ms) - _LATENCY_RING_SIZE
                ]
    logger.info("auth.session.outcome", extra={"code": code, "latency_ms": latency_ms})


def record_materialize_attempt(result: str) -> None:
    """Record one AccountMaterializer attempt.

    `result` is one of: "success", "conflict", "deleted".
    """
    with _lock:
        account_materialize_attempts_total[result] += 1
    logger.info("account.materialize.attempt", extra={"result": result})


def record_email_collision() -> None:
    """Record one observed email collision during materialization (B8)."""
    with _lock:
        email_collision_observed_total["count"] += 1
    logger.warning("account.email_collision_observed")


def snapshot() -> dict[str, dict[str, int] | list[int]]:
    """Return a point-in-time snapshot of all counters (for /metrics + tests)."""
    with _lock:
        return {
            "auth_session_outcomes_total": dict(auth_session_outcomes_total),
            "account_materialize_attempts_total": dict(
                account_materialize_attempts_total
            ),
            "email_collision_observed_total": dict(email_collision_observed_total),
            "auth_session_latency_ms_recent": list(auth_session_latency_ms),
        }


def reset_for_tests() -> None:
    """Test-only: clear all counters. Production code must never call this."""
    with _lock:
        auth_session_outcomes_total.clear()
        account_materialize_attempts_total.clear()
        email_collision_observed_total.clear()
        auth_session_latency_ms.clear()


# ---------------------------------------------------------------------------
# Middleware — latency + status observation per request.
#
# Deliberately does NOT read request/response headers or bodies (B10).
# ---------------------------------------------------------------------------


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Records per-request latency and status for observability.

    Never reads headers or bodies. Specific business outcomes (e.g.
    discriminated 401 reason codes) are emitted by route handlers via
    `record_auth_session_outcome` so that the wire-format reason is the
    source of truth, not a guess from middleware.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)

        path = request.url.path
        status = response.status_code

        # Path/status only. No headers, no body, no query-string echo.
        logger.info(
            "request.complete",
            extra={"path": path, "status": status, "latency_ms": duration_ms},
        )

        # Best-effort latency capture for the auth-session family.
        # The exact outcome code is emitted by the route, not here.
        if path.startswith("/auth/session"):
            with _lock:
                auth_session_latency_ms.append(duration_ms)
                if len(auth_session_latency_ms) > _LATENCY_RING_SIZE:
                    del auth_session_latency_ms[
                        : len(auth_session_latency_ms) - _LATENCY_RING_SIZE
                    ]

        return response
