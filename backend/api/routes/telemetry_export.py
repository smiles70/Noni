"""Telemetry export.

Provides administrative dump endpoints for the durable telemetry table.

Authentication is intentionally NOT enforced here. This is acceptable
in development. When auth lands (deferred vendor pass), this router
must be gated to admin-only callers. See `docs/deferred-decisions.md`.
"""

import csv
import io
import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.telemetry import TelemetryEvent

router = APIRouter()


def _event_to_dict(event: TelemetryEvent) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for col in sa_inspect(event).mapper.column_attrs:
        v = getattr(event, col.key)
        if hasattr(v, "isoformat"):
            v = v.isoformat()
        out[col.key] = v
    return out


@router.get("/export")
def export_telemetry_json(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return all telemetry events as JSON."""
    events: List[TelemetryEvent] = list(db.execute(select(TelemetryEvent)).scalars())
    return {"count": len(events), "events": [_event_to_dict(e) for e in events]}


@router.get("/export.csv")
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
