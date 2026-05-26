# Sprint 20: TelemetryGatedUnit Refactor (CLOSED)

Tag: `sprint-20-telemetry-gated-unit-v1`. Eliminates 3-way duplication of `Module2Unit` / `Module3Unit` / `Module4Unit` by extracting a shared `TelemetryGatedUnit` base into the canonical model file.

## Phases

- 20.1 `TelemetryGatedUnit` added to `backend/models/curriculum_units.py`
- 20.2 Module 2/3/4 files reduced to one-line alias
- 20.3 79/79 tests still pass (no behavior change)
- 20.4 ADR 0018
- 20.5 Closeout

Triggered by ADR 0017: *"If a 5th module is proposed, the refactor lands first."*

---

# Sprint 21: 100 Concurrent Users (CLOSED)

Tag: `sprint-21-100-concurrent-users`. Addresses the 4 CRITICAL SRE blockers from `docs/audits/sre-go-live-readiness-2026-05-25.md` to get Noni from ~15 concurrent users to 100 concurrent users.

## Phases

- 21.1 **C1 — DB connection pool**: `backend/core/database.py` now uses env-driven `pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle` (defaults: 5/10/10s/3600s). `pool_reset_on_return="rollback"` ensures clean connections between requests.
- 21.2 **C2 — Multi-worker Gunicorn**: Dockerfile CMD switched from single-process `uvicorn` to `gunicorn -k uvicorn.workers.UvicornWorker`. `WEB_CONCURRENCY` env var controls workers (default 1 dev, 3 production). `requirements.txt` now includes `gunicorn==23.0.0`.
- 21.3 **C4 — Horizontal scaling**: `fly.toml` `min_machines_running` bumped from 1 to 2. Each machine runs 3 workers. Total capacity: 2 machines × 3 workers × ~50 req/sec = ~300 req/sec theoretical, ~100 concurrent users realistic with headroom.
- 21.4 **C3 — Load test baseline**: `tests/load/k6-curriculum.js` added. Simulates 100 concurrent users hitting `/health` and `/api/curriculum/module-1/units` with realistic think times. Thresholds: p99 < 500ms, error rate < 0.1%.
- 21.5 **Env documentation**: `infra/.env.example` expanded with `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`, and `WEB_CONCURRENCY`.
- 21.6 **Local parity**: `docker-compose.yml` and `backend/Dockerfile` updated to use Gunicorn for consistency with production.
- 21.7 **Test verification**: 251/260 backend tests pass. The 9 failures are pre-existing auth-envelope regressions in `test_login_scenarios.py` (unrelated to infrastructure changes). No new regressions introduced.

## Capacity After Sprint 21

| Metric | Before | After |
|:-------|:-------|:------|
| Fly machines | 1 | 2 (minimum) |
| Workers per machine | 1 (uvicorn) | 3 (gunicorn + uvicorn) |
| DB connections per machine | 15 | 45 (3 workers × 15 pool) |
| Total DB connections (2 machines) | 15 | 90 |
| Est. concurrent users | ~15 | ~100 |

## Deploy Steps

1. `make secrets-sync` (pushes new env vars to Fly)
2. `fly scale count 2` (ensure 2 machines running)
3. `make deploy-prod`
4. `k6 run --env API_BASE=https://noni-api.fly.dev tests/load/k6-curriculum.js`

## Load Test Results (2026-05-25)

`k6` executed against production (`https://noni-api.fly.dev`).

| Metric | Threshold | Result |
|:-------|:----------|:-------|
| p(99) latency | < 500 ms | **53.18 ms** ✅ |
| Error rate | < 0.1% | **0.00%** ✅ |
| Total requests | — | 20,812 |
| Iterations | — | 10,406 |
| Max VUs | 100 | 100 |
| Duration | 15 min | 15m03s |

**Verdict: Noni validated for 100 concurrent users.**

## Blockers Remaining for Full Production

- H1: Prometheus metrics endpoint (in-memory telemetry only today)
- H2: Query performance audit + index review
- H3: Incident response runbook with RTO/RPO targets

---

# Sprint 22: Production Hardening (IN PROGRESS)

Tag: `sprint-22-production-hardening`. Addresses the 9 critical/high vulnerabilities from `docs/audits/enterprise-security-threat-model-2026-05-25.md` plus the 3 remaining SRE blockers (H1–H3).

## Phases

### Security Critical (I1–I7) — Immediate

- **22.1 I1 — Gate telemetry export**: `backend/api/routes/telemetry_export.py` now requires `get_current_account` + `ADMIN_ACCOUNT_IDS` env var allowlist. Returns 403 for non-admin callers.
- **22.2 I2 — Protect signals ingestion**: `/api/signals/*` endpoints require `get_current_account`. Replace raw `dict` payload with strict `TelemetryEventIn` Pydantic schema.
- **22.3 I3 — Eliminate hard-coded secrets**: `backend/core/config.py` `SECRET_KEY` and `SESSION_SECRET` defaults changed to empty strings. `main.py` startup validation crashes in production if values are missing or contain `"dev"`.
- **22.4 I4 — Remove client-side info leak**: `frontend/src/api/client.ts` `console.warn` removed entirely (previously leaked auth provider + API base URL on every page load).
- **22.5 I5 — Secret rotation**: `SECRET_KEY` and `SESSION_SECRET` rotated in Fly.io secrets. Existing sessions invalidated (acceptable: Bearer tokens are short-lived Clerk JWTs; session cookies are unused post-ADR-0024).
- **22.6 I6 — Rate limit curriculum**: Per-IP rate limits applied to all public `/api/curriculum/*` catalog endpoints (`max_per_window=120`, `window_seconds=60`).
- **22.7 I7 — Harden Stripe webhook**: IP + rate-limit pre-check on `/api/billing/stripe-webhook` before expensive signature verification.

### Security Short-Term (S1–S7)

- **22.8 S1 — Deduplicate Clerk JWT verification**: Extract shared `ClerkVerifier` class from `auth_provider.py` and `auth_verifier.py` into `backend/services/clerk_verifier.py`. Both consumers import from the single source.
- **22.9 S2 — Prometheus metrics endpoint**: Add `/metrics` with `prometheus_client` Counter/Histogram. Replaces in-memory `defaultdict` counters. Exportable to Grafana / Fly Metrics.
- **22.10 S3 — Request ID tracing**: `X-Request-ID` middleware; propagates through frontend → backend → DB logs.
- **22.11 S4 — Structured JSON logging**: Replace plain-text StreamHandler with `python-json-logger` formatter. All logs include `request_id`, `path`, `status`, `latency_ms`.
- **22.12 S5 — Prune unused `sessions` table**: Drop table and any associated pg_cron cleanup jobs (confirmed unused since ADR-0024 Bearer migration).
- **22.13 S6 — Stripe webhook IP allowlisting**: Add Cloudflare WAF rule or Fly proxy config restricting `/api/billing/stripe-webhook` to Stripe's published IP ranges.
- **22.14 S7 — Harden `auth/config`**: Return `"provider": "clerk"` unconditionally in production; do not echo raw `AUTH_PROVIDER` string.

### SRE Remaining (H1–H3)

- **22.15 H1 — Prometheus metrics endpoint** (see 22.9 above).
- **22.16 H2 — Query performance audit + index review**: Run `EXPLAIN ANALYZE` on hot paths (`accounts` lookup by `auth_user_id`, `purchases` by `gift_claim_token_hash`, `telemetry_events` by `event`). Add missing indexes. Document query plan baselines.
- **22.17 H3 — Incident response runbook**: Create `docs/operations/incident-response-runbook.md` with RTO (1 hour), RPO (15 minutes), escalation path, secret-rotation playbooks, and communication templates.

### Medium-Term Prep (M1–M7)

- **22.18 M1 — CI security scanning**: Add `bandit`, `semgrep`, `npm audit`, and `truffleHog` to GitHub Actions pipeline.
- **22.19 M5 — Backup verification**: Document and test Supabase point-in-time restore procedure.

## Sprint 22 Status

| Task | Status |
|:---|:---|
| 22.1–22.7 (I1–I7) Critical Security | **CLOSED** |
| 22.8–22.11, 22.14 (S1–S4, S7) Short-Term Security | **CLOSED** |
| 22.12 (S5) Prune sessions table | **MIGRATED → Sprint 23** |
| 22.13 (S6) Stripe IP allowlisting | **MIGRATED → Sprint 25** |
| 22.15–22.17 (H1–H3) SRE blockers | **MIGRATED → Sprints 23–26** |
| 22.18–22.19 (M1, M5) Medium-Term | **MIGRATED → Sprints 23–24** |

**Score after Sprint 22:** 59 / 100 (C+ — Hardened Beta)

---

# EPIC: Production Readiness (Sprints 23–26)

**Epic Tag:** `epic-production-readiness-2026-05`
**Source:** `docs/audits/production-readiness-100-point-audit-2026-05-25.md`
**Goal:** Close all HIGH and MEDIUM gaps; verify all Q1–Q7 operational blindspots; reach **75 / 100 (B)** before general availability.
**Target Launch:** After Sprint 26 closure.

## Dependency Map

```
Sprint 23 ─┬─ Backend: Security headers (H1) ────────────┐
           │─ Backend: Graceful shutdown (H6) ──────────┤
           │─ Backend: DB timeouts (M2) ──────────────────┤
           │─ Frontend: Error boundaries (M6) ────────────┤ → Independent; all can run in parallel
           │─ CI: Security scanning (M5) ────────────────┤
           │─ Ops: Verify Fly secrets (Q6) ─────────────┘
           │
           └─ Sprint 24 ─┬─ Backend: Circuit breakers (H3) ────────────┐
                         │─ Backend: Background job queue (H4) ────────┤
                         │─ Backend: Webhook replay dedup (M3) ──────┤ → H3/H4 can parallel
                         │─ Backend: Query param validation (H5) ──────┘   M3 depends on DB
                         │
                         └─ Sprint 25 ─┬─ Backend: API versioning (H2) ──────────┐
                                       │─ Infra: Stripe IP allowlisting (S6) ───┤ → Independent
                                       │─ Ops: Verify WAF deployed (Q2) ──────────┘   S6/Q2 can parallel
                                       │
                                       └─ Sprint 26 ─┬─ Ops: Runbook + RTO/RPO (Q5) ─────┐
                                                     │─ Ops: Verify SSL mode (Q1) ──────────┤ → All independent
                                                     │─ Ops: JWKS cache alerting (Q3) ──────┤   ops/documentation
                                                     │─ CI: Container scanning (#91) ───────┘   tasks; can parallel
```

---

# Sprint 23: Concurrent Safety & CI Hardening

**Tag:** `sprint-23-concurrent-safety`. Closes 5 HIGH/MEDIUM gaps. All tasks are independent and can run in parallel.

## Parallel Workstreams

### Workstream A — Backend Safety (Backend engineer)
- **23.1 H1 — Security headers middleware:** Add `add_security_headers` middleware to `backend/app/main.py`. Injects `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'`.
- **23.2 H6 — Graceful shutdown:** Trap `SIGTERM` in `lifespan` or via Gunicorn `worker_int` hook. Set `kill_timeout = 25s` in `fly.toml`. Close DB pool and finish in-flight requests before exit.
- **23.3 M2 — DB query timeouts:** Add `connect_args={"connect_timeout": 10, "options": "-c statement_timeout=30000"}` to `backend/core/database.py` engine creation.

### Workstream B — Frontend Resilience (Frontend engineer)
- **23.4 M6 — React ErrorBoundary:** Add top-level `<ErrorBoundary>` in `frontend/src/main.tsx`. Fallback UI: "Something went wrong. Please refresh the page or contact support." Log errors to telemetry with `request_id`.

### Workstream C — Pipeline Hardening (DevOps engineer)
- **23.5 M5 — CI security scanning:** Add three new jobs to `.github/workflows/ci.yml`:
  - `bandit backend/` (Python SAST)
  - `npm audit --audit-level=moderate` (frontend dependency audit)
  - `truffleHog filesystem . --only-verified` (secret leak detection)

### Workstream D — Operations Verification (SRE)
- **23.6 Q6 — Fly secrets audit:** Run `flyctl secrets list` (or `make secrets-list`). Confirm `SECRET_KEY` and `SESSION_SECRET` do not contain old hard-coded values. If stale, rotate immediately and redeploy.
- **23.7 Q4 — Sessions table audit:** Run `SELECT pg_size_pretty(pg_total_relation_size('sessions'))`. If > 0 and table is confirmed unused, create Alembic migration to drop table and any associated pg_cron cleanup jobs.

## Sprint 23 Exit Criteria
- [ ] All new CI jobs pass on the feature branch. **BLOCKED — GitHub Actions billing**
- [x] Security headers present on every response (verified via `curl -I`). **CLOSED**
- [x] SIGTERM trap verified: deploy a review app, trigger `flyctl machine stop`, confirm zero 500s in-flight. **CLOSED**
- [x] ErrorBoundary renders correctly when a child component throws. **CLOSED**
- [x] `sessions` table size documented; drop migration created if unused. **CLOSED (script ready)**

---

# Sprint 24: Resilience & Transaction Safety

**Tag:** `sprint-24-resilience`. Closes 4 HIGH/MEDIUM gaps. H3 and H4 are the two largest engineering tasks and can start in parallel. M3 depends on a DB table (can reuse existing schema).

## Parallel Workstreams

### Workstream A — Circuit Breakers (Backend engineer)
- **24.1 H3 — Circuit breaker on Clerk + Stripe:** Add `pybreaker==1.0.0` to `requirements.txt`. Wrap `ClerkAuthProvider.fetch_user_profile` and `StripePaymentProvider.verify_webhook` / `create_checkout_session` with a shared `CircuitBreaker`. Config: `fail_max=5`, `reset_timeout=30`, `expected_exception=(httpx.HTTPError, stripe.error.APIError)`. When open, return degraded response (skip profile enrichment, return cached data, or fail with 503 + `billing.transient_unavailable`).

### Workstream B — Background Job Queue (Backend engineer)
- **24.2 H4 — Celery + Redis queue:** Add `celery[redis]==5.3.0` to `requirements.txt`. Spin up a Fly Redis instance (or Upstash Redis). Create `backend/tasks/` module with three initial task types:
  - `process_stripe_webhook` — deferred from `billing.py:stripe_webhook` route.
  - `export_telemetry_csv` — deferred from `telemetry_export.py`.
  - `cleanup_deleted_accounts` — deferred from `account.py:request_deletion` grace period expiry.
- Update route handlers to enqueue tasks and immediately return `202 Accepted` with a `task_id` for polling.

### Workstream C — Webhook Idempotency (Backend engineer, can start after 24.2 schema is stable)
- **24.3 M3 — Stripe webhook replay protection:** Create `webhook_events` table (or Redis SET) storing `event_id` + `processed_at`. In `stripe_webhook`, check existence before processing. TTL = 24h. Return `200 OK` for duplicates (idempotent).
- **24.4 M1 — Checkout idempotency keys:** Accept `Idempotency-Key` header on checkout creation. Store key + outcome in `idempotency_keys` table with 24h TTL. Return cached response for duplicate keys.

### Workstream D — Query Param Validation (Backend engineer)
- **24.5 H5 — Strict query param schemas:** Audit all public GET endpoints. Replace bare `str` / `int` query params with `Query(..., max_length=..., pattern=..., ge=..., le=...)` constraints. Add Pydantic `ParamModel` where multiple query params are grouped.

## Sprint 24 Exit Criteria
- [ ] Circuit breaker test: mock Clerk API down for 6 requests; confirm 5th+ returns 503; confirm recovery after 30s.
- [ ] Background task test: enqueue a webhook task; confirm Redis job executes and marks purchase complete.
- [ ] Webhook replay test: POST same Stripe event ID twice; second returns 200 with no DB mutation.
- [ ] Query param validation test: pass `?page=-1` or `?search=<script>`; confirm 422 with clear error.

---

# Sprint 25: API Foundation & Edge Hardening

**Tag:** `sprint-25-api-foundation`. Closes 1 HIGH + 1 Short-Term gap. H2 and S6/Q2 are independent and can run in parallel.

## Parallel Workstreams

### Workstream A — API Versioning (Backend + Frontend engineers)
- **25.1 H2 — `/api/v1/` prefix:** Move all public API routers under `/api/v1/` in `backend/app/main.py`. Preserve `/api/` as a 302 redirect to `/api/v1/` with `Deprecation` header (`Sunset: <date>`).
- Update `frontend/src/api/client.ts` base URL from `/api/` to `/api/v1/`.
- Update E2E tests and k6 load tests to use `/api/v1/`.
- Document breaking change in `docs/adr/0025-api-versioning.md`.

### Workstream B — Edge Security (Infra engineer)
- **25.2 S6 — Stripe webhook IP allowlisting:** Add Cloudflare WAF rule or Fly proxy config restricting `/api/billing/stripe-webhook` to Stripe's published IP ranges (`stripe.com/docs/ips`).
- **25.3 Q2 — Verify WAF deployed:** Run `wrangler deploy` or Terraform apply. Check Cloudflare analytics dashboard for "Blocked requests" trending non-zero. Document deployment procedure in `infra/cloudflare/README.md`.

## Sprint 25 Exit Criteria
- [ ] All E2E tests pass against `/api/v1/` routes.
- [ ] `/api/health` still responds (not versioned; always latest).
- [ ] Cloudflare WAF rule blocks a test request from a non-Stripe IP to `/api/billing/stripe-webhook`.

---

# Sprint 26: Operational Readiness & Chaos Validation

**Tag:** `sprint-26-ops-readiness`. Closes 3 operational blindspots + 2 medium-term items. All tasks are independent (documentation, verification, testing).

## Parallel Workstreams

### Workstream A — Incident Response (SRE + Product)
- **26.1 Q5 — Incident response runbook:** Create `docs/operations/incident-response-runbook.md` with:
  - RTO: 1 hour (max acceptable learner downtime)
  - RPO: 15 minutes (max acceptable data loss)
  - Escalation path: on-call → engineering lead → CEO
  - Secret rotation playbook: step-by-step `flyctl secrets set` + `make deploy-prod`
  - Communication templates: learner-facing status page copy, internal Slack alerts
  - Rollback procedure: `fly deploy --image noni-api:<previous_tag>`
- **26.2 Q7 — SOPS key backup:** Export age private key to offline paper backup. Store in physical safe. Document recovery procedure.

### Workstream B — Infrastructure Verification (SRE)
- **26.3 Q1 — Verify Supabase SSL:** Inspect `DATABASE_URL` in Fly secrets. Confirm `sslmode=require` is present. If absent, update connection string and redeploy. Document in `infra/.env.example`.
- **26.3 Q3 — JWKS cache monitoring:** Add Prometheus gauge `clerk_jwks_cache_size` and counter `clerk_jwks_rotation_events_total`. Alert in Grafana (or Fly Metrics) if `auth.transient_verifier_unavailable` rate > 0.1% over 5 minutes.

### Workstream C — CI & Container Security (DevOps)
- **26.4 #91 — Container vulnerability scanning:** Add `trivy image noni-api:ci` to `.github/workflows/ci.yml` docker-build job. Fail on CRITICAL or HIGH CVEs.
- **26.5 #92 — Log cost controls:** Add sampling config to structured JSON logger: 100% of `error`/`warn`, 10% of `info` request logs, 0% of `debug`. Document cost projection.

### Workstream D — Chaos Engineering (QA + SRE)
- **26.6 #100 — Chaos test:** Simulate mid-transaction Fly machine kill during Stripe checkout.
  - Trigger: `fly machine stop <id>` while Playwright E2E test is on `/purchase` page.
  - Verify: No orphaned `Purchase` rows with `status='pending'` and `created_at > 1 hour ago`.
  - Verify: Stripe webhook retry eventually succeeds and purchase status transitions to `complete`.
  - Document results in `docs/operations/chaos-test-report-2026-05.md`.

## Sprint 26 Exit Criteria
- [ ] Runbook reviewed by at least two engineers; drill conducted (simulate secret leak).
- [ ] SSL mode confirmed in production `DATABASE_URL`.
- [ ] Container scan passes with zero CRITICAL CVEs.
- [ ] Chaos test passes: zero orphaned purchases, webhook retry succeeds.
- [ ] Final 100-point audit re-run: target **≥ 75 / 100**.

---

# Epic Exit Criteria (After Sprint 26)

| Gate | Requirement |
|:---|:---|
| Security | Zero CRITICAL or HIGH open vulnerabilities. All CI security scans pass. |
| Reliability | Circuit breakers active on all third-party calls. Background queue processing webhooks and exports. Graceful shutdown verified. |
| API Stability | `/api/v1/` is the canonical public surface. `/api/` redirects with deprecation warning. |
| Operations | Runbook documented, RTO/RPO defined, SSL mode verified, WAF active, secrets rotated. |
| Testing | Chaos test passes. Container scan clean. E2E tests pass on every PR. |
| Score | **≥ 75 / 100** on the 100-point audit. |

**After Sprint 26, Noni is cleared for general availability and paid marketing campaigns.**

---

# Sprint 27: Automated Gap Closure — All Remaining Code/Script Items (CLOSED)

**Tag:** `sprint-27-auto-closeout`. **Fully automated — zero human intervention required.** All tasks are code changes, scripted verification, or automated tests. Documentation items (Q5, Q7) and CI-billing-blocked items (M4, M5, #91) are intentionally excluded and deferred to human-led Sprint 28.

**Goal:** Close every remaining automatable gap from the 100-point audit and SRE readiness assessment in one concurrent pass.

**Status:** All code/script tasks completed. Post-sprint top-3 enterprise fixes applied (circuit breaker metrics, JWKS stale-while-revalidate, error-log sampling bypass).

---

## Projected Grade Impact

| Domain | Current | After Sprint 27 | Delta |
|:---|:---:|:---:|:---:|
| Trust Architecture & Secure Gatekeeping | 20 / 25 | **24 / 25** | +4 |
| Quality, Scalability & State Resiliency | 19 / 25 | **24 / 25** | +5 |
| Operational Telemetry & Silent Failure Defenses | 19 / 25 | **24 / 25** | +5 |
| Operational Blindspot Assessment | 12 / 25 | **19 / 25** | +7 |
| **TOTAL** | **70 / 100 (B-)** | **91 / 100 (A-)** | **+21** |

**Remaining after Sprint 27 (human-only or billing-blocked):**
- Q5 Incident response runbook (documentation — human writing)
- Q7 SOPS paper backup (physical action)
- M4 Staging/prod isolation in CI (billing blocked)
- M5 CI security scanning (billing blocked)
- #91 Container vulnerability scanning in CI (billing blocked)

---

## Parallel Workstreams

### Workstream A — Backend Resilience (Backend engineer × 1)
All items are independent code changes; no cross-dependencies.

- **27.1 H3 — Circuit breakers on Clerk + Stripe:** Add `pybreaker==1.0.0`. Wrap `ClerkAuthProvider.fetch_user_profile`, `StripePaymentProvider.verify_webhook`, `create_checkout_session`. Config: `fail_max=5`, `reset_timeout=30`. Open-state returns `503 billing.transient_unavailable`.
- **27.2 H4 — Celery + Redis background queue:** Add `celery[redis]==5.3.0`. Provision Fly Redis via `fly redis create` (scripted). Create `backend/tasks/` with three task types: `process_stripe_webhook`, `export_telemetry_csv`, `cleanup_deleted_accounts`. Update route handlers to enqueue and return `202 Accepted` + `task_id`.
- **27.3 M3 — Stripe webhook replay protection:** Create `webhook_events` table (`event_id` PK, `processed_at`). In `stripe_webhook`, check existence → return `200` for duplicates. TTL = 24h via `pg_cron`.
- **27.4 M1 — Checkout idempotency keys:** Create `idempotency_keys` table (`key` PK, `outcome_json`, `created_at`). Accept `Idempotency-Key` header on checkout creation. Return cached response for duplicates; TTL = 24h.
- **27.5 H5 — Strict query param validation:** Audit all public GET endpoints. Replace bare `str`/`int` query params with `Query(..., max_length=..., pattern=..., ge=..., le=...)`. Add `ParamModel` where multiple query params are grouped.
- **27.6 H2 — API versioning `/api/v1/`:** Move all public routers under `/api/v1/`. Preserve `/api/` as `302` redirect with `Deprecation` header (`Sunset: <date>`). Update `frontend/src/api/client.ts` base URL. Update E2E tests.

### Workstream B — Metrics & Observability (Backend engineer × 1)

- **27.7 SRE-H1 — Prometheus metrics endpoint:** Add `prometheus-client`. Expose `/metrics` with: `noni_http_requests_total`, `noni_http_request_duration_seconds`, `noni_db_pool_connections`, `noni_active_sessions`, `noni_auth_outcomes_total`.
- **27.8 Q3 — JWKS cache TTL + monitoring:** Add `cache_ttl=3600` to `PyJWKClient`. Add Prometheus counter `clerk_jwks_rotation_events_total`. Log warning on key rotation detection.
- **27.9 #92 — Log sampling controls:** Update structured JSON logger: 100% of `error`/`warn`, 10% of `info` request logs, 0% `debug`. Add `LOG_SAMPLING_RATE` env var.

### Workstream C — Edge Security & Infrastructure Verification (Infra engineer × 1)

- **27.10 Q2 + S6 — Cloudflare WAF deploy + Stripe IP allowlisting:** Run `wrangler deploy` (or Terraform) for `infra/cloudflare/waf-rules.json`. Add rule restricting `/api/billing/stripe-webhook` to Stripe published IP ranges. Verify via Cloudflare analytics API for non-zero "Blocked requests".
- **27.11 Q1 — Verify/enforce Supabase `sslmode=require`:** Script inspects `DATABASE_URL` in Fly secrets. If `sslmode=require` absent, updates string and redeploys. Exits 0 if already present.
- **27.12 Q4 — Sessions table audit (execute):** Run `scripts/audit-sessions-table.ps1`. If table empty, auto-generate Alembic migration to drop it. Report size + row count.
- **27.13 Q6 — Fly secrets audit (execute):** Run `scripts/audit-fly-secrets.ps1`. Report missing secrets. Do NOT auto-rotate (human confirmation required per policy).

### Workstream D — Performance & Testing (SRE/QA engineer × 1)

- **27.14 SRE-C3 — k6 load test baseline:** Add `tests/load/k6-smoke.js` with stages: 50→100→200 concurrent users against `/health`, `/api/curriculum/module-1/units`, `/auth/session`. Thresholds: p99 < 500ms, error rate < 0.1%.
- **27.15 SRE-H2 — DB query performance monitoring:** Enable SQLAlchemy query logging in staging (`sqlalchemy.engine` INFO). Add `EXPLAIN ANALYZE` audit script for top 5 endpoints. Ensure indexes on: `sessions.session_token_hash`, `accounts.auth_user_id`, `telemetry_events.created_at`, `rate_limit_counters.key`.
- **27.16 #100 — Chaos test (automated):** Script triggers `fly machine stop` mid-checkout while Playwright E2E is on `/purchase`. Verifies: (a) zero orphaned `Purchase` rows with `status='pending'` > 1h, (b) Stripe webhook retry eventually transitions to `complete`. Report exit 0/1.

---

## Sprint 27 Exit Criteria

- [x] Circuit breaker test: mock Clerk API down for 6 requests; 5th+ returns 503; recovery after 30s.
- [x] Background task test: enqueue webhook task; Redis job executes; purchase marked complete.
- [x] Webhook replay test: POST same Stripe `event_id` twice; second returns 200 with zero DB mutation.
- [x] Idempotency test: duplicate `Idempotency-Key` returns identical response; no duplicate `Purchase`.
- [x] Query param test: `?page=-1` or `?search=<script>` → 422 with clear error.
- [x] API versioning test: E2E passes against `/api/v1/`; `/api/health` still responds; `/api/` redirects.
- [x] Prometheus `/metrics` returns all five declared metrics with non-zero counts.
- [x] JWKS cache test: simulate rotation; new key accepted within 60s; metric incremented.
- [x] WAF verification: request from non-Stripe IP to `/api/billing/stripe-webhook` → blocked (403/Challenge).
- [x] SSL mode verification: script reports `sslmode=require` present in production `DATABASE_URL`.
- [x] Sessions audit: table size reported; migration generated if empty.
- [x] Fly secrets audit: script executed; report saved to `docs/operations/secrets-audit-2026-05.md`.
- [x] k6 load test: passes at 200 concurrent users with p99 < 500ms.
- [x] Chaos test: zero orphaned purchases; webhook retry succeeds.
- [ ] Final 100-point audit re-run: target **≥ 85 / 100** (deferred to Sprint 28 human validation).

---

## Items Intentionally Excluded (Require Human Action or External Fix)

| Item | Why Excluded | Deferred To |
|:---|:---|:---|
| **Q5** Incident response runbook | Requires human writing, review, sign-off | Sprint 28 (documentation sprint) |
| **Q7** SOPS age key paper backup | Physical action; cannot be scripted | Sprint 28 |
| **M4** Staging/prod CI isolation | GitHub Actions billing blocked | Post-billing restoration |
| **M5** CI security scanning (`bandit`, `npm audit`, `truffleHog`) | GitHub Actions billing blocked | Post-billing restoration |
| **#91** Container vulnerability scanning (`trivy`) | Requires CI docker-build job; billing blocked | Post-billing restoration |

---

## Sprint 28 — AI Slop Audit Closure (2026-05-26)

Four concurrent sub-sprints addressing the 100-point AI Slop Audit. Heavy/high-regression items deferred to a separate **Heavy Sprint** (md not yet written; pending user authorization).

### Rollup

| Sprint | Done | Deferred → Heavy | Status |
|:---|:---|:---|:---|
| **28-A** Backend Security & Resilience | 10/10 | 0 | ✅ CLOSED |
| **28-B** Frontend Performance & Reliability | 6/10 | 4 | ✅ Non-deferred items closed |
| **28-C** Data Architecture Modernization | 3/7 + scaffold | 3 | ✅ Non-deferred items closed |
| **28-D** UI/UX & Accessibility Polish | 9/9 | 0 | ✅ CLOSED |
| **Total** | **28/36 (78%)** | **7** | Sprint 28 closed; Heavy Sprint deferred |

### 28-A: Backend Security & Resilience — CLOSED ✅
- HSTS header in `SecurityHeadersMiddleware` (production-gated)
- Hard-coded `DATABASE_URL` default removed (`config.py`)
- `Cache-Control: public, max-age=300` on `/landing/page`, `/landing/steps`, `/ui-envelope/{id}`
- Strict `TelemetryPayload` (RootModel of primitive JSON) replaces `dict[str, Any]` in `signals.py`
- Graceful shutdown + `statement_timeout=30000` verified already in place

### 28-B: Frontend Performance & Reliability — Closed except Heavy items
- React `lazy()` + `Suspense` for 6 non-landing views
- Axios fully replaced with native `fetch` (`FetchClient` class, drop-in API surface)
- `LoadingSkeleton` contract-compliant PendingBanner pattern
- `EmptyState` reusable component
- View persisted in `sessionStorage` for refresh resume
- Structured `logger` with `VITE_LOG_LEVEL` gating; `console.*` migrated
- **Deferred → Heavy Sprint:** AuthProvider/CurriculumRenderer/LessonRenderer unit tests; inline `CSSProperties` extraction (~14 files)

### 28-C: Data Architecture — Closed except Heavy items
- `numpy` dead dependency removed
- `sa_inspect` reflection replaced with `TelemetryEventOut` Pydantic model
- `Account.purchases` + `Account.entitlements` SQLAlchemy relationships (back_populates)
- `CurriculumLoader` scaffold (`backend/content/curriculum_loader.py`)
- **Deferred → Heavy Sprint:** split 926-line `curriculum.py`; extract content to JSON/YAML; delete `curriculum_units_module_*.py` duplicates

### 28-D: UI/UX & Accessibility Polish — CLOSED ✅
- Skip-to-content link (contract-compliant via `clip-path`, no spatial movement on focus)
- Icon-only buttons: N/A — CONTRACT Section I.E prohibits icons in V1
- Focus rings: already in `styles.css:25-29` (2px muted-blue + 2px offset per CONTRACT Section II)
- `aria-live`/`aria-busy` regions on all async forms and pending banners
- Color contrast audit: **FIXED** via ADR 0026. `accentDesatGreen` darkened to `#4A6D5C` (~4.6:1), `errorConfirm` darkened to `#A84C4C` (~4.5:1). `accentMutedAmber` restricted to non-text decorative use per CONTRACT Section I.E. Both geragogy research (C5, C1, Formosa & Fragoso) and ADR 0007's WCAG 2.1 AA commitment now satisfied.
- Form field error association: `aria-invalid` + `aria-describedby` on `SignInPage` and `GiftRedeemPage`
- Keyboard nav for menu: N/A — `CurriculumMenu` is read-only syllabus; only NavBar buttons are interactive (keyboard-accessible by default)
- Reduced-motion media query: already in `styles.css:37-45`
- Screen-reader empty-state announcements via `role="status"` on `EmptyState`

### Contract Violations Discovered and Fixed (mid-sprint self-audit)

Three CONTRACT.md violations were introduced and then fixed during Sprint 28-B/D before sprint closure:

| Violation | Source | Section | Fix |
|:---|:---|:---|:---|
| Non-palette gray `#e5e7eb`, pulsing animation, `ease-in-out`, "Skeleton" not in V1 inventory | `LoadingSkeleton.tsx` | I.A, I.G, I.D | Reframed as PendingBanner with palette tokens, no animation |
| Pure white `#ffffff` button text | `EmptyState.tsx` | I.A | Use `COLORS.surface` (`#FAFAF8`) |
| Pure black/white + spatial movement on focus (`left: -9999px → 8px`) | `App.tsx` skip-link | I.A, II | Reframed via `clip-path` size-collapse pattern; palette colors only |

These violations and fixes are the seed material for the forthcoming **Anti-Slop Skill** (planned but not yet authored, pending user authorization).

### Deferred Items — Heavy Sprint Inventory (md NOT yet written)

7 items deferred due to high regression risk or large surface area:

1. **28-B.3** AuthProvider unit tests
2. **28-B.4** CurriculumRenderer unit tests
3. **28-B.5** LessonRenderer unit tests
4. **28-B.6** Replace inline `CSSProperties` with extracted style modules (~14 files)
5. **28-C.4** Split 926-line `backend/api/routes/curriculum.py` into per-module route files
6. **28-C.5** Extract curriculum content to JSON/YAML; wire `CurriculumLoader`
7. **28-C.7** Delete duplicate `backend/models/curriculum_units_module_*.py` files
