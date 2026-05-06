# Noni — Progress

## Active Sprint

None. **Sprint 2: Curriculum Expansion completed** (tag `sprint-2-curriculum-v1`).

## Out of Scope (deferred)

- [ ] Real Claude API integration (currently mocked)
- [ ] Authentication / user accounts (blocks per-learner curriculum cursor)
- [ ] Production deployment / CI-CD pipeline (GitHub Actions)
- [ ] Alembic migrations
- [ ] Real-time durable telemetry export
- [ ] Accessibility audit (WCAG AA, axe-core)
- [ ] Internationalization
- [ ] Pre-commit hooks
- [ ] Container scanning (Trivy/Grype)
- [ ] Bundle size budgets
- [ ] Browser observability (Sentry / Datadog RUM)
- [ ] Feature flags
- [ ] E2E tests (Playwright)
- [ ] ADR directory
- [ ] Design system / component library
- [ ] Frontend UI to navigate units (currently only /what-is-ai is rendered)

## Completed

### Initial Scaffolding
- [x] Python 3.12 venv; backend + dev deps
- [x] Repo structure; ARCHITECTURE.md (10 rules); initial README

### Sprint 1: Progress Closeout (tag `sprint-closeout-v1`)
- [x] Phase 1 Foundations: git, .env, pydantic-settings, retired duplicate ISG
- [x] Phase 2 Database: docker-compose Postgres, SQLAlchemy, TelemetryEvent
- [x] Phase 3 Tests: 19 tests across ISCS, signals, routes
- [x] Phase 4 Frontend: Vite+React+TS strict, axios, CurriculumRenderer, CORS
- [x] Phase 5 Cleanup: lint/format pass, README, gitignore hardened

### Sprint 2: Curriculum Expansion (tag `sprint-2-curriculum-v1`)
- [x] CurriculumUnit model with structured CurriculumPage pages
- [x] Three units of content: "What Is Claude", "How to Use Claude Safely", "Claude-Based Projects"
- [x] Endpoints: GET /api/curriculum/units, /units/{id}, /next-unit
- [x] Server-side ISCS-only selection (no client-supplied signals)
- [x] Tests: data integrity + route contracts (8 new tests)
- [x] All endpoints route through canonical ISCS

## Known Environment Quirks

- IDE write_to_file / edit do not persist to WSL filesystem in this setup. Use shell heredocs.
