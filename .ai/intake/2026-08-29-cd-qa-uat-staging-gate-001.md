# Intake — Pre-Deploy QA → UAT → Staging Gate

**Date:** 2026-08-29  
**Process:** v9.51  
**Source prompt:** `.ai/prompts/ci-cd-pipeline.md`  
**Scope:** Update the existing `deploy-staging.yml` so that a `push` to the `staging` branch first runs the QA agent, then the UAT agent, and only then deploys backend and frontend to the Railway/Cloudflare staging environment.

---

## Problem Statement

The current `.github/workflows/deploy-staging.yml` runs immediately on `push` to `staging`. It does not run linting, tests, or contract validation before deploying. This means a broken build can be pushed to the staging environment and discovered there, which is expensive for a Stripe-integrated, 55+ geragogy-sensitive application.

## Desired Flow

```
push to staging
    │
    ▼
┌─────────────┐
│ QA Agent    │  backend compile, bandit, frontend lint + test, secret scan
└──────┬──────┘
       │ on success
       ▼
┌─────────────┐
│ UAT Agent   │  pytest contract tests, Playwright E2E (if present)
└──────┬──────┘
       │ on success
       ▼
┌───────────────────────────────────────┐
│ Railway staging backend deploy        │
│ Cloudflare Pages staging frontend     │
└───────────────────────────────────────┘
```

## Requirements

| ID | Requirement | Extraction method | Confidence |
|---|---|---|---|
| REQ-CD-001 | A `push` to `staging` must trigger QA before any deploy | structured_source | 0.95 |
| REQ-CD-002 | QA must pass before UAT is allowed to run | structured_source | 0.95 |
| REQ-CD-003 | UAT must pass before staging deployment is allowed to run | structured_source | 0.95 |
| REQ-CD-004 | UAT must not attempt real Stripe or production services | structured_source | 0.95 |
| REQ-CD-005 | The existing `deploy-staging.yml` must not be duplicated or replaced by a second deploy workflow | structured_source | 0.95 |
| REQ-CD-006 | The graph must reflect the new capabilities and gates | structured_source | 0.90 |

## Capabilities to add

- `CAP-CD-QA` — run backend lint/security/compile and frontend lint/tests/build.
- `CAP-CD-UAT` — run payment-provider contract tests and optional Playwright E2E.
- `CAP-CD-GATE` — enforce QA → UAT → deploy ordering inside `deploy-staging.yml`.

## Non-goals

- Do **not** modify `deploy-railway-prod.yml` or `deploy.yml`.
- Do **not** modify `deploy-staging.yml` triggers (it still triggers on `push` to `staging` and `workflow_dispatch`).
- Do **not** add a new `deploy-to-railway` step.
- Do **not** push the workflow yet.

## Open questions

1. Does `frontend/package.json` already define `npm run e2e`?
2. Is `backend/tests/test_stripe_payment_provider.py` sufficient as the contract test, or should more tests run?
3. Should the QA/UAT jobs be placed inside `deploy-staging.yml` or a separate `qa-uat-pipeline.yml` that `deploy-staging.yml` waits on?
4. What is the `BudgetProfile` for this work? (Log a `CostEvent` in `.ai/budgets/knowledge-graph-rebuild-001.yaml`.)
