# P2 — E2E / browser-compat suite only ever runs against localhost; zero coverage of deployed environments

## Problem

`frontend/playwright.config.ts` hardcodes
`baseURL: "http://127.0.0.1:5173"` with a `webServer` block that boots a
local Vite dev server. There is **no environment-variable override** —
`baseURL` is a literal string. Consequences:

- All 5 browser projects (Chromium, Firefox, WebKit, Pixel 5, iPhone 13)
  — local runs and the CI UAT/E2E jobs alike — exercise only a local dev
  build.
- No automated browser coverage exists against
  `https://staging.noni-web.pages.dev` or `https://www.mynaani.com`.
- "Browser compat test" after a production push is currently manual HTTP
  checks (`curl` status/size) — real rendering, JS execution, and
  per-engine behaviour on the deployed bundle are never verified.
- The dev server proxies to the **production** API
  (`VITE_API_BASE_URL=https://noni-api-production.up.railway.app`), so
  even locally the test topology is "local frontend + prod backend" —
  staging frontend + staging backend is never exercised end-to-end.

## Trigger

`npm run test:e2e` in `frontend/`, or CI E2E jobs — inspect
`frontend/playwright.config.ts:13` and `:17-26`.

## Current impact

- Deployed-site regressions (asset-hash mismatches, `_redirects`
  misconfiguration, Cloudflare Pages quirks, CSP/header issues) are
  invisible to the test suite — exactly the class of bug the stale
  `gifting-ai-learning.pdf` asset demonstrated.
- Cross-browser green runs give false confidence: they validate the dev
  build, not what users receive.
- UAT staging gate passes without any browser ever touching staging.

## Outcome needed

1. A mechanism to point the Playwright suite (or a designated smoke
   subset) at a deployed base URL — e.g. `PLAYWRIGHT_BASE_URL` env
   override that also disables/skips the `webServer` block.
2. Decide the right shape per the research protocol: full-suite vs
   smoke-subset against staging (pre-prod gate) and/or production
   (post-deploy verify), and how it integrates with the existing Deploy
   workflow jobs.
3. Tests that assume local-only fixtures (dev-server routes, seeded
   state) must be identified and excluded or adapted for deployed runs.
4. Document the commands so "browser compat test on prod" becomes a
   real, repeatable step.

## Scope / non-goals

- In scope: `frontend/playwright.config.ts`, possibly a
  `playwright.deployed.config.ts` or project/tag split, `package.json`
  scripts, Deploy workflow smoke/E2E jobs (own commit per workflow
  rule), `.ai/research/` memo.
- Out of scope: rewriting existing specs, adding new product features,
  visual-regression infrastructure (unless research shows it's cheap).
- Must not break the existing local dev workflow (`npm run test:e2e`
  with no env vars must still work).

## References

- Config: `frontend/playwright.config.ts`
- Deploy workflow: `.github/workflows/deploy.yml` (staging UAT/E2E jobs)
- Prior art — stale asset caught only by manual check:
  `.ai/intake/2026-09-15-stale-gifting-pdf-assets.md`
- Research memo: `.ai/research/2026-09-15-deployed-e2e-strategy.md`
