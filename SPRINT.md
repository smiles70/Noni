# Sprint 12: Cross-browser E2E (CLOSED)

Tag: `sprint-12-multi-browser-v1`. Adds firefox + webkit to the Playwright matrix so every push/PR runs the WCAG 2.1 AA scan against three engines.

## Phases

- 12.1 Add `firefox` and `webkit` projects to `frontend/playwright.config.ts`
- 12.2 Update CI `e2e` job to install all three browsers (still cached as a unit)
- 12.3 ADR 0011
- 12.4 Closeout
