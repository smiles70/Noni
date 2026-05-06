# Sprint 2: Curriculum Expansion (CLOSED)

Goal: ship Units 2-4 of the geragogy curriculum, routed through the canonical ISCS.
Honors all rules from Sprints 1 (Initial Scaffolding) and 1b (Progress Closeout).

## Phases

- 2.1 `CurriculumUnit` model (structured `CurriculumPage` pages, no client-supplied signals)
- 2.2 Extend `/api/curriculum` router with `/units`, `/units/{id}`, `/next-unit`
  - All selection routed through existing `select_ui_state()` and module-level `InterfaceStateEstimator`
- 2.3 Tests for unit data integrity, per-unit selection, and `/next-unit` contract
- 2.4 Closeout: README, PROGRESS, commit, tag `sprint-2-curriculum-v1`

## Out of Scope (deferred)

- Per-learner state / cursor (requires Auth sprint)
- Frontend UI for unit navigation (requires design system sprint)
- Real Claude integration in unit-4 projects (separate sprint)

## Drop-in Block Conflicts (rejected and remediated)

- Imported retired `InterfaceStateGovernor` -> reuse `select_ui_state`
- Missing `backend.` import prefix -> fixed
- Field name mismatch (`max_complexity` on units, `complexity` on pages) -> structured `CurriculumPage` per unit with explicit `complexity`
- `endpoints/` subdir -> kept under `routes/`
- Client-supplied `signals: dict` (violates ISCS authority) -> server-side estimator only
- Broken Makefile (spaces, wrong app path, no venv) -> dropped; existing README run instructions are correct
