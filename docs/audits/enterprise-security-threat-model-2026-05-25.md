# Enterprise Security Threat Model & Adversarial Audit

**Date:** 2026-05-25  
**Auditor:** Automated adversarial Senior SRE / Security Architect  
**Scope:** Full-stack — backend (FastAPI), frontend (React/Vite), infrastructure (Fly.io, Cloudflare, Supabase, Stripe, Clerk)

---

## Part I: Critical Vulnerabilities & Flaws Discovered (In-Code)

### V1. UNPROTECTED TELEMETRY EXPORT — DATA EXFILTRATION GATE

**Location:** `backend/api/routes/telemetry_export.py` lines 5–8, 37–73

```python
"""Authentication is intentionally NOT enforced here. This is acceptable
in development. When auth lands (deferred vendor pass), this router
must be gated to admin-only callers."""

@router.get("/export")
def export_telemetry_json(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return all telemetry events as JSON."""
    events: List[TelemetryEvent] = list(db.execute(select(TelemetryEvent)).scalars())
    return {"count": len(events), "events": [_event_to_dict(e) for e in events]}
```

**The Risk:**  
Anyone with network access to `https://noni-api.fly.dev/api/telemetry/export` can dump the entire `TelemetryEvent` table without authentication. This table contains learner interaction data, auth session outcomes, curriculum retrieval choices, and potentially PII-adjacent metadata (IP-derived hashes, user IDs, event metadata). An attacker can enumerate user behavior patterns, identify active learners, and extract structured data for phishing or competitive intelligence. The CSV endpoint (`/export.csv`) compounds this by delivering a ready-made spreadsheet.

**The Immediate Fix:**
```python
from backend.api.deps import get_current_account
from backend.core.config import settings
from fastapi import HTTPException, status

ADMIN_ACCOUNT_IDS = frozenset(
    uuid.UUID(hex) for hex in (settings.ADMIN_ACCOUNT_IDS or "").split(",") if hex.strip()
)

def _require_admin(account: Account = Depends(get_current_account)) -> Account:
    if account.id not in ADMIN_ACCOUNT_IDS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return account

@router.get("/export", dependencies=[Depends(_require_admin)])
def export_telemetry_json(...):
```

Also add `ADMIN_ACCOUNT_IDS` to `backend/core/config.py` and `infra/.env.example`.

---

### V2. UNPROTECTED SIGNALS INGESTION — TELEMETRY POISONING

**Location:** `backend/api/routes/signals.py` lines 12–21

```python
@router.post("/user-action")
def user_action(action: UserAction) -> dict:
    record("USER_ACTION", action.model_dump())
    signals = model.update(action)
    return {"signals": signals}

@router.post("/telemetry")
def log_event(payload: dict) -> dict:
    return record(payload.get("type", "UNKNOWN"), payload)
```

**The Risk:**  
No authentication, no rate limiting, no schema validation beyond Pydantic's automatic parsing. An attacker can flood the telemetry database with synthetic events, manipulate the ISCS cognitive model's signal history, poison retrieval-choice accuracy rollups, and exhaust storage. The `dict` payload on `/telemetry` accepts any JSON shape — this is a schema-less ingestion endpoint on a public API.

**The Immediate Fix:**
1. Require `get_current_account` on both endpoints.
2. Add rate limiting per account (not just per IP).
3. Replace the `dict` payload with a strict Pydantic schema for `/telemetry`.
4. Gate `/signals/*` behind the same auth dependency used by billing.

---

### V3. HARD-CODED DEVELOPMENT SECRETS — SESSION FORGERY

**Location:** `backend/core/config.py` lines 13, 18

```python
SECRET_KEY: str = "development-secret-key-change-in-production"
SESSION_SECRET: str = "dev-session-secret-change-in-production"
```

**The Risk:**  
If the operator forgets to override `SECRET_KEY` or `SESSION_SECRET` in the Fly environment, the production instance boots with publicly known, hard-coded secrets. An attacker who discovers this (via source-code audit, misconfiguration leak, or insider threat) can forge signed session cookies. The `verify_session_cookie` function in `backend/core/security.py` uses HMAC-SHA256 keyed by `SESSION_SECRET`; with the known key, anyone can mint valid session cookies and impersonate arbitrary users.

**The Immediate Fix:**
```python
SECRET_KEY: str = ""
SESSION_SECRET: str = ""
```

Then add startup validation in `main.py`:
```python
if settings.ENVIRONMENT == "production":
    if not settings.SECRET_KEY or "dev" in settings.SECRET_KEY.lower():
        raise RuntimeError("SECRET_KEY must be set to a strong random value in production")
    if not settings.SESSION_SECRET or "dev" in settings.SESSION_SECRET.lower():
        raise RuntimeError("SESSION_SECRET must be set to a strong random value in production")
```

Generate production secrets with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

### V4. AUTHENTICATION PROVIDER ENUMERATION

**Location:** `backend/api/routes/auth.py` lines 99–104; `frontend/src/main.tsx` lines 44–48

```python
@router.get("/config", response_model=AuthConfigResponse)
def auth_config() -> AuthConfigResponse:
    return AuthConfigResponse(
        provider=settings.AUTH_PROVIDER.strip().lower(),
        version=settings.VERSION,
    )
```

**The Risk:**  
The public `/auth/config` endpoint reveals whether the backend is running `mock` or `clerk` authentication. In `mock` mode, the backend accepts any token of the form `mock:<email>`. An attacker who sees `provider=mock` (or deduces it from the frontend's `console.warn` at `client.ts:57`) can authenticate as any user without credentials by setting `localStorage.setItem("noni.mock_token", "mock:admin@noni.com")` and refreshing. Even in Clerk mode, the version string aids targeted exploitation of known CVEs.

**The Immediate Fix:**
1. Remove the `console.warn` in `client.ts` lines 57–62.
2. Return `"provider": "clerk"` unconditionally from `/auth/config` in production, or gate the endpoint behind a build-time flag.
3. Never expose the raw `AUTH_PROVIDER` string publicly.

---

### V5. NO RATE LIMITING ON CURRICULUM ENDPOINTS

**Location:** `backend/api/routes/curriculum.py` — all routes

**The Risk:**  
The curriculum module (`/api/curriculum/*`) serves the application's core content but does not apply the existing rate-limiting infrastructure (`backend/services/rate_limit.py`). An attacker can scrape the entire curriculum catalog, enumerate unit IDs, and perform timing analysis on the ISCS estimator to infer learner stability thresholds. At scale, this becomes a DDoS vector against the database and a competitive intelligence leak.

**The Immediate Fix:**
Apply per-IP rate limits to public curriculum endpoints:
```python
from backend.services.rate_limit import RateLimit, enforce, client_ip

LIMIT_CURRICULUM_PER_IP = RateLimit(
    action="curriculum", max_per_window=120, window_seconds=60
)

@router.get("/units")
def list_units(
    request: Request,
    db: DbSession = Depends(get_db),
) -> dict:
    enforce(db, LIMIT_CURRICULUM_PER_IP, client_ip(request))
    db.commit()
    ...
```

---

### V6. DUPLICATE CLERK JWT VERIFICATION PATHS

**Location:** `backend/services/auth_provider.py` lines 118–236; `backend/services/auth_verifier.py` lines 180–258

**The Risk:**  
Two parallel Clerk JWT verification implementations exist with slightly different error handling (`AuthProvider.verify_credential` returns `None` on failure; `auth_verifier.verify_token` raises `AuthError`). This is a maintenance bomb: a future JWKS rotation bugfix or algorithm policy change must be applied in both places. Divergence is guaranteed over time. The verifier also creates its own global `PyJWKClient` instance (`_clerk_jwk_client`) separate from the provider's instance, doubling JWKS cache memory and network round trips.

**The Immediate Fix:**
Consolidate on a single verification path. Remove the inlined Clerk verification from `auth_verifier.py` and delegate to a hardened, shared `ClerkVerifier` class that both the provider and the verifier import. Deprecate `auth_provider.ClerkAuthProvider.verify_credential` in favor of the verifier module.

---

### V7. IN-MEMORY TELEMETRY — BLIND FLIGHT

**Location:** `backend/app/telemetry.py` lines 56–95

**The Risk:**  
All telemetry counters are stored in process-local `defaultdict(int)` and `list` structures protected by a `threading.Lock`. On process restart (Gunicorn worker recycling, machine redeploy, crash), all counters are lost. There is no Prometheus exporter, no external time-series database, no alerting threshold. The team cannot observe auth failure spikes, rate-limit triggers, or curriculum endpoint latency degradation without logging into the machine and reading stdout. This is Stage 0 telemetry that has not graduated.

**The Immediate Fix:**
Expose a `/metrics` endpoint compatible with Prometheus (using `prometheus_client`). Replace in-memory counters with Counter and Histogram metrics. Deploy a Grafana instance or use Fly's built-in metrics integration. At minimum, ship counters to stdout in a structured format (OpenTelemetry / JSON) that a log aggregator can parse.

---

### V8. CLIENT-SIDE INFO LEAK IN BUNDLE

**Location:** `frontend/src/api/client.ts` lines 57–62

```typescript
console.warn(
  "[noni.client] build provider:",
  AUTH_PROVIDER,
  "api:",
  API_BASE_URL,
);
```

**The Risk:**  
At module load time, the frontend logs the active auth provider and API base URL to the browser console. While not a credential leak, this aids reconnaissance. Combined with the public `/auth/config` endpoint, it gives an attacker trivial confirmation of the authentication mode and backend URL. In production, this noise also pollutes support tickets and analytics.

**The Immediate Fix:**
Remove the `console.warn` entirely, or gate it behind `import.meta.env.DEV`:
```typescript
if (import.meta.env.DEV) {
  console.warn("[noni.client] build provider:", AUTH_PROVIDER, "api:", API_BASE_URL);
}
```

---

### V9. WEBHOOK ENDPOINT HAS NO IP ALLOWLISTING

**Location:** `backend/api/routes/billing.py` lines 126–146

```python
@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: DbSession = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("stripe-signature")
    provider = get_payment_provider()
    try:
        event = provider.verify_webhook(raw_body, signature)
    except WebhookVerificationError as e:
        raise HTTPException(status_code=400, detail={"envelope_id": "billing.webhook_rejected"})
```

**The Risk:**  
The Stripe webhook endpoint is public. While signature verification is correct (Stripe's `construct_event`), the endpoint still accepts any HTTP POST. An attacker can flood it with invalid requests, triggering expensive cryptographic verification on every request and creating a CPU-exhaustion DoS vector. There is no IP-based allowlisting for Stripe's known webhook IP ranges.

**The Immediate Fix:**
Add a lightweight IP pre-check before the expensive signature verification:
```python
from backend.services.rate_limit import RateLimit, enforce, client_ip

LIMIT_WEBHOOK_PER_IP = RateLimit(action="webhook", max_per_window=10, window_seconds=60)

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: DbSession = Depends(get_db)):
    enforce(db, LIMIT_WEBHOOK_PER_IP, client_ip(request))
    # Optional: also check source IP against Stripe's published ranges
    raw_body = await request.body()
    ...
```

---

### V10. TELEMETRY LOGGER ISOLATION

**Location:** `backend/app/telemetry.py` lines 37–53

```python
if not logger.handlers:
    _handler = logging.StreamHandler()
    ...
    logger.propagate = False
```

**The Risk:**  
The telemetry logger configures its own `StreamHandler` and sets `propagate=False`. In production, if the main application logger is configured to ship to a centralized log aggregator (e.g., via Uvicorn/Gunicorn log config), telemetry events will be invisible to that pipeline. They only appear on stderr/stdout. This creates a blind spot: the ops team sees application errors but never sees the telemetry counters that would have warned them about an auth failure spike.

**The Immediate Fix:**
Remove the custom handler initialization. Use the root logger or a named logger that inherits from the application's configured log hierarchy. If a custom format is required, configure it at the application bootstrap level, not inside the module.

---

## Part II: Technical Gap Analysis Matrix

| Architectural Dimension | Current "Vibe" State | Production-Ready Target | Impact/Risk Level |
|:---|:---|:---|:---|
| **Telemetry Export Auth** | No auth on `/api/telemetry/export` | Admin-only gated + audit logging | **Critical** |
| **Signals Ingestion Auth** | Open POST endpoints | Bearer-token required + per-account rate limits | **Critical** |
| **Default Secrets** | Hard-coded dev defaults in `config.py` | Startup crash if weak/blank in production | **Critical** |
| **Auth Provider Info Leak** | Public `/auth/config` + `console.warn` | Opaque provider response; no client-side leaks | **High** |
| **Curriculum Rate Limiting** | None applied | Per-IP limits on public catalog endpoints | **High** |
| **Stripe Webhook Hardening** | Signature-only verification | IP allowlisting + rate limiting + replay-idempotency | **High** |
| **Telemetry Persistence** | In-memory counters lost on restart | Prometheus/OpenTelemetry exporter + external TSDB | **High** |
| **JWT Verification Deduplication** | Two parallel Clerk paths | Single shared verifier module | **Medium** |
| **Request Tracing** | No request ID propagation | `X-Request-ID` through middleware + logs | **Medium** |
| **Input Validation** | FastAPI auto-parsing only | Explicit Pydantic constraints + Zod-like strictness | **Medium** |
| **Schema Versioning** | No API version prefix | `/v1/` prefix or Accept-version header | **Medium** |
| **Backup Verification** | Not present in repo | Automated backup + restore smoke test | **High** |
| **Incident Runbook** | Not present | Documented RTO/RPO + escalation path | **Critical** |
| **CI/CD Security** | `.github` dir present but unverified | SAST, secret scanning, dependency audit in pipeline | **High** |
| **Log Aggregation** | Stdout only | Structured JSON to aggregator (Axiom / Datadog / CloudWatch) | **Medium** |

---

## Part III: The "Outside-the-Repo" Diagnostic (Blindspots)

### Q1. Are Supabase connection strings encrypted in transit?
**What we see:** `DATABASE_URL` points to Supabase. The connection string contains the password.  
**Catastrophic consequence if unconfigured:** If `sslmode=require` is not set in the connection string, the database password traverses the internet in plaintext between Fly.io and Supabase. An attacker on the same network segment (or a compromised ISP) can sniff credentials and gain full read/write access to the entire learner database, including PII, payment records, and auth hashes.

### Q2. Is the Cloudflare WAF JSON actually deployed?
**What we see:** `infra/cloudflare/waf-rules.json` exists locally.  
**Catastrophic consequence if unconfigured:** If the WAF rules were never pushed to Cloudflare (via Terraform, Wrangler, or manual dashboard copy), the application is relying solely on application-level rate limiting. An attacker can bypass the weak DB-backed counters with a distributed botnet and DDoS the API, exhaust the Supabase connection pool, or scrape the entire curriculum catalog at line rate.

### Q3. Is the SOPS age private key recoverable if 1Password is lost?
**What we see:** `.sops.yaml` says "Private keys live at `~/.config/sops/age/keys.txt` and are backed up to 1Password."  
**Catastrophic consequence if unconfigured:** If the developer loses 1Password access (account lockout, subscription lapse, company dissolution), and the local `keys.txt` is lost, every SOPS-encrypted secret file becomes permanently unreadable. The team cannot rotate credentials, cannot decrypt production secrets, and cannot recover from a security incident requiring key revocation.

### Q4. Are Stripe webhook IPs allowlisted at the edge?
**What we see:** The webhook endpoint accepts any POST.  
**Catastrophic consequence if unconfigured:** Without IP allowlisting at Cloudflare or Fly's proxy layer, an attacker can flood the webhook endpoint with fake events. While signature verification rejects them, each request still triggers an expensive HMAC-SHA256 verification, a DB session allocation, and a 400 response. At volume, this exhausts CPU credits on `shared-cpu-1x` machines and drops legitimate checkout completions, resulting in lost revenue and learner confusion.

### Q5. What is the RTO/RPO for a Supabase outage?
**What we see:** No incident response documentation exists.  
**Catastrophic consequence if unconfigured:** If Supabase experiences a regional outage (or the free-tier project is suspended for exceeding limits), there is no documented recovery time objective. The team does not know how long learners can tolerate downtime, whether they have a point-in-time restore capability, or how to failover to a read replica. A 24-hour outage during a marketing campaign would be an existential reputation hit.

### Q6. Is the `sessions` table (unused since ADR 0024) still accumulating rows?
**What we see:** ADR 0024 migrated to Bearer tokens; the `sessions` table is "scheduled for deletion."  
**Catastrophic consequence if unconfigured:** If the old session cleanup job (or a pg_cron sweep) was never disabled, the `sessions` table may be growing indefinitely. On Supabase's free tier (500MB), this eventually triggers a disk-full condition that locks the entire database, crashing the app and preventing new account creation during a growth surge.

### Q7. Are Clerk's JWKS keys cached with a TTL, or only on-demand?
**What we see:** `PyJWKClient(jwks_url, cache_keys=True)` — the cache is in-process and unbounded.  
**Catastrophic consequence if unconfigured:** If Clerk rotates its signing keys (which they do regularly), the in-process cache holds the old key indefinitely until a token with a new `kid` arrives. During a key rotation event, legitimate users experience transient 401s on every request that hits a worker with stale keys. Without a metrics dashboard, this appears as "random logouts" and generates support tickets from confused older-adult learners who may abandon the platform.

---

## Part IV: Strategic Recommendations for Improvement

### Immediate (Next 24–48 Hours)

- [ ] **I1.** Gate `/api/telemetry/export` and `/api/telemetry/export.csv` behind admin-only auth + `ADMIN_ACCOUNT_IDS` env var.
- [ ] **I2.** Add `get_current_account` dependency to `/api/signals/*` endpoints; replace raw `dict` payload with strict Pydantic schema.
- [ ] **I3.** Replace hard-coded `SECRET_KEY` / `SESSION_SECRET` defaults with empty strings; add production startup validation that crashes on weak values.
- [ ] **I4.** Remove `console.warn` leak from `client.ts` (or gate behind `import.meta.env.DEV`).
- [ ] **I5.** Rotate `SECRET_KEY` and `SESSION_SECRET` in Fly secrets immediately.
- [ ] **I6.** Apply per-IP rate limits to all public `/api/curriculum/*` endpoints.
- [ ] **I7.** Add IP + rate-limit pre-check to `/api/billing/stripe-webhook` before signature verification.

### Short-Term (Next 1–2 Weeks)

- [ ] **S1.** Deduplicate Clerk JWT verification: create a single `ClerkVerifier` class imported by both `auth_provider.py` and `auth_verifier.py`.
- [ ] **S2.** Add Prometheus `/metrics` endpoint (Counter + Histogram) replacing in-memory telemetry counters.
- [ ] **S3.** Implement `X-Request-ID` middleware for distributed request tracing across frontend → backend → DB.
- [ ] **S4.** Add structured JSON logging (using `python-json-logger`) with request ID correlation.
- [ ] **S5.** Review and prune the unused `sessions` table and any associated cleanup jobs.
- [ ] **S6.** Add Stripe webhook IP allowlisting at the edge (Cloudflare or Fly proxy layer).
- [ ] **S7.** Harden `auth/config` to not expose raw provider string in production.

### Medium-Term (Pre-Scale)

- [ ] **M1.** Set up automated CI security scanning: `bandit` (Python SAST), `semgrep`, `npm audit`, and secret scanning (`truffleHog` or `git-secrets`).
- [ ] **M2.** Implement API versioning (`/v1/` prefix) to allow future breaking changes without client breakage.
- [ ] **M3.** Document and test backup/restore procedures with a defined RTO (e.g., 1 hour) and RPO (e.g., 15 minutes).
- [ ] **M4.** Create an incident response runbook with escalation paths, communication templates, and rollback procedures.
- [ ] **M5.** Add query performance audit + index review (Sprint 21 H2 blocker).
- [ ] **M6.** Deploy a log aggregator (Axiom, Datadog, or CloudWatch) and configure alerting on auth failure rate spikes and p99 latency degradation.
- [ ] **M7.** Conduct a tabletop exercise: simulate a secret leak (`SESSION_SECRET` exposed) and walk through full rotation + user impact assessment.

---

## Part V: Final Scoring

- **Trust Architecture Score:** **12 / 25**
  - Auth is generally well-designed (Clerk RS256, fail-closed, discriminated errors), but the unprotected telemetry export, open signals ingestion, hard-coded defaults, and info leaks are unforgivable for a SaaS handling learner PII and payment data.

- **Maintainability Score:** **14 / 25**
  - Code is well-documented with ADRs and clear module boundaries. However, duplicated JWT paths, in-memory telemetry that hasn't graduated, missing CI security gates, and no structured logging mean the codebase will collapse under operational load at 2:00 AM.

**Combined: 26 / 50** — This is a **prototype masquerading as production**. The auth and curriculum design show engineering maturity, but the security perimeter has gaping holes. Fix I1–I7 before accepting any payment data from real users.

---

---

## Appendix A: Post-Sprint 22 Reassessment

**Date:** 2026-05-25 (same day, post-implementation)  
**Items closed:** I1, I2, I3, I4, I6, I7, S1, S2, S3, S4, S7  
**Items remaining:** I5 (manual Fly secret rotation), S5 (sessions table pruning), S6 (Stripe edge IP allowlisting), M1–M7 (medium-term)

### Closed Vulnerabilities

| Vuln | Status | Fix |
|:---|:---|:---|
| V1 — Unprotected telemetry export | **CLOSED** | Admin-only via `ADMIN_ACCOUNT_IDS` + `get_current_account` |
| V2 — Unprotected signals ingestion | **CLOSED** | `get_current_account` required + strict `TelemetryEventIn` schema |
| V3 — Hard-coded secrets | **CLOSED** | Defaults emptied; `main.py` crashes on boot if weak/blank in production |
| V4 — Auth provider enumeration | **CLOSED** | `/auth/config` returns `"clerk"` unconditionally in production; `console.warn` removed |
| V5 — No curriculum rate limiting | **CLOSED** | 120/60s per-IP limits on all public `/api/curriculum/*` catalog endpoints |
| V6 — Duplicate Clerk JWT paths | **CLOSED** | New `backend/services/clerk_verifier.py` shared by `auth_provider.py` and `auth_verifier.py` |
| V7 — In-memory telemetry | **CLOSED** | Migrated to `prometheus_client` Counter/Histogram; `/metrics` endpoint exposed |
| V8 — Client-side info leak | **CLOSED** | `console.warn` removed entirely from `client.ts` |
| V9 — Webhook DoS | **MITIGATED** | 10/60s per-IP rate limit enforced *before* expensive signature verification |
| V10 — Telemetry logger isolation | **CLOSED** | Structured JSON logging via `python-json-logger`; `request_id` propagated through middleware |

### Remaining Gaps

| Gap | Risk | Path to Closure |
|:---|:---|:---|
| I5 — Secret rotation in Fly | Low (validation catches misses) | `flyctl secrets set SECRET_KEY=... SESSION_SECRET=...` then redeploy |
| S5 — Unused `sessions` table | Medium (disk-full on free tier) | Alembic migration to drop table + disable pg_cron job |
| S6 — Stripe webhook edge allowlisting | Medium (CPU DoS at volume) | Cloudflare WAF rule or Fly proxy config restricting source IPs to Stripe ranges |
| Q1 — Supabase SSL in transit | Unknown | Verify `sslmode=require` in `DATABASE_URL` |
| Q2 — Cloudflare WAF deployed | Unknown | Run `wrangler deploy` / Terraform apply and verify rule activation |
| Q3 — SOPS age key recovery | Unknown | Document offline backup procedure outside 1Password |
| Q5 — RTO/RPO documented | Medium | Create `docs/operations/incident-response-runbook.md` |
| Q6 — Sessions table growth | Medium | See S5 |
| Q7 — JWKS cache TTL | Low | `ClerkVerifier` now uses shared `PyJWKClient`; still no explicit TTL but key rotation is self-healing |
| M1–M7 — Medium-term prep | Low–Medium | Sprint 23 planning |

### Revised Scoring

- **Trust Architecture Score:** **20 / 25** (+8)
  - The critical auth perimeter holes (telemetry export, signals ingestion, hard-coded secrets, info leaks) are now sealed. The remaining trust gaps are infrastructure-level (edge allowlisting, session table hygiene, secret rotation ops) rather than code-level design flaws.

- **Maintainability Score:** **20 / 25** (+6)
  - Duplicated JWT verification eliminated, telemetry graduated to Prometheus, structured logging and request tracing in place. Remaining debt is operational (CI scanning, runbooks, backup verification) and architectural (API versioning, query indexes).

**Combined: 40 / 50** — Elevated from **prototype masquerading as production** to **hardened beta ready for limited live traffic**. The immediate security blockers are resolved. Close S5, S6, and Q5 before announcing general availability or running paid marketing campaigns.

*Audit completed 2026-05-25. Next review recommended: after Sprint 22 closure.*
