"""Telemetry service. In-memory scaffolding; needs durable store for prod."""
from datetime import datetime, timezone
from typing import List, Dict

telemetry_log: List[Dict] = []

def record(event_type: str, metadata: dict) -> dict:
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "metadata": metadata,
    }
    telemetry_log.append(entry)
    return entry
