"""Telemetry export.

Administrative dump endpoints for the durable telemetry table.
Gated to admin-only callers via ADMIN_ACCOUNT_IDS env var.
"""

import csv
import io
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.deps import get_current_account
from backend.core.config import settings
from backend.core.database import get_db
from backend.models.accounts import Account
from backend.models.telemetry import TelemetryEvent

_ADMIN_IDS = frozenset(
    uuid.UUID(h.strip())
    for h in (settings.ADMIN_ACCOUNT_IDS or "").split(",")
    if h.strip()
)


def _require_admin(account: Account = Depends(get_current_account)) -> Account:
    if not _ADMIN_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ADMIN_ACCOUNT_IDS is not configured.",
        )
    if account.id not in _ADMIN_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return account


router = APIRouter()


# Sprint 28-C.2: explicit Pydantic model replaces sa_inspect reflection.
class TelemetryEventOut(BaseModel):
    id: int
    time: datetime
    event: str
    metadata: Dict[str, Any]
    request_path: str | None = None
    stability: float | None = None
    selected_state_id: str | None = None
    decision_reason: str | None = None
    max_complexity: int | None = None

    @classmethod
    def from_orm(cls, event: TelemetryEvent) -> "TelemetryEventOut":
        meta = event.event_metadata
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except (TypeError, ValueError):
                meta = {}
        return cls(
            id=event.id,
            time=event.time,
            event=event.event,
            metadata=meta or {},
            request_path=event.request_path,
            stability=event.stability,
            selected_state_id=event.selected_state_id,
            decision_reason=event.decision_reason,
            max_complexity=event.max_complexity,
        )


def _event_to_dict(event: TelemetryEvent) -> Dict[str, Any]:
    return TelemetryEventOut.from_orm(event).model_dump(mode="json")


@router.get("/export", dependencies=[Depends(_require_admin)])
def export_telemetry_json(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return all telemetry events as JSON."""
    events: List[TelemetryEvent] = list(db.execute(select(TelemetryEvent)).scalars())
    return {"count": len(events), "events": [_event_to_dict(e) for e in events]}


@router.get("/export.csv", dependencies=[Depends(_require_admin)])
def export_telemetry_csv(db: Session = Depends(get_db)) -> StreamingResponse:
    """Return all telemetry events as CSV."""
    events: List[TelemetryEvent] = list(db.execute(select(TelemetryEvent)).scalars())

    fieldnames: List[str] = []
    rows: List[Dict[str, Any]] = []
    for e in events:
        d = _event_to_dict(e)
        rows.append(d)
        for k in d.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        # Serialize dict / list payloads as compact JSON strings for CSV-safety.
        flat = {
            k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
            for k, v in r.items()
        }
        writer.writerow(flat)

    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=telemetry_export.csv"},
    )


# ---- S25.6: retrieval-choice rollup -----------------------------------------
#
# Editorial-review aggregation over the existing `curriculum.retrieval_choice`
# events. The endpoint does NOT introduce a new event type or schema; it
# simply summarizes the JSON metadata that has been recorded since the
# retrieval-page rollout. A low per-unit accuracy is a signal that either:
#   - the retrieval prompt itself is unclear, or
#   - the principle page didn't make the right answer obvious.
#
# Scoped to free-track modules (1-3): the body schema for the
# /retrieval-choice endpoint already enforces module in [1, 3], so paid
# modules cannot leak into the rollup.


@router.get("/rollup")
def retrieval_rollup(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Per-unit and per-module retrieval-choice accuracy.

    Walks `curriculum.retrieval_choice` events (one row per learner
    selection on a retrieval page) and returns:

      {
        "total_choices": <int>,
        "by_module":  [{ "module": 1|2|3, "attempts", "correct", "accuracy" }, ...],
        "by_unit":    [{ "module", "unit_id", "attempts", "correct", "accuracy" }, ...],
      }

    `accuracy` is `correct / attempts` rounded to 3 decimals; units
    with zero attempts are omitted (they cannot have an accuracy).
    """
    events: List[TelemetryEvent] = list(
        db.execute(
            select(TelemetryEvent).where(
                TelemetryEvent.event == "curriculum.retrieval_choice"
            )
        ).scalars()
    )

    # Aggregate. Key: (module, unit_id) for per-unit; module for per-module.
    unit_attempts: Dict[tuple, int] = {}
    unit_correct: Dict[tuple, int] = {}
    module_attempts: Dict[int, int] = {}
    module_correct: Dict[int, int] = {}

    for e in events:
        meta = e.event_metadata or {}
        if isinstance(meta, str):
            # Defensive: some drivers persist JSON columns as text.
            try:
                meta = json.loads(meta)
            except (TypeError, ValueError):
                continue
        module = meta.get("module")
        unit_id = meta.get("unit_id")
        correct = bool(meta.get("correct"))
        if not isinstance(module, int) or not isinstance(unit_id, str):
            continue

        key = (module, unit_id)
        unit_attempts[key] = unit_attempts.get(key, 0) + 1
        unit_correct[key] = unit_correct.get(key, 0) + (1 if correct else 0)
        module_attempts[module] = module_attempts.get(module, 0) + 1
        module_correct[module] = module_correct.get(module, 0) + (1 if correct else 0)

    def _accuracy(correct: int, attempts: int) -> float:
        return round(correct / attempts, 3) if attempts > 0 else 0.0

    by_module = [
        {
            "module": m,
            "attempts": module_attempts[m],
            "correct": module_correct[m],
            "accuracy": _accuracy(module_correct[m], module_attempts[m]),
        }
        for m in sorted(module_attempts.keys())
    ]

    by_unit = [
        {
            "module": k[0],
            "unit_id": k[1],
            "attempts": unit_attempts[k],
            "correct": unit_correct[k],
            "accuracy": _accuracy(unit_correct[k], unit_attempts[k]),
        }
        for k in sorted(unit_attempts.keys())
    ]

    return {
        "total_choices": len(events),
        "by_module": by_module,
        "by_unit": by_unit,
    }
