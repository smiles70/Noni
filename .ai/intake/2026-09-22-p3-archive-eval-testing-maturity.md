# Intake — evaluate archived clone's unpushed commits for porting

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** evaluated — nothing to port
**Parent:** PS-N8N-001 · **Skill check:** `knowledge-graph-extraction` n/a —
historical audit, no new entities.

## Question

Does `/home/h/mynaani/n8n-help-flow` (deleted, archived to
`~/Downloads/legacy-help-flow-archive-2026-09-22.tar.gz`) contain work
worth porting? Primary suspect: `feat/testing-maturity-004`, 20 commits
ahead of its remote branch.

## What testing-maturity-004 was — plain English

The branch built the current e2e + smoke backbone: Playwright journey
specs for gift checkout, account settings, admin console, onboarding,
paywall, community, and auth-callback (Blocks 4.1–4.6); smoke/perf gates
wiring k6 + Lighthouse + pa11y; the A10 isolated backend smoke workflow;
a Playwright config pointing the dev server at the prod API for deployed
runs; and a false-positive fix on `/for-communities` (`"Buy"` substring
matching "if we were buying" → exact-match locators).

## Verdict (verified, not assumed)

The branch commits exist as objects but are not ancestors of staging —
however the **content landed** under different SHAs:

- `community.spec.ts` exact-match fix — present on `main` AND `staging`
  (lines 43–44 verified).
- `playwright.config.ts` prod-API dev-server wiring — present on staging.
- The journey specs — all present and green in today's prod matrix run.

**Nothing to port.** The archive is a redundant backup only.

## Acceptance criteria

- [x] Unique commits enumerated (20) and content compared to live repo.
- [x] No code/test/doc content missing from staging or main.
- [x] Archive retained purely as cold backup in `~/Downloads`.
