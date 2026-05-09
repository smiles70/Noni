# Sprint 8: CI Playwright Integration (CLOSED)

Tag: `sprint-8-ci-e2e-v1`. Closes the WCAG enforcement loop by running the Playwright + axe E2E suite on every push/PR in GitHub Actions.

## Phases

- 8.1 New `e2e` job in `.github/workflows/ci.yml` - depends on backend + frontend, runs Postgres service, boots backend, health-checks `/health`, then runs E2E
- 8.2 Playwright config made CI-aware (forbidOnly, retries=2, traces/screenshots on failure, no server reuse)
- 8.3 Failure artifacts uploaded: HTML report + backend log
- 8.4 Closeout

## Out of scope

- Cross-browser matrix (firefox/webkit) - chromium only for now
- Vendor decisions (see `docs/deferred-decisions.md`)
- Caching the backend Python deps separately (pip install is cheap on CI)
