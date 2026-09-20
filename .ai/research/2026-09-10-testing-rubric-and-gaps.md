# Testing rubric and gap analysis — Noni / Mynaani

**Date:** 2026-09-10  
**Branch:** `docs/research-protocol`  
**Scope:** full application stack (FastAPI backend, React/Vite frontend, GitHub Actions CI/CD)

## Executive summary

The repo has a **large, well-organized test inventory** but a **significant effective-coverage gap**. There are ~285 backend test functions, ~154 frontend unit tests, and a Playwright E2E matrix that expands to ~75 generated test cases across 5 browser projects. However:

- Backend tests are currently **failing en masse** (≈51 failures per `CI-HEALTH-001`) due to route-contract drift, and **9 backend test files are empty placeholders**.
- Frontend unit coverage is **76.78 % lines / 61.72 % branch / 62.33 % functions**, but 15 of 154 frontend unit tests are `it.fails` stubs and many production components have **zero** unit or E2E coverage.
- E2E Playwright only functionally covers **landing, the free-curriculum dialog, and post-purchase success routing**. High-risk surfaces (`/gift`, `/gift-redeem`, `/paywall`, onboarding flows, `/admin`, `/account`, `/org`, `/c/:slug`, `/purchase/cancel`, auth callback) are not exercised end-to-end.
- Security, accessibility, and static-analysis tooling are present, but not all gates are green (`bandit` debt, broken `trivy-action` tag).

**Overall grade: C+** — strong scaffolding and tooling choices, but the test suite is not yet a reliable regression net for the product's most critical paths.

## 1. Test inventory

### 1.1 Frontend

| Layer | Files | Test cases | Notes |
|-------|-------|------------|-------|
| Unit / component | 19 `*.test.{ts,tsx}` | 154 (`138 passing`, `15 expected fail`) | `login_contract.test.ts` contributes the 15 `it.fails` stubs. |
| E2E (Playwright) | 5 `.spec.ts` files | 75 generated cases (≈375 browser runs across 5 projects) | `responsive.spec.ts` loops 4 viewports × 5 routes × 3 checks + 1 hero check. |
| A11y / contrast | `axe-playwright` + `contrast.spec.ts` | 4 contrast surfaces + axe in landing/curriculum | Only `/`, sign-in, free curriculum, and curriculum menu are contrast-checked. |
| Bundle / lint | `check-bundle-size.mjs`, `madge`, `knip`, ESLint, Prettier | Not tests per se, but quality gates. | Dead-code and circular-dependency checks in `package.json`. |

Coverage from `npm run test:coverage`:

```
All files | 76.78 % Stmts | 61.72 % Branch | 62.33 % Funcs | 77.77 % Lines
```

Notable low-coverage files:

- `frontend/src/components/HowItWorksDialog.tsx` — 32.25 % stmts, 0 % branch/funcs
- `frontend/src/components/OrgDashboardPage.tsx` — 30 % stmts, 16.66 % branch/funcs
- `frontend/src/hooks/useViewport.ts` — 53.84 % stmts, 35.71 % branch
- `frontend/src/api/billing.ts` — 50 % stmts
- `frontend/src/api/client.ts` — 66.26 % stmts, 45 % funcs
- `frontend/src/components/curriculum/PageTypes.tsx` — 72.97 % stmts, 47.05 % branch, 11.11 % funcs

### 1.2 Backend

| File | `def test_` | xfail / skip markers | Notes |
|------|-------------|----------------------|-------|
| `test_admin_console.py` | 40 | 0 | Staff/admin surface is the most tested backend module. |
| `test_ui_state_envelope.py` | 37 | 0 | Strong contract coverage for UI envelopes. |
| `test_login_constraints.py` | 18 | 14 xfail + 1 skipif | Intake `P2-JOURNEY-LOOP-003` / `login_contract` redesign in progress. |
| `test_safe_yellow.py` | 14 | 16 conditional skips | Static architecture/dependency guards; many skip if files missing. |
| `test_curriculum_module_2-5.py` (4 files) | 36 total | 0 | Content/ISCS coverage for paid modules. |
| `test_enterprise_contracts.py` | 13 | 0 | API contract smoke tests. |
| `test_enterprise_security.py` | 12 | 0 | CORS/auth/session baseline. |
| `test_a4_billing.py` | 11 | 1 skipif (sqlite) | Billing path (postgres only). |
| `test_paid_lesson_endpoint.py` | 10 | 0 | Paywall/entitlement gating for paid lessons. |
| `test_a2_launch_schema.py` | 9 | 1 skipif | Schema/migration checks. |
| `test_a6_retention_deletion.py` | 9 | 1 skipif | Account deletion flow. |
| `test_curriculum_page_types.py` | 12 | 0 | Page-type contract. |
| `test_stripe_payment_provider.py` | 8 | 0 | Webhook/provider unit tests. |
| `test_a3_auth.py` | 8 | 1 skipif | Auth config/session. |
| `test_a10_smoke.py` | 5 | 1 skipif | Deployment smoke. |
| `test_email_gift_lifecycle.py` | 5 | 0 | Gift token email flow. |
| `test_signup_first_win.py` | 5 | 0 | First-win landing endpoint. |
| `test_sharing_signals.py` | 4 | 0 | Fraud/sharing detection. |
| `test_a5_estimator_persistence.py` | 4 | 1 skipif | Estimator persistence. |
| `test_a7_rate_limit.py` | 5 | 1 skipif | Rate limiting. |
| `test_telemetry_richness.py` | 4 | 0 | Telemetry audit columns. |
| `test_org_dashboard.py` | 3 | 0 | Org dashboard basics. |
| `test_routes.py` | 6 | 0 | Health/root/signals/telemetry. |
| `test_enterprise_business_logic.py` | 7 | 3 skipif | Checkout idempotency/paid-content gating. |
| **9 empty placeholder files** | 0 | — | `test_curriculum_units.py`, `test_curriculum_units_module_0.py`, `test_geragogy_signals.py`, `test_iscs.py`, `test_landing.py`, `test_landing_page.py`, `test_login_scenarios.py`, `test_magic_verifier.py`, `test_telemetry_export.py` |

**Total `def test_` in `backend/tests`:** 285 across 37 files.  
**Empty placeholder files:** 9 (24 % of test files).  
**xfail markers:** 14, all in `test_login_constraints.py`.  
**Conditional skip markers:** 30 (mostly skip-if-sqlite or file-presence guards).  
**Effective backend test functions (excluding empty files):** ~247.

### 1.3 CI / automation

`.github/workflows/ci.yml` runs on every PR:

- Backend: `ruff`, `black`, migrations forward + round-trip, `pytest backend/tests/ -v`.
- Frontend: type-check, build, bundle-size, format, lint.
- E2E: backend service + Postgres, auth contract scripts, Playwright + axe across 5 projects.
- Security: `bandit`, `npm audit`, `trufflehog`, `trivy`.

`.github/workflows/deploy-staging.yml` and `.github/workflows/deploy.yml` add deployment smoke tests and environment verification.

Known red items from `.ai/intake/2026-09-05-ci-health-research-001.md`:

- `pytest backend/tests/` reports **51 failures + 2 errors** (route-contract drift).
- `bandit` reports real findings (B110, B301, B104) not yet triaged.
- `trivy-action@v0.30.0` transitive pin is broken.
- Frontend `build` step needs `VITE_API_BASE_URL` env in CI.

## 2. Route / surface coverage matrix

### 2.1 Frontend routes from `frontend/src/App.tsx`

| Route | Component | Unit test | E2E functional | A11y / contrast | Notes / gap severity |
|-------|-----------|-----------|--------------|-----------------|----------------------|
| `/` | `LandingPage` | `LandingPage.brand.test.tsx` (3) | `landing.spec.ts` (3) | axe + contrast | Hero overlay, caregiver/facilities CTAs, and help-button visibility not fully covered. |
| `/signin` | `SignInPage` | none | `contrast.spec.ts` (sign-in) | contrast only | No auth-flow E2E; no unit tests. |
| `/c/:slug` | `PartnerPage` | none | none | none | **P2** — partner code path has zero tests. |
| `/for-communities` | `ForCommunitiesPage` | `ForCommunitiesPage.test.tsx` (3) | none | none | B2B citations and CTAs not E2E'd. |
| `/privacy` | `PrivacyPage` | `PrivacyPage.test.tsx` (4) | none | none | Copy-only page; low risk. |
| `/help` | `HelpPage` | none | none | none | **P2** — help surface has no tests (relevant to "remove help button for signed-out users" requirement). |
| `/admin` | `AdminConsolePage` | none | none | none | **P2** — staff login/admin surface has no tests. |
| `/gift` | `GiftCheckoutPage` | none | none | none | **P1** — public guest checkout is a known product gap (`P1-GIFT-CHECKOUT-002`); no automated coverage. |
| `/purchase/success` | `PurchaseSuccessPage` | `PurchaseSuccessPage.test.tsx` (2) | `purchase.spec.ts` (1) | none | Only gift-self-purchase routing partially checked. |
| `/purchase/cancel` | `PurchaseCancelPage` | none | none | none | **P2** — cancel loop risk (`P2-JOURNEY-LOOP-003`). |
| `/welcome` | `WelcomePage` | none | none | none | **P2** — onboarding start not E2E'd. |
| `/setup` | `AccountSetupPage` | none | none | none | **P2** — onboarding setup not E2E'd. |
| `/getting-started` | `GettingStartedPage` | none | none | none | **P2** — onboarding steps not E2E'd. |
| `/curriculum` | `CurriculumRenderer` | `PageTypes.test.ts` (13) | `curriculum.spec.ts` (3) | axe + contrast | End-of-free-track CTA entitlement logic not tested. |
| `/paid-curriculum` | `PaidLessonRenderer` | none | none | none | **P2** — paid track E2E missing. |
| `/menu` | `CurriculumMenu` | `PageTypes.test.ts` (curriculum menu envelopes) | `contrast.spec.ts` (curriculum menu) | contrast | Resume/entitlement routing not tested. |
| `/paywall` | `PaywallPage` | none | none | none | **P2** — paywall surface, gift/self-purchase CTAs, entitlement-aware state missing. |
| `/gift-redeem` | `GiftRedeemPage` | none | none | none | **P2** — gift redemption E2E missing. |
| `/mock-checkout` | `MockCheckoutPage` | none | none | none | **P2** — checkout success/cancel E2E missing. |
| `/account` | `AccountSettingsPage` | none | none | none | **P2** — account deletion/export not E2E'd. |
| `/org` | `OrgDashboardPage` | `OrgDashboardPage.test.tsx` (2) | none | none | Staff/org dashboard E2E missing. |
| `/auth/callback` | inline pending banner | none | none | none | **P2** — OAuth/Magic callback not tested. |

**Summary:** 7 of 22 routes have any frontend unit test; 5 of 22 have functional E2E; 4 of 22 have axe/contrast coverage. Critical revenue/gifting/onboarding surfaces are largely untested.

### 2.2 Backend routes from `backend/api/routes/*.py`

| Route module | Endpoints | Test file(s) | Tests | Notes / gap severity |
|--------------|-----------|--------------|-------|----------------------|
| `admin.py` | 20 | `test_admin_console.py` | 40 | Strong coverage. |
| `curriculum.py` | 28 | `test_curriculum_module_2-5.py`, `test_curriculum_page_types.py`, `test_paid_lesson_endpoint.py` | 67 | Missing `test_curriculum_units.py` and `test_curriculum_units_module_0.py` (empty placeholders). |
| `organizations.py` | 13 | `test_org_dashboard.py` (3) + some in `test_enterprise_contracts.py` | ~3 | **P2** — B2B org/license/codes/redeem/dashboard largely untested. |
| `landing.py` | 4 | `test_landing.py`, `test_landing_page.py` empty | 0 | **P2** — landing content endpoint (`/api/landing/page`) has zero tests. |
| `billing.py` | 4 | `test_a4_billing.py`, `test_stripe_payment_provider.py`, `test_enterprise_business_logic.py` | 26 | Good unit coverage; guest checkout path needs tests once implemented. |
| `auth.py` | 3 | `test_a3_auth.py`, `test_login_constraints.py` | 26 | 14 xfail in login constraints = redesign in progress. |
| `me.py` | 3 | `test_a6_retention_deletion.py`, `test_enterprise_contracts.py` | ~12 | Missing `/me/export` and any entitlements endpoint (`P2-JOURNEY-LOOP-003` option C). |
| `gifts.py` | 2 | `test_email_gift_lifecycle.py`, `test_enterprise_business_logic.py` | ~8 | Token preview/claim covered lightly; fraud edge cases missing. |
| `telemetry_export.py` | 3 | `test_telemetry_export.py` empty | 0 | **P2** — admin telemetry export has zero tests. |
| `signals.py` | 2 | `test_routes.py` | 6 | Basic user-action/telemetry logging only. |
| `telemetry_summary.py` | 1 | none dedicated | 0 | **P3** — summary endpoint not tested. |
| `onboarding_telemetry.py` | 1 | none dedicated | 0 | **P3** — onboarding telemetry not tested. |
| `session_validation.py` | 1 | `test_enterprise_security.py` | 1 | Session validate covered. |
| `ui_envelope.py` | 1 | `test_ui_state_envelope.py` | 37 | Excellent contract coverage. |
| `account.py` | 0 | none | — | Module has no endpoints (unused/placeholder). |
| `betterstack_onboarding.py` | 0 | none | — | Module has no endpoints. |

## 3. Testing rubric and grades

| Dimension | Grade | Score (0-4) | Evidence |
|-----------|-------|-------------|----------|
| **Static analysis & CI hygiene** | B | 3 | Pre-push hooks, lint, format, type-check, bundle-size, migration round-trip, security scans all wired. But CI has unresolved red items (backend tests, bandit, trivy tag, missing `VITE_API_BASE_URL`). |
| **Backend API / service testing** | C- | 1.5 | 285 test functions, but 51 failing due to contract drift, 14 xfail, 9 empty files, and several route modules (org, landing, telemetry export) have no tests. No measured coverage. |
| **Frontend unit / component testing** | C+ | 2.5 | 154 tests, 76.78 % line coverage, strong design-token and contract tests. However 15 are stubs, many core components untested, branch/func coverage <65 %. |
| **E2E / journey / a11y testing** | C | 2 | Playwright + axe + contrast + responsive matrix across 5 projects is excellent tooling. But only landing, curriculum dialog, and purchase-success routing are functionally tested; high-risk revenue/onboarding/admin surfaces are not. |
| **Security & compliance** | B | 3 | Bandit, npm audit, TruffleHog, Trivy, CORS/auth tests, secret scanning are present. Not all gates green; no dedicated OWASP-style abuse tests for guest checkout. |
| **Performance / load / smoke** | D | 1 | `bundle-size` check in CI; `k6-smoke.js` and `chaos-test.ps1` exist but are not wired to CI. No load/perf regression gate. |
| **Regression / contract coverage** | C | 2 | `p11-window-settimeout-regression.test.ts`, telemetry contract, UI envelope contract, auth contract scripts. Login contract stubs and backend route-contract drift are unresolved. |

**Weighted overall grade: C+** (≈2.14 / 4.0).

## 4. Priority gap analysis and recommended additions

### P1 — must have before production confidence

1. **Guest gift checkout E2E** (`/gift` → mock checkout → `/purchase/success?is_gift=true` → email token → `/gift-redeem` → `/paid-curriculum`)
   - *Where:* `frontend/e2e/gift.spec.ts` and `backend/tests/test_gift_guest_checkout.py`.
   - *Tracks:* `P1-GIFT-CHECKOUT-002`.
2. **Backend route-contract reconvergence**
   - *Where:* `.ai/intake/2026-09-05-ci-health-research-001.md` layer 9.
   - *Action:* reconcile `/login/scenario`-style endpoints or tests; get `pytest backend/tests/` green in CI.
3. **Paywall / entitlement-aware routing tests**
   - *Where:* `frontend/e2e/paywall.spec.ts`, `frontend/src/components/__tests__/PaywallPage.test.tsx`, backend `GET /api/me/entitlements` tests.
   - *Tracks:* `P2-JOURNEY-LOOP-003`.
4. **Onboarding flow E2E**
   - *Where:* `frontend/e2e/onboarding.spec.ts` covering `/welcome` → `/setup` → `/getting-started` → `/curriculum`.
   - *Tracks:* `WI-003-testing-instructions.md`.

### P2 — high value, can follow P1

5. **Component unit tests for untested pages**
   - `SignInPage`, `PaywallPage`, `GiftCheckoutPage`, `GiftRedeemPage`, `AccountSettingsPage`, `AdminConsolePage`, `PurchaseCancelPage`, `PartnerPage`, `HelpPage`, `WelcomePage`, `AccountSetupPage`, `GettingStartedPage`, `PaidLessonRenderer`, `CurriculumRenderer`, `CurriculumMenu`.
6. **Backend org/B2B surface tests**
   - `organizations.py` endpoints: create org, license, codes, redeem, usage, slug, dashboard.
   - *Where:* `backend/tests/test_organizations.py` (new) and extend `test_org_dashboard.py`.
7. **Backend landing content tests**
   - `GET /api/landing/page`, `/api/landing/steps`, `/api/landing/first-win`.
   - *Where:* fill `backend/tests/test_landing.py` and `test_landing_page.py`.
8. **Telemetry export / admin tests**
   - `GET /api/v1/telemetry/export` and `.csv`, `/api/v1/telemetry/rollup`.
   - *Where:* `backend/tests/test_telemetry_export.py`.
9. **Auth callback and Magic link flow**
   - `frontend/e2e/auth.spec.ts` for `/auth/callback`, `/signin` with Magic, cross-tab sign-out.
10. **Help-button visibility regression**
   - `frontend/e2e/help.spec.ts` asserting `Help` link absent when signed out and present when signed in on key surfaces.
11. **Visual / responsive regression for landing hero**
   - Extend `responsive.spec.ts` to use real routes (`/gift`, `/for-communities`) instead of `/lessons` and `/redeem`, and add screenshot-diff or at least layout assertions for the fixed single-viewport hero.

### P3 — quality-of-life and coverage completion

12. **Frontend coverage gate**
   - Add `test:coverage` to CI with a threshold (e.g. 80 % stmts / 70 % branch) and fail on regression.
13. **Backend coverage gate**
   - Add `pytest-cov` to the backend job with a threshold and `coverage report`.
14. **Load / smoke tests in CI**
   - Wire `scripts/k6-smoke.js` or a lightweight health/ready check to the staging deploy workflow.
15. **Fill empty backend placeholder files**
   - `test_curriculum_units.py`, `test_curriculum_units_module_0.py`, `test_geragogy_signals.py`, `test_iscs.py`, `test_magic_verifier.py`, `test_login_scenarios.py`.
16. **Resolve static-analysis debt**
   - Triage `bandit` findings, fix trivy-action tag, add `VITE_API_BASE_URL` to CI build step.

## 5. Risk summary

| Risk | Current state | If not addressed |
|------|---------------|------------------|
| Backend test failures in CI | CI red on `pytest backend/tests/` | Cannot trust CI as a merge gate; regressions slip in. |
| Empty test files / placeholders | 9 backend, 15 frontend stubs | Critical surfaces (landing API, Magic auth, telemetry export, frontend login contracts) have no automated protection. |
| Gift checkout untested | No E2E or unit for `/gift` | The P1 caregiver conversion fix (`P1-GIFT-CHECKOUT-002`) can break in production without detection. |
| Paywall / entitlement loop untested | No tests for `/paywall`, `CurriculumRenderer` end-of-track, `PurchaseCancelPage` | Already-identified P2 journey loop risk (`P2-JOURNEY-LOOP-003`) can regress. |
| Responsive E2E using stale routes | `/lessons`, `/redeem` do not exist in `App.tsx` | The responsive suite gives false confidence; layout checks may pass on 404/redirect pages. |
| No coverage gates | `test:coverage` exists but not enforced in CI | Coverage erodes as new code lands without tests. |

## 6. Suggested implementation order

1. **Stabilize backend tests** — fix route-contract drift so `pytest backend/tests/` passes in CI.
2. **Land P1 gift checkout with paired E2E tests** — `frontend/e2e/gift.spec.ts` + backend `test_gift_guest_checkout.py`.
3. **Add entitlement-aware routing tests** — backend `/api/me/entitlements` tests + `PaywallPage` + `CurriculumRenderer` unit tests.
4. **Backfill missing component unit tests** — start with `SignInPage`, `PaywallPage`, `GiftCheckoutPage`, `PurchaseCancelPage`.
5. **Backfill E2E for onboarding and auth** — `onboarding.spec.ts`, `auth.spec.ts`.
6. **Fix responsive spec routes** and add `/gift`, `/for-communities`, `/paywall` layout checks.
7. **Add coverage gates** to `ci.yml` for both frontend and backend.
8. **Resolve CI red items** (bandit, trivy tag, `VITE_API_BASE_URL`).

## 7. Sources and methodology

- Frontend unit test counts and coverage: `npm run test:coverage` in `frontend/` (2026-09-10 run).
- Backend test inventory: counted `def test_` in `backend/tests/*.py`.
- Route surfaces: `frontend/src/App.tsx` and `backend/api/routes/*.py`.
- Journey / intake context: `.ai/journeys/default/journey.md`, `.ai/intake/2026-09-05-ci-health-research-001.md`, `.ai/intake/P1-GIFT-CHECKOUT-002`, `.ai/intake/P2-JOURNEY-LOOP-003`, `.ai/intake/WI-003-testing-instructions.md`.
- CI state: `.github/workflows/ci.yml`, `.github/workflows/deploy-staging.yml`, `.github/workflows/deploy.yml`.
- Existing audit artifacts: `.ai/audit/journey-logic-validation.md`, `.ai/audit/marty-ui-ux-report.md`, `.ai/audit/persona-journey-validation.md`.
