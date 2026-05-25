# Noni Production Readiness Audit — 100-Point Threat Model

**Date:** 2026-05-25  
**Auditor:** Adversarial Principal Security Engineer  
**Scope:** Full-stack FastAPI + React/Vite SaaS (Post-Sprint 22)  
**Baseline:** `docs/audits/enterprise-security-threat-model-2026-05-25.md`  

---

## EXECUTIVE SUMMARY

Post-Sprint 22, Noni has closed its most egregious security holes and graduated from **"prototype masquerading as production"** to **"hardened beta with operational gaps."** The immediate critical vulnerabilities (unprotected telemetry export, hard-coded secrets, open signals ingestion, client-side info leaks) are now sealed. However, the codebase still lacks security headers, API versioning, circuit breakers, background job infrastructure, and comprehensive CI security scanning. It is ready for **limited live traffic with monitoring**, but not for a public marketing launch.

---

## READINESS GRID

| Dimension | Status | Grade | Blocker Count |
|:---|:---|:---|:---|
| Authentication & Authorization | **PROTECTED** | B+ | 1 |
| Input Validation & Injection Defense | **PROTECTED** | A- | 0 |
| Client-Side Security | **HARDENED** | B+ | 1 |
| Infrastructure & Deployment | **PARTIAL** | C+ | 4 |
| Observability & Telemetry | **OPERATIONAL** | B | 2 |
| Operational Resilience | **FRAGILE** | C | 5 |
| **OVERALL** | **HARDENED BETA** | **C+ / 59%** | **13** |

---

## PART I: CODE-LEVEL CRITICAL VULNERABILITIES & GAPS

### CRITICAL (Fixed in Sprint 22) — Historical Record

**V1. UNPROTECTED TELEMETRY EXPORT** (Criteria #1, #14, #19)
- **Location:** `backend/api/routes/telemetry_export.py`
- **Status:** CLOSED. Now gated behind `get_current_account` + `ADMIN_ACCOUNT_IDS` frozenset. Returns 403 for non-admin callers.

**V2. UNPROTECTED SIGNALS INGESTION** (Criteria #1, #9, #17)
- **Location:** `backend/api/routes/signals.py`
- **Status:** CLOSED. `get_current_account` required. Raw `dict` payload replaced with strict `TelemetryEventIn` Pydantic schema.

**V3. HARD-CODED DEVELOPMENT SECRETS** (Criteria #15, #25)
- **Location:** `backend/core/config.py`
- **Status:** CLOSED. Defaults emptied to `""`. `main.py` `_verify_production_secrets()` crashes on boot if missing, short (<32), or containing weak substrings.

**V4. CLIENT-SIDE INFO LEAK + AUTH PROVIDER ENUMERATION** (Criteria #3, #20)
- **Location:** `frontend/src/api/client.ts` + `backend/api/routes/auth.py:/config`
- **Status:** CLOSED. `console.warn` removed. `/auth/config` returns `"clerk"` unconditionally in production.

---

### HIGH — Remaining Active Risks

**H1. MISSING SECURITY HEADERS** (Criteria #12)
- **Location:** `frontend/index.html`, `backend/app/main.py`
- **Risk:** No CSP, HSTS, X-Frame-Options, X-Content-Type-Options, or Referrer-Policy. A compromised npm dependency executing XSS has no policy boundary.
- **Fix:** FastAPI middleware or Cloudflare injects `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'self'`, `Strict-Transport-Security`.

**H2. NO API VERSIONING** (Criteria #46)
- **Location:** All routers in `backend/api/routes/`
- **Risk:** Flat `/api/` namespace forces hard deploy lockstep for breaking changes. No migration path for mobile clients.
- **Fix:** Move public routes to `/api/v1/`. Preserve `/api/` as a 302 redirect.

**H3. NO CIRCUIT BREAKER ON THIRD-PARTY CALLS** (Criteria #56)
- **Location:** `backend/services/auth_provider.py:fetch_user_profile`, `backend/services/payment_provider.py`
- **Risk:** Clerk/Stripe API hangs exhaust the DB connection pool and worker processes under load.
- **Fix:** Add `CircuitBreaker` wrapper (30s open window) with degraded response.

**H4. NO BACKGROUND JOB QUEUE** (Criteria #42)
- **Location:** Entire backend
- **Risk:** Stripe webhook processing, account deletion cleanup, telemetry batching all happen inline. A slow webhook blocks the Gunicorn worker.
- **Fix:** Introduce Celery + Redis or `arq` for deferred work.

**H5. NO INPUT SANITIZATION ON QUERY PARAMS** (Criteria #9)
- **Location:** Public GET endpoints across curriculum, landing, ui-envelope
- **Risk:** Query/path parameters rely on FastAPI auto-parsing only. No explicit `Query(..., max_length=..., pattern=...)` constraints.
- **Fix:** Add strict `Query` constraints on all public query params.

**H6. GRACEFUL SHUTDOWN MISSING** (Criteria #60)
- **Location:** `backend/app/main.py`
- **Risk:** Fly.io SIGTERM kills in-flight requests mid-transaction, causing partial DB writes.
- **Fix:** Trap SIGTERM in lifespan/Gunicorn config; wait for active requests (25s ceiling).

---

### MEDIUM — Quality & Maintainability Debt

**M1. NO IDEMPOTENCY KEYS ON MUTATIONS** (Criteria #38)
- **Location:** `backend/api/routes/billing.py` (checkout creation)
- **Risk:** Double-click or retry spawns duplicate `Purchase` rows.
- **Fix:** Accept `Idempotency-Key` header; store key + outcome for 24h.

**M2. NO EXPLICIT DB QUERY TIMEOUTS** (Criteria #57)
- **Location:** `backend/core/database.py`
- **Risk:** Missing `statement_timeout` means a slow query holds a connection indefinitely.
- **Fix:** Add `connect_args={"connect_timeout": 10, "options": "-c statement_timeout=30000"}`.

**M3. WEBHOOK REPLAY PROTECTION MISSING** (Criteria #78)
- **Location:** `backend/api/routes/billing.py:stripe_webhook`
- **Status:** Partially mitigated by rate limiting.
- **Risk:** Stripe retry or replay attack can double-apply a payment.
- **Fix:** Store processed `event.id` values with 24h TTL.

**M4. NO STAGING/PROD ENVIRONMENT ISOLATION IN CI** (Criteria #76)
- **Location:** `.github/workflows/ci.yml`
- **Risk:** CI runs against generic `ENVIRONMENT=test`. No automated verification that staging and production configs differ.
- **Fix:** Add `config-smoke` job validating production env schema.

**M5. CI PIPELINE LACKS SECURITY SCANNING** (Criteria #71, #81, #99)
- **Location:** `.github/workflows/ci.yml`
- **Risk:** No SAST (`bandit`), no secret scanning (`truffleHog`), no dependency audit (`pip-audit`, `npm audit`).
- **Fix:** Add `bandit backend/`, `npm audit --audit-level=moderate`, `truffleHog filesystem .`.

**M6. FRONTEND ERROR BOUNDARIES NOT VERIFIED** (Criteria #39)
- **Location:** `frontend/src/`
- **Risk:** Clerk SDK init failure or unexpected API shape crashes React tree to a white screen.
- **Fix:** Add top-level `ErrorBoundary` with human-friendly fallback UI.

---

## PART II: TECHNICAL GAP ANALYSIS MATRIX

| Audit Point ID & Dimension | Current State | Production Target | Risk / Impact |
|:---|:---|:---|:---|
| **#12 Security Headers** | None | CSP + HSTS + frame-deny | **High** — XSS/clickjacking |
| **#46 API Versioning** | Flat `/api/` | `/api/v1/` + redirects | **High** — breaking change lockstep |
| **#56 Circuit Breakers** | Direct httpx calls | Circuit breaker + degraded response | **High** — cascade failure |
| **#42 Background Jobs** | All synchronous | Celery/arq queue | **High** — worker exhaustion |
| **#60 Graceful Shutdown** | No SIGTERM handler | Wait for in-flight + close pool | **High** — partial transactions |
| **#38 Idempotency Keys** | None | `Idempotency-Key` + 24h dedup | **Medium** — duplicate charges |
| **#57 DB Query Timeouts** | No `statement_timeout` | 30s statement timeout | **Medium** — pool exhaustion |
| **#78 Webhook Replay** | Rate-limited only | Event ID dedup 24h TTL | **Medium** — double-charge |
| **#71/99 CI Security** | Lint + type-check | SAST + secret scan + dep audit | **Medium** — supply chain leak |
| **#39 Error Boundaries** | Not verified | React ErrorBoundary + fallback | **Medium** — user abandonment |
| **#17 Rate Limiting** | DB-backed fixed window | Token-bucket with Redis | **Low** — burst at window edge |
| **#55 Third-Party Timeouts** | 5s Clerk timeout | 5s + circuit breaker + backoff | **Low** — transient failure amp |
| **#65 External 429 Handling** | No handling | Parse Retry-After + queue | **Low** — API rate limit violation |
| **#66 Dead Letter Queue** | None | Failed webhooks → DLQ | **Low** — lost revenue |

---

## PART III: OUTSIDE-THE-REPO OPERATIONAL BLINDSPOTS

**Q1. Is Supabase `sslmode=require` actually set in `DATABASE_URL`?**
Without it, the Postgres password traverses the internet in plaintext. A compromised transit router yields full R/W access to all learner PII and payment records. **Catastrophic single-point failure.**

**Q2. Are Cloudflare WAF rules actually deployed and active?**
`infra/cloudflare/waf-rules.json` exists locally, but if never pushed, a botnet can bypass application-level rate limits and DDoS at line rate. **Verify rule activation.**

**Q3. What happens when Clerk rotates JWKS signing keys?**
`PyJWKClient` caches in-process with no TTL. On rotation, stale keys reject legitimate users with transient 401s. For older-adult learners, "random logouts" are abandonment triggers. **Monitor and alert.**

**Q4. Is the `sessions` table still growing?**
ADR 0024 deprecated it, but a `pg_cron` cleanup job may still insert rows. On Supabase's free tier (500MB), this triggers disk-full lock, crashing the app during growth. **Check size immediately.**

**Q5. What is the verified RTO for a Supabase regional outage?**
No documented recovery time objective. No failover, no read replica, no tested point-in-time restore. **A 24-hour outage during marketing is existential.**

**Q6. Are Fly secrets rotated after the hard-coded defaults were removed?**
If production still has the old `development-secret-key-change-in-production` value, startup validation will crash the deploy. **Verify `flyctl secrets list`.**

**Q7. Is the SOPS age private key recoverable outside 1Password?**
`.sops.yaml` says keys are backed up to 1Password. If access is lost, every SOPS-encrypted secret becomes permanently unreadable. **Create offline paper backup.**

---

## PART IV: PRIORITIZED EXECUTION PIPELINE

### Immediate Mitigation (Next 24–48 Hours)
- [ ] **H1:** Add security headers middleware (CSP, HSTS, X-Frame-Options)
- [ ] **H6:** Add SIGTERM handler for graceful shutdown
- [ ] **Q6:** Verify Fly secrets do not contain old hard-coded defaults
- [ ] **M3:** Add Stripe webhook event ID deduplication (24h TTL)
- [ ] **Q4:** Check `sessions` table size; drop if unused

### Short-Term Hardening (Next 1–2 Weeks)
- [ ] **H3:** Add circuit breaker on Clerk Backend API and Stripe API calls
- [ ] **H4:** Introduce background job queue (Celery/Redis) for webhooks and exports
- [ ] **H5:** Add strict `Query(...)` validation on all public GET query parameters
- [ ] **M1:** Implement `Idempotency-Key` dedup on checkout creation
- [ ] **M2:** Add `statement_timeout=30000` to SQLAlchemy engine
- [ ] **M5:** Add `bandit`, `npm audit`, and `truffleHog` to CI pipeline
- [ ] **M6:** Add React ErrorBoundary with human-friendly fallback UI
- [ ] **Q2:** Verify Cloudflare WAF rules are deployed and logging

### Production Readiness (Pre-Scale / Pre-GA)
- [ ] **H2:** Implement `/api/v1/` versioning with `/api/` deprecation redirect
- [ ] **Q1:** Verify `sslmode=require` in all Supabase connection strings
- [ ] **Q3:** Add JWKS cache TTL or metrics-based alerting on key rotation failures
- [ ] **Q5:** Document and test point-in-time restore; define RTO (1h) and RPO (15min)
- [ ] **#91:** Add container vulnerability scanning (`trivy`) to CI
- [ ] **#92:** Add log sampling/filtering to avoid cost explosion at scale
- [ ] **#100:** Run chaos test: kill a Fly machine mid-checkout, verify no orphaned purchases

---

## PART V: SYSTEMIC SCORING

| Domain | Points | Raw Score | Notes |
|:---|:---|:---|:---|
| **Trust Architecture & Secure Gatekeeping** | 25 | **17 / 25** | Auth is solid (Clerk RS256, fail-closed, discriminated errors, no CSRF, no XSS vectors). Dinged for missing security headers, no API versioning, no idempotency keys, and no BOLA hardening beyond entitlements. |
| **Quality, Scalability & State Resiliency** | 25 | **15 / 25** | Good modular boundaries, DB pooling configured, race-handled account upserts, no circular deps. Dinged for no background queue, no circuit breakers, monolithic auth files, no caching layer, and missing error boundaries. |
| **Operational Telemetry & Silent Failure Defenses** | 25 | **16 / 25** | Prometheus metrics, structured JSON logging, request ID tracing, health checks, and CI testing operational. Dinged for no circuit breaker telemetry, no DB timeout policies, no graceful shutdown, no DLQ, and missing ghost-catch-block audit. |
| **Operational Blindspot Assessment** | 25 | **11 / 25** | Fly secrets externalized, Stripe webhooks verify signatures, backups and restore drills exist in CI. Dinged for unverified WAF deployment, unknown SSL mode, no documented RTO/RPO, no container scanning, no secret rotation automation, and no chaos testing. |

### FINAL JUDGMENT

- **Trust Architecture Score:** **17 / 25**
- **Quality & Scalability Score:** **15 / 25**
- **Operational Resiliency Score:** **16 / 25**
- **Operational Blindspot Score:** **11 / 25**

# TOTAL SCORE: 59 / 100

**Grade: C+ (Hardened Beta)**

The critical security perimeter is sealed. The codebase will not leak data, accept forged sessions, or expose its auth mode. However, it is still a **synchronous, single-tenant, un-cached application** with no circuit breakers, no background job queue, and no graceful shutdown. Under production load or a third-party outage, it will cascade-fail. **Close H1, H3, H4, H6, and M5 before general availability. Close Q1, Q2, and Q5 before running paid marketing campaigns.**

*Next re-audit recommended: After Sprint 23 closure or before first paid-user onboarding, whichever comes first.*
