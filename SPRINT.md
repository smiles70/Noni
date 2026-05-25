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
- [ ] All new CI jobs pass on the feature branch.
- [ ] Security headers present on every response (verified via `curl -I`).
- [ ] SIGTERM trap verified: deploy a review app, trigger `flyctl machine stop`, confirm zero 500s in-flight.
- [ ] ErrorBoundary renders correctly when a child component throws.
- [ ] `sessions` table size documented; drop migration created if unused.

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

