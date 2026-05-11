# Sprint 20: TelemetryGatedUnit Refactor (CLOSED)

Tag: `sprint-20-telemetry-gated-unit-v1`. Eliminates 3-way duplication of `Module2Unit` / `Module3Unit` / `Module4Unit` by extracting a shared `TelemetryGatedUnit` base into the canonical model file.

## Phases

- 20.1 `TelemetryGatedUnit` added to `backend/models/curriculum_units.py`
- 20.2 Module 2/3/4 files reduced to one-line alias
- 20.3 79/79 tests still pass (no behavior change)
- 20.4 ADR 0018
- 20.5 Closeout

Triggered by ADR 0017: *"If a 5th module is proposed, the refactor lands first."*
