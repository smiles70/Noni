# Noni — Progress

## Active Sprint

None. **Sprint 3: Golden Landing Flow Contract completed** (tag `sprint-3-landing-contract-v1`).

## Out of Scope (deferred)

- [ ] Real Claude API integration (currently mocked)
- [ ] Authentication / user accounts
- [ ] Production deployment / CI-CD pipeline
- [ ] Alembic migrations
- [ ] Real-time durable telemetry export
- [ ] Accessibility audit (WCAG AA, axe-core)
- [ ] Internationalization
- [ ] Pre-commit hooks
- [ ] Container scanning
- [ ] Bundle size budgets
- [ ] Browser observability
- [ ] Feature flags
- [ ] E2E tests (Playwright)
- [ ] Design system / component library
- [ ] Frontend UI to navigate units (currently only /what-is-ai is rendered)
- [ ] Landing flow UI + final copy (spec is locked; copy/visual sprint pending)

## Completed

### Initial Scaffolding
- [x] Python 3.12 venv; backend + dev deps
- [x] Repo structure; ARCHITECTURE.md (10 rules); initial README

### Sprint 1: Progress Closeout (tag `sprint-closeout-v1`)
- [x] Foundations, Database, Tests (19), Frontend (Vite+React+TS), Cleanup

### Sprint 2: Curriculum Expansion (tag `sprint-2-curriculum-v1`)
- [x] Units 2-4 via canonical ISCS; 8 new tests; remediated drop-in block

### Sprint 3: Golden Landing Flow Contract (tag `sprint-3-landing-contract-v1`)
- [x] `docs/flows/golden-landing-flow.md` canonical product spec
- [x] `docs/decisions/0001-landing-flow.md` first ADR
- [x] `LandingStep` model + 8 steps (sequence 0-7)
- [x] `GET /api/landing/steps` and `GET /api/landing/steps/{id}`
- [x] Contract tests (every step `exit_always_safe=True`; no user action before step 4; no display copy finalized)
- [x] Total tests: 38

## Known Environment Quirks

- IDE write_to_file / edit do not persist to WSL filesystem in this setup. Use shell heredocs.
