# CI health research protocol (Process v9.51)

**Date:** 2026-09-05
**ID:** CI-HEALTH-001
**Status:** RESEARCH FINDING — layered failure stack, two genuine-debt items remain
**Runs analyzed:** 33987299548 (pre-fix), 33987692521 (mid-fix), 33987850816 (latest)

## Background

CI on `main` was red before this session and had been for some time — the
failures were **stacked**: each visible failure masked the next layer.
Restoring the git hooks (pre-push/pre-commit) surfaced the whole stack.

## Failure archaeology — what was masked by what

| Layer | Failure | Status |
|---|---|---|
| 1 | pre-push hook: `frontend/node_modules/.bin/*` paths don't exist under npm workspaces (hoisted to root) | ✅ FIXED — `0e3cb43` |
| 1b | pre-commit lint-staged: `cd frontend && npx …` is not a spawnable command | ✅ FIXED — in `3a6cf0e` |
| 2 | `setup-node` cache: `cache-dependency-path: frontend/package-lock.json` — file doesn't exist (workspace lockfile is at root) | ✅ FIXED — `222af88` (ci.yml ×3, deploy-staging.yml ×2) |
| 3 | backend `ruff`: 14 errors — 12 unused imports + 2 dead assignments | ✅ FIXED — `222af88` |
| 4 | backend `black --check`: 15 files drifted (never ran — masked by layer 3) | ✅ FIXED — `222af88` |
| 5 | `trivy-action@0.30.0`: missing `v` prefix | ✅ FIXED — `222af88` |
| 5b | `trivy-action@v0.30.0` internally pins `setup-trivy@v0.2.2`, a **deleted tag** — transitive resolution fails at job setup | ⚠️ KNOWN — needs a newer trivy-action tag whose transitive pin resolves (v0.33.1+), not yet applied |
| 6 | frontend `prettier --check`: 5 files drifted | ✅ FIXED — `62b3f0e` |
| 7 | frontend Build: `VITE_API_BASE_URL is not set` — job's build env lacks the var | ⚠️ KNOWN — needs `env: VITE_API_BASE_URL` (staging value or a CI placeholder) on the Build step |
| 8 | security-scan `bandit`: findings — B110 try/except/pass (several), B301 pickle, B104 bind-all-interfaces | ❌ REAL DEBT — code triage or an explicit severity policy decision |
| 9 | backend Tests: **51 failed, 2 errors** — `405 Method Not Allowed`, `KeyError: 'account_id'`, `assert 404 == 401`, circuit-listener AttributeError | ❌ REAL DEBT — contract drift between tests and routes; largest item |

## What's green now

- backend job: ruff ✅, black ✅, migrations forward ✅, migration round-trip ✅ — only the Tests step fails.
- docker-build ✅ both images.
- Deploy workflows unaffected — production and staging deploys are green; **the app itself is stable and live**.

## Assessment

Layers 1–6 were config/tooling rot — fixed non-destructively (no behavior
changes; lint/format/workflow only, verified with the CI-pinned tool
versions locally: ruff 0.15.12, black 26.3.1, prettier).

Layers 7–9 are **real engineering debt**, not gate misconfiguration:

- **7** is a one-line env addition but the correct value needs a decision
  (staging URL vs. a deliberate CI placeholder).
- **8** bandit findings need security triage — some may be intentional
  (pickle in a controlled context, bind-all in a container); fixing or
  tuning the gate without review would be overclaim.
- **9** is the substantive one: ~51 backend tests fail on what looks like
  route-contract drift (`/login/scenario` endpoints returning 405/404).
  The tests may encode a newer contract than the code, or vice versa.
  Either way this is a sprint, not a patch.

## Recommendation

Do not chase further fixes ad hoc. Park layers 7–9 as a tracked work item:
a "backend contract re-convergence" pass (routes vs. tests) plus a bandit
triage + severity policy, and the VITE_API_BASE_URL build-env decision.
The value already delivered: the gate stack now *fails visibly at the real
problems* instead of dying on config rot — which is what a CI gate is for.
