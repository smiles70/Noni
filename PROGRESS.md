# Noni — Progress

## Active Sprint

None. Progress Closeout sprint completed (tag sprint-closeout-v1).

See SPRINT.md for the active plan.

## Still Pending (in current sprint)

- [ ] Phase 1.1 — git init + baseline commit
- [ ] Phase 1.2 — .env from .env.example
- [ ] Phase 1.3 — pydantic-settings + Settings wiring
- [ ] Phase 1.4 — retire interface_state_governor.py
- [ ] Phase 2.1 — docker-compose db up
- [ ] Phase 2.2 — SQLAlchemy engine
- [ ] Phase 2.3 — TelemetryEvent ORM
- [ ] Phase 2.4 — DB-backed telemetry
- [ ] Phase 3.1 — test_iscs.py
- [ ] Phase 3.2 — test_geragogy_signals.py
- [ ] Phase 3.3 — test_routes.py
- [ ] Phase 3.4 — pytest all green
- [ ] Phase 4.1 — Vite + React + TS init
- [ ] Phase 4.2 — frontend deps
- [ ] Phase 4.3 — wire components
- [ ] Phase 4.4 — CORS
- [ ] Phase 5.1 — README updates
- [ ] Phase 5.2 — repo location decision
- [ ] Phase 5.3 — lint/format/typecheck clean
- [ ] Phase 5.4 — closeout commit

## Out of Scope (deferred to future sprints)

- [ ] Real Claude API integration (currently mocked in claude_engine/claude_client.py)
- [ ] Authentication / user accounts
- [ ] Production deployment / CI-CD pipeline
- [ ] Additional curriculum modules: "What is Claude", "How to Use Claude", "Three Claude-based Projects"
- [ ] Alembic migrations (currently using SQLAlchemy create_all)
- [ ] Real-time durable telemetry export (e.g., to data warehouse)
- [ ] Accessibility audit (WCAG AA validation)
- [ ] Internationalization

## Completed (initial scaffolding sprint)

- [x] Python 3.12 venv
- [x] Backend deps + dev tooling
- [x] Initial scaffolding (backend/app, core, models, etc.)
- [x] ISCS core: state_estimator, stability_metric, state_selector
- [x] Signal-only engines: geragogy, diagnostic, nlu, claude (mocked), projects
- [x] In-memory telemetry service
- [x] API routes: /api/curriculum/what-is-ai, /api/signals/*
- [x] Models: UserAction, ProgramGraph, CurriculumPage
- [x] main.py wires routers; smoke tests pass via TestClient

## Known Environment Quirks

- IDE write_to_file/edit do not persist to WSL filesystem in this setup. Use shell heredocs.
