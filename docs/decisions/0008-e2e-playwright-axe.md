# 0008 - End-to-end and accessibility verification via Playwright + axe-playwright

## Status

Accepted (Sprint 6).

## Context

Unit tests cover engine logic and route contracts. They do not catch:
- Frontend / backend integration regressions.
- Routing / state-toggle bugs in the React tree.
- WCAG violations that only manifest in a real DOM.

Three credible options for E2E:

- **Cypress** - mature, good DX, but requires its own runtime and lacks first-class WebKit support.
- **Selenium / WebDriver** - legacy choice; not recommended for new projects.
- **Playwright** - Microsoft-backed, OSS, fast, Chromium + Firefox + WebKit, first-class TypeScript, integrates cleanly with `axe-playwright`.

## Decision

- Adopt **Playwright** for end-to-end testing.
- Adopt **axe-playwright** for automated WCAG 2.1 A/AA scanning inside Playwright tests (see ADR 0007).
- Tests live in `frontend/e2e/`; config in `frontend/playwright.config.ts`.
- Playwright `webServer` block boots `npm run dev` automatically with `reuseExistingServer: true` so local runs do not double-start the dev server.
- Local first-time setup: `npm run test:e2e:install` (downloads browsers, ~150 MB).
- Routine local runs: `npm run test:e2e`.
- CI integration is deferred until the GitHub Actions workflow gains a frontend job that needs the browser binaries; this is tracked as a follow-on engineering task.

## Consequences

- Browser binaries are large; CI cache is required when CI integration lands.
- Tests assume baseURL `http://127.0.0.1:5173` and that the backend (`http://127.0.0.1:8000`) is reachable. Solo dev runs Postgres via `docker compose up -d db` first.
- The axe scan is part of the E2E suite, so accessibility is enforced by the same gate as functional correctness.
- Adding a new page requires a corresponding e2e spec or, at minimum, an a11y scan invocation.
