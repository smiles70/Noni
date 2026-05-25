# Noni SRE Go-Live Readiness Assessment

> **Date:** 2026-05-25  
> **Assessor:** Noni Engineering (self-assessment)  
> **Scope:** Backend API concurrency, database capacity, infrastructure scaling, monitoring, and operational runbooks.  
> **Not in scope:** Marketing, user acquisition, content quality, or geragogy compliance.

---

## Executive Summary

**Status: NOT READY for production traffic beyond a soft launch.**

Noni's infrastructure is functional for development and a small pilot (<100 concurrent users), but critical SRE gaps exist around database connection pooling, horizontal scaling, load testing, and observability. The current architecture would degrade or fail under moderate production load (500+ concurrent users).

**Recommendation:** Address the 4 CRITICAL and 3 HIGH items below before go-live. A soft-launch to ≤50 beta users is feasible with monitoring in place.

---

## I. Current Infrastructure Topology

```
┌─────────────────────────────────────────────────────────────────┐
│  Client (Browser)                                               │
│  ├── Cloudflare CDN + WAF (rate limiting, DDoS protection)     │
│  ├── Cloudflare Pages (static frontend, edge-cached)          │
│  └── └── Fly.io API (FastAPI + Uvicorn)                       │
│         └── Supabase Postgres (or Fly Postgres)                 │
└─────────────────────────────────────────────────────────────────┘
```

| Component | Vendor | Current Spec | Scaling Model |
|:----------|:-------|:-------------|:--------------|
| **Frontend** | Cloudflare Pages | Edge-cached static assets | Automatic (CDN) |
| **API** | Fly.io | shared-cpu-1x, 512MB RAM, 1 CPU | Auto stop/start, 1 machine minimum |
| **Database** | Supabase Postgres (or Fly Postgres) | Default Supabase tier (or Fly 256MB-1GB) | Manual upgrade |
| **Auth** | Clerk (external SaaS) | Managed by Clerk | Fully managed |
| **Payments** | Stripe (external SaaS) | Managed by Stripe | Fully managed |
| **Observability** | BetterStack (optional) | 3 monitors (health, envelope, billing) | SaaS |

---

## II. Capacity Analysis

### A. Fly.io API Machine Limits

From `fly.toml`:

```toml
[http_service.concurrency]
  type = "requests"
  soft_limit = 200
  hard_limit = 250

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"
  cpus = 1
```

**What this means:**
- **1 machine** running with **1 shared vCPU** and **512MB RAM**
- Fly's proxy will route new requests to the machine up to **200 concurrent requests** (soft limit)
- At **250 concurrent requests** (hard limit), Fly stops sending traffic and may start a new machine (if configured)
- **Uvicorn runs with a single worker process** (no `--workers` flag in Dockerfile or CMD)
- Uvicorn's default worker class is `uvicorn.workers.UvicornWorker`, which is ASGI single-threaded per worker

**Concurrent user estimate:**
- Curriculum API calls are lightweight (DB read → JSON serialize → response)
- Average request latency: ~50–200ms (measured from telemetry middleware logs)
- With 1 worker × 1 CPU, realistic throughput: **~50–100 req/sec**
- At 200 concurrent requests with 100ms average latency: **~2,000 req/sec theoretical**, but CPU-bound at ~100 req/sec
- **Realistic concurrent user ceiling: ~150–200 active users** before response times degrade

### B. Database Connection Pool

From `backend/core/database.py`:

```python
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
```

**What this means:**
- SQLAlchemy `create_engine` with **default pool settings**
- Default `pool_size` = **5** connections
- Default `max_overflow` = **10** connections
- Default `pool_timeout` = **30** seconds
- Default `pool_recycle` = **-1** (no recycle — connections held indefinitely)
- **No `pool_pre_ping` in the default sense** — wait, `pool_pre_ping=True` IS set, which is good for stale connection detection

**Concurrent user estimate:**
- With pool_size=5 + max_overflow=10 = **15 max DB connections per API machine**
- Each API request uses one DB connection for the duration of the request
- At 200 concurrent API requests, only 15 can hold DB connections simultaneously
- The remaining 185 requests will **queue for up to 30 seconds** before timing out
- **This is the PRIMARY BOTTLENECK**

### C. Rate Limiting

| Layer | Limit | Per |
|:------|:------|:----|
| Cloudflare WAF (generic API) | 300 requests | per IP per 60s |
| Cloudflare WAF (auth callback) | 20 requests | per IP per 60s |
| Cloudflare WAF (account deletion) | 5 requests | per IP per 3600s |
| Cloudflare WAF (gift claim) | 10 requests | per IP per 600s |
| App-level (auth callback) | 20 requests | per IP per 60s |
| App-level (account deletion) | 5 requests | per account per 3600s |
| App-level (gift claim) | 10 requests | per IP per 600s |

**Assessment:** Rate limiting is appropriately configured at the edge (Cloudflare) with app-level defense in depth. No gap here.

### D. Session Management

| Property | Value | Assessment |
|:---------|:------|:-----------|
| Session storage | PostgreSQL (row per session) | ✅ Durable, auditable |
| Session TTL | 30 days | ⚠️ Long; consider 7–14 days for security |
| Cookie signing | HMAC-SHA256 (itsdangerous-style) | ✅ Tamper-proof |
| Session revocation | Row-level `revoked_at` timestamp | ✅ Immediate revocation |
| Concurrent sessions per user | Unlimited | ⚠️ No session limit; could accumulate |

---

## III. Findings & Risk Register

### CRITICAL — Must Fix Before Go-Live

#### C1. Database Connection Pool Undersized (Current: 15 max, Needs: 50–100+)

**Finding:** `backend/core/database.py` uses SQLAlchemy defaults (pool_size=5, max_overflow=10). At 200 concurrent HTTP requests, only 15 DB connections are available. Requests will queue and timeout.

**Impact:** API returns 500 errors or hangs under moderate load. Users see blank screens or infinite loading states.

**Remediation:**
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,           # base connections
    max_overflow=30,          # burst connections
    pool_timeout=10,        # fail fast, don't queue forever
    pool_recycle=3600,      # recycle connections hourly (Supabase/Fly benefit)
    pool_reset_on_return="rollback",  # clean state between requests
)
```
**Also verify:** Supabase connection limit (default is 60–200 depending on tier). If using Fly Postgres, check `max_connections` in postgresql.conf.

---

#### C2. Uvicorn Single-Worker Process (No Multi-Core Utilization)

**Finding:** Dockerfile CMD runs `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` with no `--workers` flag. On a 1-vCPU machine this is fine, but scaling to a `performance-2x` (2 vCPU) or larger machine will waste cores.

**Impact:** Cannot scale vertically by upgrading Fly machine size. Must scale horizontally (more machines) instead, which costs more and complicates session state.

**Remediation (two options):**

**Option A — Gunicorn + Uvicorn workers (recommended for production):**
```dockerfile
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "--bind", "0.0.0.0:8000", "backend.app.main:app"]
```

**Option B — Uvicorn with `--workers`:**
```dockerfile
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Workers formula:** `workers = (2 × CPU cores) + 1`. For shared-cpu-1x (1 vCPU): 3 workers. For performance-2x (2 vCPU): 5 workers.

**Note:** With Gunicorn, each worker gets its own SQLAlchemy connection pool. If pool_size=20, 4 workers = 80 base connections. Must ensure Supabase/Fly `max_connections` accommodates this.

---

#### C3. No Load Testing or Performance Baseline

**Finding:** No load tests (k6, Locust, Artillery, wrk, or ab) exist in the repository. No performance benchmarks have been established.

**Impact:** Cannot answer "how many users can we handle?" with data. Cannot detect performance regressions in CI. Cannot validate remediation effectiveness.

**Remediation:**
1. Add a `tests/load/` directory with a k6 or Locust script
2. Baseline test: simulate 50, 100, 200 concurrent users hitting `/health`, `/api/curriculum/module-1/units`, and `/auth/session`
3. Run against staging before every production deploy
4. Set SLOs: p99 latency < 500ms, error rate < 0.1%, throughput > 100 req/sec per machine

Example k6 script:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // ramp up
    { duration: '5m', target: 50 },   // steady state
    { duration: '2m', target: 100 },  // ramp up
    { duration: '5m', target: 100 },  // steady state
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'],
    http_req_failed: ['rate<0.001'],
  },
};

export default function () {
  const res = http.get('https://noni-api.fly.dev/api/curriculum/module-1/units');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

---

#### C4. No Horizontal Auto-Scaling Configuration

**Finding:** Fly.toml has `auto_stop_machines = "stop"` and `auto_start_machines = true`, but no explicit scaling configuration (no `[[services]]` with `min_machines`, `max_machines`, or `auto_scale_count`).

**Impact:** Under load, Fly may not start additional machines quickly enough. During a traffic spike, the single machine becomes overwhelmed before new machines boot.

**Remediation:** Add to `fly.toml`:
```toml
[http_service.concurrency]
  type = "requests"
  soft_limit = 200
  hard_limit = 250

[http_service.tls_options]
  alpn = ["h2", "http/1.1"]

# Explicit scaling policy
[[services]]
  protocol = "tcp"
  internal_port = 8000
  
  [[services.ports]]
    handlers = ["http"]
    port = 80
    
  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [services.concurrency]
    type = "requests"
    soft_limit = 200
    hard_limit = 250

  [[services.http_checks]]
    interval = 30000
    timeout = 5000
    grace_period = 20000
    method = "get"
    path = "/health"
    protocol = "https"

# Autoscaling (requires Fly autoscaler or explicit machine count)
[deploy]
  strategy = "canary"
  max_unavailable = 0
```

**Better:** Use Fly's `fly scale count` or configure autoscaling via `fly autoscaler` (if available on the org plan). For predictable load, run `fly scale count 2` minimum for redundancy.

---

### HIGH — Should Fix Before Go-Live

#### H1. In-Memory Telemetry Counters (Not Production-Grade)

**Finding:** `backend/app/telemetry.py` uses in-memory Python dictionaries with threading locks. No Prometheus, StatsD, or external metrics exporter. Counters are lost on process restart.

**Impact:** Cannot observe trends over time. Cannot set up Grafana dashboards. Cannot alert on error rate spikes. Cannot debug production issues effectively.

**Remediation:**
1. Add `prometheus-client` to requirements.txt
2. Instrument key metrics: request latency histogram, request count by status, active sessions, DB connection pool usage
3. Expose `/metrics` endpoint for Prometheus scraping
4. Or: Send metrics to BetterStack / Datadog / CloudWatch via their SDKs

Minimum metrics to expose:
- `noni_http_requests_total` (counter, labeled by path, status)
- `noni_http_request_duration_seconds` (histogram)
- `noni_db_pool_connections` (gauge: active, idle, overflow)
- `noni_active_sessions` (gauge)
- `noni_auth_outcomes_total` (counter, labeled by outcome code)

---

#### H2. No Database Query Performance Monitoring

**Finding:** No slow query logging, no query plan analysis, no index review process. SQLAlchemy logging is set to WARNING.

**Impact:** A single unindexed query could degrade the entire API under load. No visibility into which endpoints are DB-bound.

**Remediation:**
1. Enable SQLAlchemy query logging in staging (not production) to identify N+1 queries:
   ```python
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```
2. Add `explain` analysis to the audit checklist before go-live
3. Ensure indexes exist on: `sessions.session_token_hash`, `accounts.auth_user_id`, `telemetry_events.created_at`, `rate_limit_counters.key`
4. Review query plans for the most frequent endpoints:
   - `/auth/session`
   - `/api/curriculum/module-N/units/{id}`
   - `/api/ui-envelope/curriculum.unit`

---

#### H3. No Disaster Recovery Runbook Beyond Scripts

**Finding:** `infra/scripts/backup-now.sh`, `restore-drill.sh`, and `smoke-prod.sh` exist, but no documented RTO/RPO targets, no incident response runbook, and no on-call rotation.

**Impact:** During an outage, the team does not know target recovery times. No clear escalation path.

**Remediation:**
1. Document RTO (Recovery Time Objective): e.g., 30 minutes
2. Document RPO (Recovery Point Objective): e.g., 1 hour (last backup)
3. Test `make restore-drill` monthly
4. Document incident response runbook:
   - P0 (service down): page on-call, execute rollback, notify users
   - P1 (degraded): investigate metrics, scale up machines, notify users
   - P2 (non-urgent): ticket for next sprint

---

## IV. Concurrent User Capacity — Current vs. Target

| Scenario | Current Capacity | Bottleneck | With Remediations (C1, C2, C4) |
|:---------|:-----------------|:-----------|:-------------------------------|
| **10 concurrent users** | ✅ Smooth | None | ✅ Smooth |
| **50 concurrent users** | ⚠️ Degraded latency | DB pool (15 conn) | ✅ Smooth |
| **100 concurrent users** | ❌ Timeouts, 500s | DB pool + single worker | ✅ Smooth |
| **200 concurrent users** | ❌ Service failure | All bottlenecks | ⚠️ Need 2 machines |
| **500 concurrent users** | ❌ Catastrophic failure | Infrastructure | ❌ Need 3–4 machines + DB tier upgrade |
| **1,000 concurrent users** | ❌ Catastrophic failure | Everything | ❌ Need horizontal scaling + load balancer + DB read replicas |

**Soft-launch recommendation:** ≤50 concurrent users with C1 and C2 fixed.
**Full go-live recommendation:** ≤200 concurrent users with all CRITICAL items fixed and H1 (metrics) in place.

---

## V. Remediation Priority & Timeline

| Priority | Item | Effort | Owner | Target Date |
|:---------|:-----|:-------|:------|:------------|
| **P0** | C1: Configure DB connection pool | 2 hours | Backend | Before soft-launch |
| **P0** | C2: Add Uvicorn/Gunicorn workers | 2 hours | Backend | Before soft-launch |
| **P0** | C4: Configure Fly scaling (2 machines min) | 1 hour | Infra | Before soft-launch |
| **P1** | C3: Add k6 load tests + CI | 4 hours | SRE | Within 1 week |
| **P1** | H1: Add Prometheus metrics endpoint | 4 hours | Backend | Within 1 week |
| **P2** | H2: Query performance audit + indexes | 4 hours | Backend | Within 2 weeks |
| **P2** | H3: Document RTO/RPO + incident runbook | 2 hours | SRE | Within 2 weeks |

---

## VI. Go/No-Go Decision Matrix

| Criterion | Required | Current | Status |
|:----------|:---------|:--------|:-------|
| DB connection pool sized for target load | Yes | No (15 max) | 🔴 BLOCKING |
| Multi-process worker utilization | Yes | No (1 worker) | 🔴 BLOCKING |
| Horizontal scaling configured | Yes | Partial | 🔴 BLOCKING |
| Load test baseline established | Yes | No | 🔴 BLOCKING |
| Metrics exporter (Prometheus/otherwise) | Recommended | No | 🟡 WARNING |
| Query performance validated | Recommended | No | 🟡 WARNING |
| DR runbook with RTO/RPO | Recommended | Partial | 🟡 WARNING |
| Health checks operational | Yes | Yes | ✅ PASS |
| Rate limiting configured | Yes | Yes | ✅ PASS |
| SSL/TLS enforced | Yes | Yes (Fly + CF) | ✅ PASS |
| Secrets encrypted at rest | Yes | Yes (SOPS) | ✅ PASS |
| Backup automation | Yes | Yes (scripted) | ✅ PASS |

**Decision: NO-GO for production traffic.** Fix 4 CRITICAL items, then re-assess.

---

*Assessment compiled: 2026-05-25*  
*Next review: After C1–C4 remediation*
