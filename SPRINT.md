# Sprint 10: Telemetry Signal Richness (CLOSED)

Tag: `sprint-10-telemetry-richness-v1`. Promotes ISCS decision variables to dedicated audit columns and wires the curriculum routes to record every decision.

## Phases

- 10.1 Retroactively populate the empty baseline migration with `telemetry_events` table creation (fresh DBs / CI now actually get the schema)
- 10.2 New migration `b2c3_telem_rich`: add 5 nullable audit columns
- 10.3 Extend `TelemetryEvent` model and `telemetry.record(...)` signature
- 10.4 Wire `/api/curriculum/what-is-ai`, `/units/{id}`, `/next-unit` to record `iscs_decision` / `iscs_recommendation` events with audit fields
- 10.5 New test file `test_telemetry_richness.py` (4 tests including CSV header check)
- 10.6 ADR 0009: rationale (defensibility, queryability)
- 10.7 Closeout

## Out of scope

- PII fields (user_id, session_id) - block on auth vendor selection
- Index / partitioning strategy at scale
- Time-series rollups
