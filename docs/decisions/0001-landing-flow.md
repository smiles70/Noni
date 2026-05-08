# 0001 — Landing flow is sequenced by user agency, not ISCS stability

## Status

Accepted (Sprint 3, tag `sprint-3-landing-contract-v1`).

## Context

The Golden Landing Flow (`docs/flows/golden-landing-flow.md`) defines the first-visit experience: 8 steps from arrival to optional continuation, with strict constraints (zero pressure, fully reversible, no hidden commitments).

The existing ISCS (`backend/core/interface_control/`) governs **curriculum** complexity by gating which page is rendered based on the stability metric. The landing flow has different requirements:

1. The flow is intentionally fixed and minimal at every step. There is no "harder" or "easier" version.
2. Steps 0-3 must be reachable with **no telemetry, no tracking, and no user action**.
3. Advancement is driven entirely by explicit user agency, not by stability or any inferred signal.

## Decision

1. The landing flow is served from `/api/landing/*`, separate from `/api/curriculum/*`.
2. ISCS does **not** gate landing-step selection. The flow is linear, with one canonical content per step.
3. Backend serves step structure and intent; the frontend tracks current-step position locally for steps 0-3.
4. No telemetry is emitted for steps 0-3. Telemetry may begin at step 4 ("first explicit action") and only after explicit opt-in.
5. Per-learner landing-flow position is **not** persisted server-side until authentication exists. This is a deliberate trade-off in service of "no hidden commitments".

## Consequences

- Landing endpoints (`GET /api/landing/steps`, `GET /api/landing/steps/{id}`) are anonymous reads with no side effects.
- The frontend will need a small local state machine for step navigation (deferred to a later UI/copy sprint).
- A future "Auth + Persistence" sprint must explicitly decide whether returning users resume their landing position or always restart.
- ISCS authority over the curriculum is preserved untouched. The carve-out is documented and bounded to first-visit orientation.
