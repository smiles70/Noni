# 0009 - Rich audit telemetry: promote ISCS decision variables to columns

## Status

Accepted (Sprint 10).

## Context

Sprint 6 added telemetry persistence and CSV/JSON export. The schema then was minimal: `id`, `time`, `event`, and a free-form `metadata` JSON column. That shape is acceptable for ad-hoc product debugging but is a poor audit-trail substrate for two reasons:

1. **Defensibility / patentability.** Noni's claim of being a backend-governed, ISCS-driven learning system rests on showing that every UI-state decision is grounded in measurable variables. If those variables live only inside an opaque JSON blob, an external auditor (or a patent examiner reviewing prior art) cannot confirm at a glance that the system actually behaves as claimed.
2. **Queryability.** Filtering on `metadata->>'stability'` requires Postgres-specific JSON operators and resists indexing on most hosts. SQL queries in dashboards and reports become awkward.

The decision variables that uniquely characterize an ISCS decision are:
- the request path the decision was made for,
- the stability metric at decision time,
- the id of the selected UI state,
- the human-readable reason the selector returned (`approved`, `linear-walk`, etc.),
- the complexity ceiling that was in effect.

## Decision

Promote those five fields to **dedicated nullable columns** on `telemetry_events`:

| Column | Type | Notes |
|---|---|---|
| `request_path` | `String(128)` | The API path that produced the decision |
| `stability` | `Float` | The ISCS stability metric at decision time |
| `selected_state_id` | `String(128)` | The id of the candidate the selector chose |
| `decision_reason` | `String(64)` | Selector verdict (`approved`, `linear-walk`, future: `fallback_simpler`, etc.) |
| `max_complexity` | `Integer` | The complexity ceiling in force when the decision was made |

The free-form `metadata` JSON column is retained for non-audit context (candidate id lists, unit ids, etc.). It is no longer the primary audit substrate.

The columns are nullable because non-decision events (signals, generic telemetry) do not produce these fields.

## Consequences

- Every ISCS-gated endpoint must call `telemetry.record(...)` with the audit kwargs at the decision point. Sprint 10 wires `/api/curriculum/what-is-ai`, `/api/curriculum/units/{id}`, and `/api/curriculum/next-unit`. New ISCS-gated endpoints must do the same; this is enforced by review.
- The CSV export shape is now wider (5 new columns); downstream consumers should treat unknown columns as additive, not breaking.
- Migration `b2c3_telem_rich` adds the columns; the previously-empty baseline migration was retroactively populated so fresh databases (CI) get the table at all.
- Per-row storage cost grows by ~24 bytes; negligible at expected volumes. If volume becomes a concern, partition or roll up older rows.
- Future PII fields (user_id, session_id) belong in their own ADR after the auth vendor decision lands. They are deliberately not included here.
