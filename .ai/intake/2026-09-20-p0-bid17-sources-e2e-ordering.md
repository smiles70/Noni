# PS-BID17-005 — /sources footer-link e2e fails pre-deploy UAT (test-ordering defect)

**Status:** fixing | **Severity:** P0 pipeline blocker (staging)
**Found:** UAT run 35510167805 — all 5 browser projects, 15 failures,
`getByRole("link", {name:"Sources"})` element not found.

## Root cause

The footer nav is backend-served (`/api/v1/site/footer`,
MKT-FOOTER-001). Pipeline order is: QA → **UAT e2e** → Pages deploy →
**Railway backend deploy** → post-deploy smoke. My `@smoke` test clicks
the new "Sources" footer link — but during UAT the staging backend still
serves the *previous* `site_chrome.py` (nav_links has no Sources), and
the frontend FALLBACK only applies when the fetch fails. Link absent →
strict-mode locator fails on every project.

## Fix

Change the smoke test to navigate to `/sources` directly (route + page
content live in the frontend bundle, which UAT *does* test). Footer-link
coverage stays at the layers that own it:

- unit: FALLBACK nav_links includes `/sources` (Footer.test.tsx)
- backend: `SITE_FOOTER_CONTENT.nav_links` includes it
  (`test_site_chrome.py`)
- post-deploy smoke already exercises the footer on deployed env where
  the backend change is live

Do NOT make the click conditional (`if exists click else goto`) —
non-deterministic assertions hide real regressions.

## Acceptance

- UAT e2e green on all projects; post-deploy smoke green.
- Footer link verified live post-deploy via the footer assertions that
  already run in the smoke job.
