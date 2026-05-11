# Noni - Progress

## Deferred Decisions

See [`docs/deferred-decisions.md`](./docs/deferred-decisions.md) for the bundle of 3rd-party / vendor decisions held for a single later pass.

## Active Sprint

**Sprints A3 + A5 + A6 + A7 — IN PROGRESS** (auth/sessions, estimator persistence, retention/deletion, rate limiting). A4 (billing/Stripe) and A8 (frontend paywall) follow.

## Completed

- Sprint 0: Initial Scaffolding
- Sprint 1: Progress Closeout (`sprint-closeout-v1`)
- Sprint 2: Curriculum Expansion (`sprint-2-curriculum-v1`)
- Sprint 3: Golden Landing Flow Contract (`sprint-3-landing-contract-v1`)
- Sprint 4: Engineering Foundations (`sprint-4-engineering-foundations-v1`)
- Sprint 5: Landing Copy + Page Rendering (`sprint-5-landing-copy-v1`)
- Sprint 6: Hardening & Coverage (`sprint-6-hardening-coverage-v1`)
- Sprint 7: Documentation & Developer Onboarding (`sprint-7-docs-onboarding-v1`)
- Sprint 8: CI Playwright Integration (`sprint-8-ci-e2e-v1`)
  - New `e2e` job in `.github/workflows/ci.yml` running after backend + frontend jobs
  - Postgres service container, backend booted in background, health-checked
  - Playwright chromium browser cached by `package-lock.json` hash
  - Playwright config now CI-aware: `forbidOnly`, retries=2, traces + screenshots on failure
  - Failure artifacts uploaded: HTML report + backend log (14-day retention)
  - WCAG 2.1 AA axe scan now enforced on every push/PR
- Sprint 9: Curriculum View Accessibility Polish (`sprint-9-curriculum-a11y-v1`)
  - CurriculumRenderer rewritten with semantic landmarks + CSS variables + aria-live
  - Return-to-start affordance added (Reversibility rule enforced in code)
  - 3 new E2E specs in `frontend/e2e/curriculum.spec.ts` including axe WCAG 2.1 AA scan
- Sprint 10: Telemetry Signal Richness (`sprint-10-telemetry-richness-v1`)
  - 5 new audit columns on `telemetry_events` (request_path, stability, selected_state_id, decision_reason, max_complexity)
  - Curriculum + next-unit routes record `iscs_decision` / `iscs_recommendation` per request
  - Baseline migration retroactively populated; fresh DBs (CI) now actually get the schema
  - 4 new tests (53/53 passing); ADR 0009
- Sprint 11: Containerization (`sprint-11-containers-v1`)
  - Multi-stage backend Dockerfile (python:3.12-slim, non-root, /health healthcheck)
  - Multi-stage frontend Dockerfile (node:18-alpine -> nginx:1.27-alpine) + SPA fallback nginx.conf
  - docker-compose.yml extended; `docker compose up --build` boots the full stack
  - ADR 0010
- Sprint 12: Cross-browser E2E (`sprint-12-multi-browser-v1`)
  - Playwright matrix expanded to chromium + firefox + webkit
  - CI `e2e` job installs all 3 browsers (cached as a unit by lockfile hash)
  - WCAG 2.1 AA axe scan now runs against 3 rendering engines per push/PR
  - ADR 0011
- Sprint 13: Sign-up -> First Safe Win Content (`sprint-13-first-win-content-v1`)
  - `backend/content/signup_first_win.py` + Pydantic schema (`backend/models/signup_first_win.py`)
  - `GET /api/landing/first-win` endpoint
  - 5 new tests including no-urgency / reversible-choice invariants (58/58 passing)
  - Closes the previously deferred 'Copy for Golden Flow Steps 5-7' item
- Sprint 14: Pin Backend Dependencies (`sprint-14-pinned-deps-v1`)
  - `requirements.txt` (runtime, exact pins) + `requirements-dev.txt` (tooling)
  - Dockerfile, CI (backend + e2e jobs), README, and CONTRIBUTING.md all install via `pip install -r ...`
  - Four drift-prone inline package lists eliminated
  - ADR 0012
- Sprint 15: Bundle-Size Budget in CI (`sprint-15-bundle-budget-v1`)
  - `scripts/check-bundle-size.mjs` enforces frontend build-output ceiling
  - `npm run bundle-size` available locally; CI fails on regression
  - ADR 0013
- Sprint 16: Mobile Device Emulation in E2E (`sprint-16-mobile-e2e-v1`)
  - Playwright matrix extended with `mobile-pixel` and `mobile-iphone` projects
  - WCAG 2.1 AA axe scan now covers desktop + mobile viewports
  - ADR 0014
- Sprint 17: Module 2 — Sustained Real-World Use of Claude (`sprint-17-module-2-curriculum-v1`)
  - `backend/models/curriculum_units_module_2.py` + `/api/curriculum/module-2/*` endpoints
  - Multi-dimensional ISCS gating via `telemetry_requirements` (recorded, not yet enforced — auth-vendor pass)
  - Rejected the drop-in's `signals: dict` request body; kept backend-derived stability (Rule 1)
  - ADR 0015
- Sprint 18: Module 3 — Long-term Judgment & Recalibration (`sprint-18-module-3-curriculum-v1`)
  - `backend/models/curriculum_units_module_3.py` + `/api/curriculum/module-3/*` endpoints
  - Same architectural pattern as Module 2 (backend-authoritative)
  - ADR 0016
- Sprint 19: Module 4 — Building Claude Skills (`sprint-19-module-4-curriculum-v1`)
  - `backend/models/curriculum_units_module_4.py` + `/api/curriculum/module-4/*` endpoints
  - Same pattern as Modules 2-3; teaches Skills declaratively (vendor-blocked for actual creation)
  - ADR 0017
- Sprint 20: TelemetryGatedUnit Shared Base (`sprint-20-telemetry-gated-unit-v1`)
  - Collapsed three identical `ModuleNUnit(CurriculumUnit)` subclasses to a single `TelemetryGatedUnit` in `curriculum_units.py`
  - Modules 2/3/4 now use one-line aliases: `ModuleNUnit = TelemetryGatedUnit`
  - 79/79 tests unchanged; ADR 0018
- Sprint 21: Closed-World Design Contract (`sprint-21-phase-a-closed-world-v1`, `sprint-21-complete`)
  - Adopted `docs/library/CONTRACT.md` as authoritative design/rendering/AI-reasoning contract
  - Closed reference list in `docs/library/README.md` (2 primary + 20 external sources)
  - UI State Envelope (`/api/ui-envelope/{state_id}`) + Pydantic schema (`backend/models/ui_state_envelope.py`)
  - Design tokens (`frontend/src/design/tokens.ts`) + `RenderGuard` boundary (fail-closed on violation)
  - 16 Vitest unit tests for the 10-item self-check
  - `LandingPage` and `CurriculumRenderer` migrated to tokens + RenderGuard
  - axe WCAG 2.1 AA still clean across all 5 Playwright projects
  - ADR 0019
- Sprint 22: Module 5 — Composing Agents from Skills (`sprint-22-module-5-v1`)
  - `backend/models/curriculum_units_module_5.py` (5 units via `Module5Unit = TelemetryGatedUnit`)
  - `/api/curriculum/module-5/*` endpoints — same backend-authoritative pattern
  - New content-level invariant test: any unit mentioning "agent" must include a human-control marker
  - Citations re-grounded under the closed reference list (ADR 0019): Carr 2009 → Fisk 2009; Formosa 2012 → Knowles 2019; Lövdén 2010 → Sweller 2011; Wiener 1948 → IDD + Fisk 2009
  - 124/124 tests passing; ADR 0020
- Architect/DBA review + topology consolidation (binding docs, no tag yet)
  - `docs/architecture/SYSTEM.md`, `VENDORS.md`, `SCHEMA.md` — system, third-party, and DB diagrams
  - ADR 0021 (pricing & tiering) ratified
  - ADR 0022 (vendor topology — 5 vendors at launch)
  - ADR 0023 (auth and session model — Supabase Auth, server-side session cookie, logical `auth_user_id`)
  - ADR 0024 (DB operational policy — pooler mode, migration via Fly release_command, RLS, pg_cron retention, restore drill)
  - ADR 0025 (secrets — SOPS source of truth + `make secrets-sync` propagation)
- Sprint A1 — Foundations (committed `72ad25f`, push pending until auth set up)
  - `infra/Makefile` (operator surface; `make help` lists all targets)
  - `infra/.env.example` (canonical key manifest)
  - `infra/scripts/` (bootstrap, sync, rotate, audit, deploy, smoke, stripe, restore-drill, backup-now, observability)
  - `infra/cloudflare/waf-rules.json`
  - `.sops.yaml` (encryption rules; public key filled by `make secrets-bootstrap`)
  - `.gitignore` updated to protect plaintext production env files
- Sprint A2 — Launch DB schema (in progress)
  - `alembic/versions/0003_launch_schema.py` — 12 new tables + telemetry_events additive columns
  - `backend/models/{accounts,auth,billing,learning,governance}.py` — SQLAlchemy models
  - `alembic/env.py` updated to import all launch-domain models
  - `supabase/migrations/0001_rls_and_extensions.sql` — RLS policies + extensions (applied via `supabase db push`)
  - `supabase/migrations/0002_pg_cron_retention.sql` — telemetry + rate-limit retention jobs
  - `backend/tests/test_a2_launch_schema.py` — shape, FKs, idempotency, estimator persistence (5 tests)
- Sprint A9 — CI/CD pipelines (in progress)
  - `.github/workflows/ci.yml` — added migration round-trip step (down + up)
  - `.github/workflows/deploy.yml` — preflight + supabase-db-push + fly-deploy + pages-deploy + smoke; no-ops when secrets absent
  - `.github/workflows/secrets-drift.yml` — daily audit, opens `secrets-drift` issue on drift
  - `.github/workflows/nightly-backup.yml` — pg_dump → R2 nightly; no-ops without secrets
  - `.github/workflows/restore-drill.yml` — manual trigger; downloads latest dump, restores into ephemeral Postgres
- Sprint A3 — Sessions & identity (mock OAuth) (in progress)
  - `backend/core/security.py` — token generation, HMAC cookie signing, SHA-256 hashing
  - `backend/services/auth_provider.py` — `AuthProvider` interface + `MockAuthProvider` + `SupabaseAuthProvider` stub
  - `backend/services/sessions.py` — session CRUD, account upsert by `auth_user_id`
  - `backend/api/deps.py` — `get_db`, `get_optional_account`, `get_current_account`
  - `backend/api/routes/auth.py` — `/auth/callback`, `/auth/signout`, `/auth/whoami`
  - `backend/core/config.py` — new settings: `SESSION_SECRET`, `SESSION_TTL_DAYS`, `AUTH_PROVIDER`, etc.
  - `backend/tests/test_a3_auth.py` — 7 tests (happy path, tamper, revoke, idempotent account)
- Sprint A5 — Estimator persistence (in progress)
  - `backend/services/estimator_state.py` — load/save per `(account_id, scope)`; restart-safe
  - `backend/tests/test_a5_estimator_persistence.py` — 4 tests including scope isolation
- Sprint A6 — Retention + GDPR deletion (in progress)
  - `backend/services/telemetry_retention.py` — `expires_at_for(event_type)` policy
  - `backend/services/deletion.py` — request / cancel / execute with grace period
  - `backend/api/routes/account.py` — `/me/delete`, `/me/delete/cancel`
  - `backend/tests/test_a6_retention_deletion.py` — retention + deletion lifecycle (8 tests)
- Sprint A7 — Rate limit primitives (in progress)
  - `backend/services/rate_limit.py` — fixed-window counter, FastAPI `enforce` helper, predefined limits
  - `backend/tests/test_a7_rate_limit.py` — 4 tests (allow/block, identifier and action isolation)
- Main app router registration: `/auth`, `/me`

## Out of Scope (deferred)

- Real Claude API integration (vendor pass)
- Authentication / per-learner state (vendor pass)
- Email provider, observability, hosting, CDN, payments (vendor pass)
- Production deployment pipeline beyond GitHub Actions config
- Internationalization
- Container scanning (Trivy/Grype) and Dockerfile
- Browser observability (Sentry / Datadog RUM)
- Feature flags
- Manual screen-reader audit (NVDA/JAWS/VoiceOver)
- Design system / component library

## Known Environment Quirks

- IDE write_to_file/edit do not persist to WSL filesystem in this setup. Use shell heredocs.
