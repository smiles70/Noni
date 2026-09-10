---
name: site-checker
description: >-
  App-, codebase-, and repo-agnostic health checker for a deployed web
  application. Crawls the site with Playwright, maps discovered pages to
  source code, diagnoses console/network errors, broken links, and auth-gated
  redirects, and writes a structured report with optional fix proposals.
---

# Site checker

Run this prompt whenever you need to audit the health of a deployed web application and connect findings back to its codebase. This prompt is app-, codebase-, and repo-agnostic.

## Required inputs

- `<base-url>`: the deployed URL to check. If not supplied, infer from `package.json` scripts, `README.md`, `.env`, `vite.config.*`, `next.config.*`, CI config, or Railway/Vercel/Cloudflare settings; if still unclear, ask.
- `<repo-path>` (optional): absolute path to the local repository. If supplied, map discovered surfaces to code.
- `<max-pages>` (default `30`): crawl budget.
- `<scope>` (default `same-origin`): `same-origin`, `subdomains`, or an explicit allow-list of domains.

## Phase 1 — Crawl and capture

1. Identify the stack from root files:
   - `package.json`, `vite.config.*`, `next.config.*`, `nuxt.config.*`, `vue.config.*`
   - `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`
   - `Dockerfile`, `docker-compose.yml`, `railway.toml`, `vercel.json`, `wrangler.toml`
   - `README.md`, `.github/workflows/*.yml`, `.ai/`, `docs/`, `AGENTS.md`

2. Launch a Playwright or MCP browser context with listeners for:
   - `console` events (error / warning / log)
   - `pageerror` (uncaught exceptions)
   - `response` events with status >= 400 or CORS failures
   - `requestfailed` events

3. Discover pages:
   - Start at `<base-url>`.
   - Collect visible same-origin `a[href]` links and form actions.
   - If `<repo-path>` is known, read the route table to seed known routes (React `App.tsx`, Next.js `app/` or `pages/`, Vue `router/index.ts`, etc.).
   - Respect `robots.txt`, `rel="nofollow"`, and `<max-pages>`.

4. For every page visited, capture:
   - URL, HTTP status, and final URL after redirects.
   - Console errors and warnings grouped by source.
   - Network requests with 4xx/5xx, CORS failures, or >2 s response time.
   - Accessibility tree snapshot and interactive elements.
   - Full-page screenshot.
   - Dead/broken links: follow each `a[href]` and record status code.
   - Page title, meta description, H1/H2 structure, viewport rendering issues.

5. Handle auth gates:
   - If a route redirects to `/signin`, `/login`, or a paywall, record it as an auth-gated surface.
   - Use seeded authentication state, a documented test account, or ask the user. Do not brute-force credentials.

## Phase 2 — Map to code

If `<repo-path>` is provided:

1. Find the route table and component layout:
   - React: `src/App.tsx`, `src/main.tsx`, `src/router.*`
   - Next.js: `app/**/page.tsx`, `pages/**/*.tsx`
   - Vue: `src/router/`, `src/views/`
   - Other frameworks: equivalent root routing files.

2. Build a mapping table:

   ```
   Page URL → Frontend route file → Component(s) → API endpoint(s) → Backend handler → Model / service
   ```

3. Locate the backend API surface:
   - FastAPI: `backend/api/routes/*.py`
   - Express: `src/routes/*.js`, `app/routes/*.ts`
   - Django: `*/urls.py`
   - Use the OpenAPI spec (`/openapi.json`, `/docs`, `/api/openapi`) if available.

4. Cross-check with any repo governance:
   - `AGENTS.md` rules
   - `.ai/ontology/*` and `.ai/journeys/*`
   - `docs/adr/*.md`
   - `.devin/skills/*`

## Phase 3 — Diagnose

Classify every finding with a severity:

- **P0** — broken page, 5xx, unhandled exception, auth/security regression, inaccessible critical CTA, payment flow blocked.
- **P1** — 4xx on important route, console error in user flow, layout break on a key viewport, missing alt/label, dead primary CTA.
- **P2** — console warning, minor accessibility issue, non-critical dead link, missing test for a discovered route.
- **P3** — cosmetic, SEO meta, documentation gap.

For every P0/P1, produce a structured RCA:

- **Symptom**: what the user sees.
- **Trigger**: URL, action, and state that reproduce it.
- **Root cause**: likely code path, contract, or configuration issue.
- **Evidence**: log snippet, screenshot reference, network call, code snippet.
- **Confidence**: High / Medium / Low.

De-duplicate findings and rank by user impact.

## Phase 4 — Report

Write the report to `<repo-path>/.ai/research/YYYY-MM-DD-site-checker-report.md` unless the user specifies another path. Include:

1. Executive summary:
   - total pages crawled
   - counts of P0 / P1 / P2 / P3
   - top 3 risks and why they matter
2. Environment snapshot:
   - inferred stack
   - target URL(s)
   - crawl scope and auth strategy
3. Per-page / per-flow findings
4. Code mapping table
5. Recommended next steps
6. Optional fix proposals (only if requested):
   - minimal scoped changes
   - files that would change
   - tests that would need to pass
   - note that every proposal requires human review and must pass CI before merge

## Guardrails

- Do not modify production systems.
- Do not deploy, push, or merge without explicit user approval.
- Do not stage or commit changes unless asked.
- Redact secrets, PII, auth tokens, and card details from logs and screenshots.
- Respect `robots.txt`, rate limits, and the target site's resources.
- Stop and ask if crawl scope or auth is unclear.
- If the site is unreachable, fall back to static code analysis of `<repo-path>` and report likely runtime failure modes.
