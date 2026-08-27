# Phase Inventory — Magic.link Authentication Integration

**Process:** v9.51
**Date:** 2026-08-27
**Scope:** Implementation of Magic.link as the production auth provider for Noni
**Source:** `.ai/process/MAGIC_LINK_INTEGRATION_PLAN.md` | ADR 0027 | Intake 2026-08-27

---

## Summary

The Magic.link integration is divided into **6 phases** (0 through 5). Each phase has an entry gate, exit gate, owner, verification evidence, and a commit boundary.

| Phase | Name | Status | Primary owner | Exit gate |
|---|---|---|---|---|
| 0 | External prerequisites | Pending | Product / Engineering | Magic Dashboard app created; API keys available |
| 1 | Backend SDK + verifier | Pending | Engineering | `pytest test_magic_verifier.py` passes |
| 2 | Frontend SDK + sign-in | Pending | Engineering | `npm run test:unit` auth tests pass |
| 3 | Infrastructure + secrets | Pending | Engineering / Ops | `npm run build` bundle guard passes with `VITE_AUTH_PROVIDER=magic` |
| 4 | Process + documentation | Pending | Engineering | BRD/FRD/PRD, ADR, and `CURRENT_STATE.md` aligned |
| 5 | Verification + release | Pending | Engineering | PRA/Nelson evidence updated; all gates pass |

---

## Phase 0 — External prerequisites

**Objective:** Obtain credentials and configure the Magic Dashboard.

**Inputs:**
- BRD/FRD/PRD
- ADR 0027
- Integration plan

**Tasks:**
1. Create Magic Auth app at `https://dashboard.magic.link`.
2. Copy `MAGIC_PUBLISHABLE_KEY` and `MAGIC_API_SECRET_KEY`.
3. Configure email template and optional redirect URI.

**Outputs:**
- `MAGIC_PUBLISHABLE_KEY`
- `MAGIC_API_SECRET_KEY`
- Magic Dashboard configuration

**Verification:**
- Keys are not committed to source.
- Keys are stored in `infra/.env` or SOPS.

**Commit boundary:** None (credentials are external).

---

## Phase 1 — Backend SDK + verifier

**Objective:** Make the backend capable of validating Magic DID tokens.

**Inputs:**
- `pyproject.toml`
- `backend/services/auth_provider.py` (existing `AuthProvider` protocol)
- `backend/services/auth_verifier.py`
- `backend/core/config.py`

**Tasks:**
1. Add `magic-admin>=2.4.0,<2.6.0` to `pyproject.toml`.
2. Add `MAGIC_API_SECRET_KEY` and `MAGIC_PUBLISHABLE_KEY` to `backend/core/config.py`.
3. Create `backend/services/magic_verifier.py`.
4. Implement `MagicAuthProvider` in `backend/services/auth_provider.py`.
5. Update `auth_verifier.py` `verify_token()` to route `magic` provider.
6. Write `backend/tests/test_magic_verifier.py`.

**Outputs:**
- `MagicAuthProvider` class
- `magic_verifier.py`
- Updated `auth_verifier.py`
- Unit tests

**Verification:**
- `pip install -e .` succeeds.
- `pytest backend/tests/test_magic_verifier.py --no-cov -q` passes.
- `pytest backend/tests/test_iscs.py backend/tests/test_geragogy_signals.py` still passes.

**Commit boundary:** `git add backend/` (include dependency change).

---

## Phase 2 — Frontend SDK + sign-in

**Objective:** Wire the frontend to request and store Magic DID tokens.

**Inputs:**
- `frontend/package.json`
- `frontend/src/components/SignInPage.tsx`
- `frontend/src/auth/AuthProvider.tsx`
- `frontend/src/lib/env.ts`

**Tasks:**
1. Add `magic-sdk@~33.9.0` to `frontend/package.json`.
2. Add `VITE_MAGIC_PUBLISHABLE_KEY` to `frontend/src/lib/env.ts` and `.env.example`.
3. Create `frontend/src/lib/magic.ts`.
4. Update `SignInPage.tsx` to call `magic.auth.loginWithMagicLink`.
5. Update `AuthProvider.tsx` `useCredentialSource()` to read `noni.magic_token` when `AUTH_PROVIDER === "magic"`.
6. Update `frontend/src/api/__tests__/auth.test.ts` and `AuthProvider.test.tsx`.

**Outputs:**
- Magic client config
- Updated sign-in and auth-provider code
- Updated tests

**Verification:**
- `npm install` succeeds.
- `npm run type-check` passes.
- `npm run test:unit` passes.

**Commit boundary:** `git add frontend/`

---

## Phase 3 — Infrastructure + secrets

**Objective:** Ensure build, deploy, and secret management support the new provider.

**Inputs:**
- `infra/.env.example`
- `infra/.env.prod.sops.yaml`
- `frontend/.env.example`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `.github/workflows/deploy.yml`
- `scripts/setup-infrastructure.ps1`
- `scripts/audit-fly-secrets.ps1`
- `scripts/auto_deploy.py`
- `infra/scripts/secrets-sync.sh`

**Tasks:**
1. Add `MAGIC_API_SECRET_KEY` and `VITE_MAGIC_PUBLISHABLE_KEY` to all env files and scripts.
2. Remove any remaining Clerk placeholders.
3. Update `frontend/Dockerfile` build args.
4. Update `docker-compose.yml` and `deploy.yml`.

**Outputs:**
- Updated environment and secret configuration
- Updated CI/CD

**Verification:**
- `npm run build` passes.
- Bundle guard passes (no localhost refs, API URL correct).
- `scripts/audit-fly-secrets.ps1` lists `MAGIC_*`.

**Commit boundary:** `git add infra/ .github/ scripts/ docker-compose.yml frontend/Dockerfile`

---

## Phase 4 — Process + documentation

**Objective:** Keep v9.51 canonical artifacts consistent.

**Inputs:**
- `docs/CURRENT_STATE.md`
- `docs/deferred-decisions.md`
- `docs/ONBOARDING.md`
- `SECURITY.md`
- `README.md`
- `.ai/repo-landscape/package-inventory.*`
- `KNOWLEDGE_GRAPH.json`

**Tasks:**
1. Update `CURRENT_STATE.md` to reflect Magic selected.
2. Close auth-provider item in `deferred-decisions.md`.
3. Update `ONBOARDING.md`, `SECURITY.md` if needed.
4. Update package inventory with `magic-admin` and `magic-sdk`.
5. Update knowledge graph with new capabilities and tests.

**Outputs:**
- Updated canonical docs
- Updated graph

**Verification:**
- `npm run type-check` and `npm run build` still pass.
- Graph is valid JSON and traceable.

**Commit boundary:** `git add docs/ .ai/`

---

## Phase 5 — Verification + release

**Objective:** Prove the integration is production-ready and update process evidence.

**Inputs:**
- All previous phases
- `.ai/production-readiness/PRA_REPORT.*`
- `.ai/nelson/nelson-scorecard.*`

**Tasks:**
1. Run full frontend verification: `npm run type-check`, `npm run test:unit`, `npm run build`, `npm audit`.
2. Run backend verification: targeted `pytest` modules.
3. Run Lighthouse/pa11y if available.
4. Rescore PRA and Nelson.
5. Generate updated HTML reports if required.

**Outputs:**
- Updated PRA/Nelson artifacts
- Updated `PRA_REPORT_noni.html` if required

**Verification:**
- PRA score ≥ previous baseline.
- Nelson score ≥ previous baseline.
- No new `npm` or Python audit findings.

**Commit boundary:** `git add .ai/nelson/ .ai/production-readiness/`

---

## Inter-phase gates

| From | To | Gate |
|---|---|---|
| 0 → 1 | Magic keys available and stored securely |
| 1 → 2 | Backend DID validation is unit tested and green |
| 2 → 3 | Frontend auth tests pass; bundle builds with new env |
| 3 → 4 | No missing secrets; build artifact verified |
| 4 → 5 | Canonical docs and graph updated |
| 5 → done | PRA/Nelson evidence updated and gates met |

---

*Generated under Process v9.51.*


## Railway backend migration

- **Phase 0:** Intake and plan (2026-08-27)
- **Phase 1:** GitHub Actions deploy workflow
- **Phase 2:** Secrets sync and environment
- **Phase 3:** Smoke and docs
- **Phase 4:** Verification and release

See `.ai/process/RAILWAY_MIGRATION_PLAN.md` and `.ai/intake/2026-08-27-railway-migration.md`.
