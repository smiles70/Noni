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
