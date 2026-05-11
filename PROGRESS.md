# Noni - Progress

## Deferred Decisions

See [`docs/deferred-decisions.md`](./docs/deferred-decisions.md) for the bundle of 3rd-party / vendor decisions held for a single later pass.

## Active Sprint

None. **Sprint 20: TelemetryGatedUnit Refactor completed** (tag `sprint-20-telemetry-gated-unit-v1`).

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
