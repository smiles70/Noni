# 0018 - Extract `TelemetryGatedUnit` as the shared base for Modules 2-4+

## Status

Accepted (Sprint 20).

## Context

After ADRs 0015 / 0016 / 0017 landed Modules 2, 3, and 4 in successive sprints, three classes (`Module2Unit`, `Module3Unit`, `Module4Unit`) all carried the identical single-field extension to `CurriculumUnit`: a `telemetry_requirements: Dict[str, float]` field with `default_factory=dict`.

ADR 0016 deferred the refactor with: *"A shared `TelemetryGatedUnit` base could collapse them, but is deliberately deferred until a Module 4 lands."* ADR 0017 confirmed the trigger: *"If a 5th module is proposed, the refactor lands first."*

Three identical duplicates is the conventional threshold at which DRY wins. Module 5 is anticipated, so the refactor lands now, before the next content drop-in.

## Decision

- `TelemetryGatedUnit(CurriculumUnit)` is defined once in the canonical `backend/models/curriculum_units.py`, with the shared `telemetry_requirements` field.
- Each module file replaces its local subclass with a one-line alias: `ModuleNUnit = TelemetryGatedUnit`. The alias is kept for readability of the unit lists.
- Tests unchanged; 79/79 passing both before and after.
- Future telemetry-gated modules import `TelemetryGatedUnit` directly. No new subclass needed.

## Consequences

- The single-field duplication that grew from 1 to 3 copies is gone.
- Adding Module 5 (or N) is one import + one alias + one `UNITS_MODULE_N` list.
- If a future module needs *additional* fields beyond `telemetry_requirements`, it gets its own subclass (named, with an ADR explaining the extension). The base stays narrow.
- The architectural contract (no request-body signals, audit-logged decisions, per-learner enforcement deferred) is preserved verbatim across all modules.
