---
name: app-error-patterns
description: >-
  Run when implementing error handling in backend services (FastAPI,
  SQLAlchemy, Celery) or frontend API/component code (React, TypeScript).
  Covers exception hierarchies aligned to the Noni error envelope,
  retry/backoff, circuit breaking, Result types, and graceful
  degradation. For CI gate failures (ruff, Trivy, Playwright) use the
  error-taxonomy skill instead — that is a different problem.
---

# Application error-handling patterns (Noni)

How errors should be shaped, propagated, and recovered in this codebase.

## The contract that already exists — do not break it

Two wire shapes are load-bearing and covered by tests:

- **Auth envelope**: `{error: {code, message}}`. `AuthProvider` reads
  `data.error.code` directly. Enforced by the `HTTPException` handler at
  `backend/app/main.py` (`_http_exception_handler`), which unwraps
  `detail` only when it is exactly `{"error": ...}`.
- **UI envelope**: `{detail: {envelope_id: ...}}` — FastAPI's default
  shape, read by `frontend/src/api/curriculum.ts`. Preserve it.

Any new error surface must pick one of these shapes deliberately. Do not
invent a third.

## Backend (FastAPI + SQLAlchemy + Celery)

### Exception hierarchy

Current service exceptions are flat (`AuthError`, `GiftClaimError`,
`WebhookVerificationError` in `backend/services/`). When adding a new
failure mode, subclass a base that carries a machine-readable code and
structured details so the HTTPException handler can emit the envelope:

```python
class NoniError(Exception):
    """Base for application errors. `code` maps to the wire envelope."""

    def __init__(self, message: str, code: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class NotFoundError(NoniError):
    pass
```

At the route boundary, translate to `HTTPException` with the envelope —
never let a raw service exception become a shapeless 500.

### Retry with exponential backoff

Celery tasks already retry (`backend/tasks/*_tasks.py`); use the task
queue's retry machinery rather than hand-rolled decorators where a task
boundary exists. For a plain function retry, preserve context and add
jitter — do not copy naive examples that re-raise `last_exception`
without tracebacks:

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(
    func: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 1.0,
    retryable: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Retry `func` with exponential backoff + jitter. Raises the last
    error with its traceback intact after `attempts` tries."""
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except retryable:
            if attempt == attempts:
                raise  # traceback preserved
            time.sleep(base_delay * 2 ** (attempt - 1) + random.random())
    raise AssertionError("unreachable")
```

Retry only transient failures (timeouts, 5xx, connection resets). Never
retry 4xx or validation errors.

### Circuit breaker

The repo has `backend/app/circuit_breaker_metrics.py` — extend that
implementation rather than adding a second one. If you add state to it,
guard it: unsynchronised mutable counters race under gunicorn workers.

## Frontend (React + TypeScript)

### Current convention: try/catch + envelope codes

`src/api/client.ts` catches, maps envelope codes, and retries where
safe. Components render `ErrorBoundary` (`src/components/ErrorBoundary.tsx`,
`OnboardingErrorBoundary.tsx`) as the UI backstop. Follow this
convention; do not mix in a parallel error model without an intake.

### Custom error classes

When a thrown error needs a machine-readable identity:

```typescript
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
```

### Result type (opt-in, needs an intake before adoption)

A `Result<T, E>` union suits expected-failure paths (validation, parse):

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });
```

Do not mix Result and exceptions in the same call path — pick one per
boundary. Migrating `api/client.ts` to Result returns is a convention
change; open an intake first.

## Graceful degradation — the safe shape

Fallbacks are correct for *availability*, not for hiding faults. Rules:

- Distinguish "no value" from "value happened to be falsy" — return a
  discriminated result, never `null`-or-value from a try/catch helper.
- Log the primary failure before falling back (one log, at the right
  level — do not log-then-rethrow and double-log).
- A fallback that is itself a network call needs its own timeout.

```typescript
async function withFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>,
  onError: (e: unknown) => void,
): Promise<T> {
  try {
    return await primary();
  } catch (e) {
    onError(e);
    return fallback();
  }
}
```

## Pitfalls enforced here

- No bare `except:` / `catch {}` that discards the error.
- No swallow-and-continue on unexpected errors; expected failures get a
  typed path, unexpected ones propagate to the boundary.
- `finally`/context managers own cleanup (`db.session`, file handles,
  `page` fixtures).
- Catch at the layer that can act: services raise typed errors, routes
  translate to envelopes, UI boundaries render fallback UI.
- Error messages say what happened and what to do next — never "error
  occurred".

## Related

- `.devin/skills/error-taxonomy/SKILL.md` — CI gate failure classes and
  their remediation playbooks (ruff, Trivy, Playwright, migrations).
- `backend/app/main.py` — `_http_exception_handler`, the envelope
  enforcement point.
- `backend/app/circuit_breaker_metrics.py` — repo circuit breaker.
