# PS-E2E-001 — Local e2e matrix runs chromium-only; firefox/webkit absent

**Date:** 2026-09-21 · **Priority:** P3 · **Status:** verified-local
**Skill check:** `error-taxonomy` invoked — classified `e2e-failure`
(environment-caused browser launch error, not an assertion failure).

## Problem statement

Local `npx playwright test` errors on every firefox and webkit project:
`browserType.launch: Executable doesn't exist`. The chromium project runs
and passes. Local pre-push e2e verification therefore covers one third of
the configured matrix and reports false failures for the rest.

## Root cause (confirmed, not assumed)

- `frontend/playwright.config.ts` defines three projects:
  chromium, firefox, webkit.
- `.github/workflows/ci.yml:158` installs all three browsers
  (cached under `~/.cache/ms-playwright`) — the CI matrix is complete.
- This machine's `~/.cache/ms-playwright` contained only
  `chromium_headless_shell-1228` — firefox-1532 and webkit-2311 were never
  installed locally. Environment gap, not a repo defect.

## Options

- **A — Install missing browsers locally (selected).**
  `npx playwright install firefox webkit` (+ `--with-deps` if OS libs
  missing). Immediate, matches CI exactly, zero repo risk.
- **B — Accept CI matrix only.** Rejected: local runs would keep
  erroring on 2/3 of projects and mask real failures in the noise.
- **C — Restrict playwright.config to chromium.** Rejected: shrinks CI
  coverage for zero benefit; cross-browser is the point of the matrix.

## Edge cases

- `firefox`/`webkit` system deps missing → install fails →
  `npx playwright install --with-deps` handles OS libs.
- Version drift: lockfile-pinned playwright downloads matching browser
  builds — the cache key already accounts for it in CI.
- Future machines hit the same gap → document the install step
  (proportionate doc note alongside this intake).

## Acceptance criteria

- [x] `npx playwright test --project=firefox --project=webkit` launches
      and runs locally — firefox green (14.5s) under
      MOZ_DISABLE_CONTENT_SANDBOX=1 (userns EPERM on this kernel);
      webkit green on retry (cold-start).
- [x] Doc note exists — CONTRIBUTING.md e2e section covers install,
      deployed-site env var, firefox sandbox workaround, webkit
      cold-start.
- [x] Chromium unchanged — 14/14 prod e2e green pre-change.
