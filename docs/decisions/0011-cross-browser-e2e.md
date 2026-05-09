# 0011 - Cross-browser E2E: chromium + firefox + webkit on every CI run

## Status

Accepted (Sprint 12).

## Context

Sprint 8 wired the Playwright + axe E2E suite into GitHub Actions, but only against chromium. That catches most regressions but misses class-of-bug failures unique to:

- **WebKit (Safari)** - older adults disproportionately use iPads and Safari on macOS. A WebKit-only regression would land in front of the most sensitive part of the user base.
- **Firefox** - common on Linux desktops and a meaningful long tail.

The cost of adding the other two engines is the cache size (~300 MB total instead of ~100 MB) and roughly tripled E2E runtime (~3 minutes instead of ~1 minute on the GitHub Actions runner).

## Decision

- Add `firefox` and `webkit` projects to `frontend/playwright.config.ts`.
- Update the CI `e2e` job to `npx playwright install --with-deps chromium firefox webkit`. The browsers cache as a unit, keyed on `frontend/package-lock.json` hash.
- The 4 existing specs run unchanged across all 3 engines (Playwright fans out the test list per project automatically).
- Local developers can keep running just chromium with `npx playwright test --project=chromium` if speed matters during iteration.

## Consequences

- The WCAG 2.1 AA axe scan now runs against three rendering engines per push/PR, materially strengthening the accessibility guarantee.
- E2E job duration increases by ~2 minutes; acceptable given the failure-class coverage gain.
- Cache miss (after a `package-lock.json` bump) means the first run on a new lockfile downloads ~300 MB of browser binaries. Subsequent runs hit the cache.
- Test flake risk grows linearly with engine count. If a flake appears that is webkit-only, the right response is to investigate; webkit-skip flags are not allowed without an ADR override.
