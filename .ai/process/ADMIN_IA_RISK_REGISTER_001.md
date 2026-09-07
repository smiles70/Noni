# ADMIN-IA-001 — Risk register (50 cases) + work decomposition
**Date:** 2026-09-07 · **Process:** v9.51 · **Rule:** safety > efficiency; concurrency where safe, sequence where not.

## Triple preflight (checked before writing)

- **PF-1 Architecture fit:** all org endpoints already staff-gated via
  `require_staff` (which now accepts staff. tokens) — the wizard composes
  existing, audited mutations; no new write-paths needed for G1.
- **PF-2 Migration risk:** `organizations` gains nullable columns + new
  `org_contacts` table — additive-only, reversible (downgrade drops
  table+columns); alembic chain intact (head: ob5_org_audit_log).
- **PF-3 Blast radius:** changes are confined to `admin.*` surface +
  organizations schema + new frontend routes under /admin. Learner
  routes, envelope system, auth verifier untouched.

## Risk register — 50 cases, each with mitigation

### A. AuthN/AuthZ (staff session + staff-gated mutations)
- R01 Staff token replay after password rotation → token TTL 8h +
  SESSION_SECRET rotation invalidates all; document rotation runbook.
- R02 `staff.` token presented to learner endpoints → get_optional_account
  bypass returns None → 401 on learner routes; no learner identity leak.
- R03 Learner Bearer token hitting /admin/login → login is credential
  route, not token-based; no conflict.
- R04 Tampered/forged staff token → HMAC verify + expiry + username
  allowlist triple-check; tested.
- R05 Deleted staff account still holding token → require_staff checks
  `deleted_at is None`; blocked.
- R06 Removed-from-ADMIN_CONSOLE_USERS username holding valid token →
  verify re-checks allowlist every request; blocked.
- R07 Brute force on /admin/login → rate limit 5/min/IP via existing
  limiter (Redis-backed, fails open only on Redis outage — acceptable).
- R08 Credential stuffing via many IPs → rate limit is per-IP; shared
  credential means single password — record as residual risk, recommend
  per-user passwords later.
- R09 Staff token in localStorage → XSS exfil risk exists; mitigated by
  8h TTL + staff-only scope; CSP already set by SecurityHeadersMiddleware.
- R10 whoami-check oracle (username enumeration) → returns only
  staff:true/false for *presented* token; no enumeration possible.

### B. Schema & migration
- R11 Alembic head conflict if another branch adds a migration → name
  file `adminia_org_contacts.py`, down_revision = current head
  (`ob5_org_audit_log`); rebase if head moves.
- R12 CITEXT/Postgres-only types in new table → use plain String for
  contact email to avoid CI sqlite surprises; rely on app validation.
- R13 Migration on prod DB with existing rows → all new columns NULLABLE,
  org_contacts is a new table → zero-downtime additive.
- R14 Migration failure mid-deploy → alembic runs in lifespan at boot;
  failed migration = pod won't start; old pods keep serving (Railway
  rolling deploy keeps last healthy).
- R15 contacts JSON vs table → chose table (queryable, FK integrity).
- R16 PII minimality → address/phone are org-level business contact data
  (B2B), not learner PII; still aggregate boundary unaffected.
- R17 postal_code free text (international facilities) → String(16), no
  US-only zip regex — validate format loosely, never block.
- R18 state free text → 2-letter validate only when US; keep optional.
- R19 Org contact "primary" multiplicity → enforce one primary in
  service layer, not DB constraint (portable).
- R20 Orphaned contacts on org delete → FK + cascade delete.

### C. API contracts
- R21 POST /org/create schema change → additive optional fields; existing
  callers unaffected (Pydantic ignores absent optional fields).
- R22 Wizard partial failure mid-chain (org created, license fails) →
  each step calls its own endpoint; client retries remaining steps; org
  is usable state without license. Show "incomplete" banner.
- R23 Duplicate slug race → DB unique constraint; surface 409 calmly,
  suggest alternate slug.
- R24 codes generation count > license seats → server already validates
  (check); if not, add guard: codes ≤ remaining seats.
- R25 Wizard double-submit → disable submit while in-flight; idempotent
  retry safe because steps are separate POSTs.
- R26 Overview endpoint N+1 on large org count → single grouped query +
  COUNT aggregates; fine at current scale (<1k orgs).
- R27 Overview staleness → computed per request; no cache.
- R28 accounts search returns PII → already limited fields (id, email,
  name, deletion ts, purchase count) — keep unchanged.
- R29 Staff session vs org_fair_share → fair-share skips when account
  has no org link; staff accounts never claim codes → unaffected.
- R30 Expired staff token mid-wizard → 401 → frontend catches, returns
  to login card, preserves draft in state (sessionStorage).

### D. Frontend
- R31 RequireAuth regression — /admin must stay outside RequireAuth
  (learned from yesterday's bug); covered by unit test asserting route
  renders login card when unauthenticated.
- R32 Interceptor precedence — staff token overrides learner token;
  sign-out clears only staff key, not learner session.
- R33 Wizard state loss on refresh → draft persisted to sessionStorage;
  cleared on completion/sign-out.
- R34 Org list pagination → none yet; cap list at 200 + search required
  (existing min-3-chars rule).
- R35 Copy-link UX without clipboard API → fallback to select+manual copy.
- R36 Mobile/small viewport → sidebar collapses to top bar (stacked).
- R37 Color-token drift → only tokens.ts values; no hardcoded hex except
  the login card surface (already in use).
- R38 Screen readers → labelled sections, aria-current on nav, focus
  order = DOM order; run axe in e2e (existing).
- R39 Bundle size → lazy-load admin chunk (existing pattern continues).
- R40 Print/report view → not claimed; deferred.

### E. Ops & process
- R41 Deploy to prod ordering: migration must land before code → alembic
  runs at app boot (lifespan) — same deploy, safe order.
- R42 Rollback → additive migration stays (downgrade optional); old code
  ignores new columns — safe both directions.
- R43 Env vars missing on an env → login fails closed (503
  admin.session_unavailable); document required vars in .env.example.
- R44 TruffleHog/secret scan on new files → no secrets in code; password
  hash lives in Railway env only.
- R45 Test isolation → new tests use monkeypatched settings + mock db
  where possible; CI provides postgres.
- R46 E2E cost — add one Playwright spec for login→console→overview,
  not full wizard (keep suite <7min).
- R47 Coverage gate (25%) → new code covered by unit tests.
- R48 Lint/format — run ruff+black+prettier before commit (learned: two
  CI failures this session were formatting-only).
- R49 Documentation drift → update how-to-noni-admin.html §2/§7 in the
  same PR so the guide never outclaims the console.
- R50 Scope creep — anything not in G1/G2/G3/G4/G6 is out; log new asks
  as separate intakes.

## Decomposition — epics / blocks / tracks

**E1 — Backend (sequential, single author)**
- B1.1 migration `adminia_org_contacts`: nullable org columns
  (address_line1/2, city, state, postal_code, phone) + `org_contacts`
  table (id, org_id FK cascade, name, email, phone, role, is_primary)
- B1.2 model + Pydantic schema updates (create + detail return fields)
- B1.3 `GET /admin/overview` (orgs, seats, pending flags, licenses
  expiring ≤30d, recent audit across orgs)
- B1.4 `GET /admin/audit` (searchable audit feed, paginated)
- B1.5 tests: migration-shaped model tests, overview, audit, wizard-order
  invariants, staff-token regressions

**E2 — Frontend (sequential after E1; UI depends on contracts)**
- B2.1 console shell: left nav (Overview/Organizations/Accounts/Flags) +
  header w/ user + sign out
- B2.2 Overview page (KPI cards, expiring list, recent audit, +New org)
- B2.3 Organizations list + detail page (licenses, seats, contacts,
  address, audit, dashboard link)
- B2.4 New-organization wizard (4 steps, draft persistence, error resume)
- B2.5 Audit page (feed + filters)
- B2.6 unit tests + 1 e2e spec + guide update (§2, §7)

**Tracks (concurrency map)**
- T1 backend: B1.1→B1.2→B1.3→B1.4→B1.5 strictly sequential (shared files)
- T2 frontend: B2.1→{B2.2..B2.5 can parallel once shell+contracts exist}
  → B2.6 last
- T1 ∥ T2 blocked at contract boundary: B2.3/B2.4 need B1.2; B2.2 needs B1.3
- Merge order: single PR containing E1+E2 (CI is the integration gate)

## Safety rule applied
Concurrency only within E2 leaf screens after contracts freeze;
migrations, shared files, and route files sequential; one PR, one CI
gate, staging verify, owner merge.
