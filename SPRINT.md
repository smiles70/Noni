# Sprint 6: Hardening & Coverage (CLOSED)

Tag: `sprint-6-hardening-coverage-v1`. 4-in-1 hardening sprint covering accessibility, curriculum depth, E2E, and telemetry export.

## Phases

- 6.2 Curriculum Units 5-7 added; 49 backend tests pass
- 6.4 Telemetry export endpoints (JSON + CSV) with tests
- 6.1 Accessibility: focus-visible rings, larger-text toggle (persistent), reduced-motion respect
- 6.3 Playwright + axe-playwright E2E suite (4 specs) at `frontend/e2e/`
- 6.5 ADRs 0007 (a11y) + 0008 (Playwright + axe)
- 6.6 Closeout

## Deferred

- Vendor-bundle decisions (auth, real Claude, observability, hosting, etc.) - see `docs/deferred-decisions.md`
- Manual screen-reader audit
- Playwright job in GitHub Actions CI (browser-binary cache work)
