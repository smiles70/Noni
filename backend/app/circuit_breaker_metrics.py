"""Shared Prometheus metrics for circuit breaker state transitions.

Prevents "Duplicated timeseries in CollectorRegistry" when multiple
modules import circuit breaker listeners in the same process.
"""

from __future__ import annotations

from prometheus_client import Counter

_circuit_state_transitions = Counter(
    "noni_circuit_breaker_state_transitions_total",
    "Circuit breaker state transitions",
    ["service", "from_state", "to_state"],
)


def record_circuit_transition(service: str, from_state: str, to_state: str) -> None:
    _circuit_state_transitions.labels(
        service=service,
        from_state=from_state,
        to_state=to_state,
    ).inc()
