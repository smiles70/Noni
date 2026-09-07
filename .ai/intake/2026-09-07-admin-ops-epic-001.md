# Intake: ADMIN-OPS — staff console lifecycle operations epic

**Date:** 2026-09-07
**Trigger:** Post-ADMIN-IA-001 gap analysis — the console can create but
cannot *manage*: no license edit/renew, no code top-up from UI, no
suspend/deactivate, no sub-org linking, no export, no staff-user
management.
**Charter anchor:** institutional buyers (senior living, communities,
nonprofits, health plans) need lifecycle control, auditable reporting,
and graceful offboarding; aggregate-only privacy stays structural.

## Epic blocks (proposed decomposition)

- **E1 — License lifecycle:** edit seats/expiry, renew, suspend license;
  in-console "generate more codes" on an existing license.
- **E2 — Org status control:** suspend/reactivate org; gentle
  deprovisioning (access removed, data retained per retention policy).
- **E3 — Hierarchy:** `parent_org_id` in the wizard; parent rollup view.
- **E4 — Export/reporting:** CSV export of seats/licenses/audit;
  institutional report shape (utilization, expiries, aggregate
  engagement ≥5 cohort only).
- **E5 — Staff administration:** staff user management surface or
  documented secure rotation path (currently env-var only).
- **E6 — Account actions:** suspend/deactivate learner account from
  console; cancel scheduled deletion.

## Verification baseline (pre-research)

- Code top-up API exists: `POST /api/v1/billing/org/{license_id}/codes` —
  UI gap only.
- Org model has `status`; license has `expires_at`; no suspend semantics
  yet — needs semantics + enforcement points (redeem, login, dashboard).
- No staff-user CRUD; auth is `ADMIN_CONSOLE_USERS` +
  `ADMIN_CONSOLE_PASSWORD_SHA256` env vars.
- Export: nothing exists anywhere — new surface.
- Audit trail already captures staff actions — new mutations must log.

## Process artifacts (to fill during epic)

- External research digest: DONE — `.ai/process/ADMIN_OPS_RESEARCH_001.md`
  (20 sources: Stripe, Chargebee, Paddle, 10Duke, Keygen, ISO 27001,
  SOC2 CC6.3, AppMaster, Coggno, AccountableHQ, TouchClass, NIST,
  OWASP, Auth0, Okta, Recurly, CoreLine, Keycloak).
- Use cases + edge cases: in research digest — seat-decrease rules,
  concurrent-edit locking, session revocation on suspend, reactivation
  restore, legal hold, export PII guard, UTC/ISO-8601.
- Epic ordering: E1 license lifecycle → E2 suspend/deactivate →
  E4 export → E3 hierarchy → E5 staff admin → E6 account actions.
- Risk register: pending per-epic intake.
- Ontology/KG nodes: pending closeout.
- Preflights: 3× per PR per standing rule.

## Merge rule

6/6 green + staging verification before merge; production deploy only on
explicit approval per change.
