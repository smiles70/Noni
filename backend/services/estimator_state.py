"""Persistent estimator state per (account, scope).

Closes the architect-review P0 (ADR 0024): the ISCS estimator's covariance
and last-stability state must survive process restarts.

Encoding: pickle-protocol-5 bytes for portability with the existing
`InterfaceStateEstimator`. Future migrations can switch to a structured
format (e.g. msgpack) without changing this service surface — only the
private codec helpers change.
"""

from __future__ import annotations

import pickle
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session as DbSession

from backend.models.learning import EstimatorState

DEFAULT_SCOPE = "global"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_state(
    db: DbSession,
    account_id: uuid.UUID,
    *,
    scope: str = DEFAULT_SCOPE,
) -> Optional[Any]:
    """Return the deserialized estimator state, or None if absent."""
    row = (
        db.query(EstimatorState)
        .filter(
            EstimatorState.account_id == account_id,
            EstimatorState.scope == scope,
        )
        .one_or_none()
    )
    if row is None:
        return None
    try:
        return pickle.loads(row.state_blob)
    except (pickle.UnpicklingError, EOFError, AttributeError):
        # Corrupted blob: fail closed (caller will treat as missing).
        return None


def save_state(
    db: DbSession,
    account_id: uuid.UUID,
    state: Any,
    *,
    scope: str = DEFAULT_SCOPE,
    last_stability: Optional[float] = None,
) -> None:
    """Upsert estimator state. Caller is responsible for commit."""
    blob = pickle.dumps(state, protocol=5)
    row = (
        db.query(EstimatorState)
        .filter(
            EstimatorState.account_id == account_id,
            EstimatorState.scope == scope,
        )
        .one_or_none()
    )
    if row is None:
        row = EstimatorState(
            account_id=account_id,
            scope=scope,
            state_blob=blob,
            last_stability=(
                Decimal(str(last_stability)) if last_stability is not None else None
            ),
        )
        db.add(row)
    else:
        row.state_blob = blob
        if last_stability is not None:
            row.last_stability = Decimal(str(last_stability))
        row.updated_at = _utcnow()
    db.flush()


def get_last_stability(
    db: DbSession,
    account_id: uuid.UUID,
    *,
    scope: str = DEFAULT_SCOPE,
) -> Optional[float]:
    row = (
        db.query(EstimatorState.last_stability)
        .filter(
            EstimatorState.account_id == account_id,
            EstimatorState.scope == scope,
        )
        .one_or_none()
    )
    if row is None or row[0] is None:
        return None
    return float(row[0])
