# Noni — Progress

## Active Sprint

None. **Sprint 4: Engineering Foundations completed** (tag `sprint-4-engineering-foundations-v1`).

## Out of Scope (deferred)

- [ ] Real Claude API integration (currently mocked)
- [ ] Authentication / user accounts
- [ ] Production deployment / CI-CD pipeline beyond GitHub Actions config
- [ ] Real-time durable telemetry export
- [ ] Accessibility audit (WCAG AA, axe-core)
- [ ] Internationalization
- [ ] Container scanning (Trivy/Grype)
- [ ] Bundle size budgets
- [ ] Browser observability (Sentry / Datadog RUM)
- [ ] Feature flags
- [ ] E2E tests (Playwright)
- [ ] Design system / component library
- [ ] Frontend UI to navigate units
- [ ] Landing flow UI + final copy

## Completed

### Sprint 0: Initial Scaffolding
- [x] Python 3.12 venv; backend + dev deps; ARCHITECTURE.md (10 rules)

### Sprint 1: Progress Closeout (tag `sprint-closeout-v1`)
- [x] Foundations, Postgres, 19 tests, Vite+React+TS frontend, lint/format/CORS

### Sprint 2: Curriculum Expansion (tag `sprint-2-curriculum-v1`)
- [x] Units 2-4 via canonical ISCS; 8 new tests; remediated drop-in block

### Sprint 3: Golden Landing Flow Contract (tag `sprint-3-landing-contract-v1`)
- [x] Spec doc, ADR 0001, LandingStep model, /api/landing routes, 11 tests

### Sprint 4: Engineering Foundations (tag `sprint-4-engineering-foundations-v1`)
- [x] Pre-commit hooks (ruff, black, standard hooks)
- [x] GitHub Actions CI (.github/workflows/ci.yml; backend lint+test+migrations, frontend type-check+build)
- [x] Alembic migrations (env.py reads settings; baseline migration; stamp head)
- [x] Lifespan switched from create_all() to alembic upgrade head
- [x] ADRs 0002-0005 (Postgres, Vite+TS, tooling stack, Alembic)
- [x] All tests still passing under new alembic-driven flow

## Known Environment Quirks

- IDE write_to_file / edit do not persist to WSL filesystem in this setup. Use shell heredocs.
