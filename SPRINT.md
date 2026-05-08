# Sprint 3: Golden Landing Flow Contract (CLOSED)

Goal: lock the Golden Landing Flow as canonical, scaffold its backend contract without finalizing copy or UI.

## Phases

- 3.1 Spec doc (`docs/flows/golden-landing-flow.md`) + first ADR (`docs/decisions/0001-landing-flow.md`)
- 3.2 `LandingStep` model + `LANDING_STEPS` (8 steps, sequence 0-7, no display copy)
- 3.3 `GET /api/landing/steps` and `GET /api/landing/steps/{id}` mounted in `main.py`
- 3.4 Contract tests: data integrity, exit_always_safe invariant, requires_user_action only for step 4+, no display copy finalized
- 3.5 Closeout: PROGRESS, commit, tag `sprint-3-landing-contract-v1`

## Out of Scope (deferred)

- Final user-facing copy (spec explicitly forbids "copy finalization" here)
- UI / visual design / frontend rendering of landing steps
- Per-learner persistence of landing position (requires Auth sprint)
- Telemetry hooks for steps 4+ (requires consent / opt-in design)
