# Noni Incident Response Runbook

**Version:** 1.0.0
**Owner:** SRE / Platform Engineering
**Last Reviewed:** 2026-05-28
**Review Cadence:** Monthly, or within 48 hours of any SEV-1/SEV-2 incident
**Related Documents:**
- `docs/ops/standard-operating-procedures.md`
- `docs/ops/incident-severity.md`
- `docs/staging-deploy.md`
- `infra/scripts/` (automation scripts)

---

## 1. Severity Classification

| Level | Name | Criteria | Response Time | Notification |
|:---|:---|:---|:---|:---|
| **SEV-1** | Critical | Service completely unavailable; all users affected; data loss possible; security breach confirmed. | Immediate (5 min) | Page on-call -> Eng Lead -> CEO |
| **SEV-2** | Major | Core feature degraded (checkout, auth, curriculum); >25% users affected; no data loss. | 15 minutes | Page on-call -> Eng Lead |
| **SEV-3** | Minor | Non-core feature affected (telemetry export, admin tools); <25% users affected; workaround exists. | 1 hour | Slack #alerts channel |
| **SEV-4** | Informational | Cosmetic issue, performance degradation within SLO, monitoring noise. | Next business day | Ticket for next sprint |

**SLO Targets:**
- p99 latency < 500ms
- Error rate < 0.1%
- 100 concurrent users supported

---

## 2. Service Overview

| Component | Technology | Vendor | Health Endpoint |
|:---|:---|:---|:---|
| API Backend | FastAPI + Gunicorn + Uvicorn | Fly.io | `https://noni-api.fly.dev/health` |
| Frontend | React + Vite | Cloudflare Pages | `https://noni-web.pages.dev` |
| Database | PostgreSQL 15 | Supabase | `/health` (DB pool check) |
| Auth | Clerk (JWT / JWKS) | Clerk | `/auth/config` |
| Payments | Stripe Checkout + Webhooks | Stripe | `/api/v1/billing/health` |
| Backups | pg_dump -> R2 | Cloudflare | `make restore-drill` (quarterly) |

**Architecture:** 2 Fly machines minimum, 3 Gunicorn workers per machine, SQLAlchemy connection pool (size=5, max_overflow=10).

---

## 3. Escalation Path

```
On-Call Engineer (primary)
    | (if no acknowledgment within 5 min OR SEV-1)
Engineering Lead
    | (if no acknowledgment within 10 min OR SEV-1)
CEO / Business Lead
    | (if security breach OR legal/compliance risk)
Legal / Compliance Officer (if applicable)
```

**On-Call Rotation:** Managed via BetterStack.
**Eng Lead:** [FILL IN]
**CEO:** [FILL IN]
**Security Contact:** [FILL IN]

---

## 4. Communication Templates

### SEV-1 / SEV-2 - Internal Slack (#incidents)
```
:rotating_light: INCIDENT ALERT - SEV-{level}
Impact: {service} is {down/degraded}
Started: {timestamp} UTC
Detected by: {alert_source}
On-call: @{engineer}
Status page: {link}
Thread for updates |
```

### SEV-1 / SEV-2 - External Status Page
```
Noni is experiencing a service disruption.
Affected: {web app / checkout / curriculum / all services}
Status: Investigating
Next update: {15 minutes from now}
Subscribe for notifications: {link}
```

### All-Clear Template
```
:green_circle: RESOLVED - {service}
Duration: {X minutes}
Root cause (preliminary): {one sentence}
Postmortem: {link to ticket}
```

---

## 5. Incident Playbooks

### 5.1 PLAYBOOK: Service Completely Down (SEV-1)

**Trigger:** `/health` returns non-200; users report site inaccessible.

**Triage (2 minutes):**
1. Check Fly app status: `fly status --app noni-api`
2. Check Fly platform status: https://status.fly.io
3. Check Cloudflare Pages: `curl -I https://noni-web.pages.dev`

**Mitigation:**
- Restart machines: `fly apps restart noni-api`
- Rollback to last known good: `fly deploy --image noni-api:<previous_tag> --app noni-api`

**Validation:**
- `curl -fsS https://noni-api.fly.dev/health | jq .status` -> `"healthy"`
- Run smoke test: `make smoke-prod`

---

### 5.2 PLAYBOOK: Auth Failure - Users Cannot Log In (SEV-1/SEV-2)

**Trigger:** `/auth/session` returning 401 for all users; Clerk status page shows incident.

**Triage (3 minutes):**
1. Check Clerk status: https://status.clerk.io
2. Check JWKS endpoint: `curl -fsS "$CLERK_JWKS_URL" | jq '.keys | length'`

**Mitigation:**
- If Clerk is down: enable mock auth (EMERGENCY ONLY):
  ```bash
  fly secrets set AUTH_PROVIDER=mock --app noni-api
  fly deploy --app noni-api
  ```
  :warning: Revert to `clerk` as soon as their service recovers.
- If JWKS rotation caused cache miss: restart backend to clear cache.

---

### 5.3 PLAYBOOK: Bad Deployment Rollback (SEV-1/SEV-2)

**Trigger:** Errors spike immediately after deploy.

**Mitigation (2 minutes):**
```bash
fly releases list --app noni-api
fly deploy --image noni-api:<previous_tag> --app noni-api
make smoke-prod
```

**Remediation:** Fix forward in feature branch, run full CI, then redeploy. Never push directly to main during incident.

---

### 5.4 PLAYBOOK: Security Incident - Suspected Breach (SEV-1)

**Trigger:** Unauthorized access detected; secrets leaked.

**Triage (5 minutes):**
1. Contain: Revoke suspected credentials immediately.
2. Check auth logs: `fly logs --app noni-api --recent | grep -i "auth"`
3. Identify scope: which data, which users, which time window.

**Mitigation:**
1. Rotate compromised secrets:
   ```bash
   openssl rand -hex 32
   fly secrets set SECRET_KEY=<new> SESSION_SECRET=<new> --app noni-api
   fly deploy --app noni-api
   ```
2. Invalidate all Clerk sessions via Clerk Dashboard.
3. Block suspicious IPs at Cloudflare WAF level.

---

## 6. Post-Incident Review (Blameless Postmortem)

**Required for:** All SEV-1 and SEV-2 incidents.

**Timeline:** Within 24 hours of resolution.

**Template:**
```markdown
# Postmortem: {Incident Title}
**Date:** {YYYY-MM-DD}
**Severity:** SEV-{level}
**Duration:** {X minutes}
**Incident Commander:** {name}

## Summary
{One-paragraph description}

## Timeline (UTC)
| Time | Event |
|:---|:---|
| HH:MM | Alert fired |
| HH:MM | On-call acknowledged |
| HH:MM | Mitigation applied |
| HH:MM | Service restored |

## Root Cause Analysis
{5 Whys analysis}

## Action Items
| # | Action | Owner | Due Date |
|:---|:---|:---|:---|
| 1 | {Specific action} | {name} | {date} |
```

---

## 7. Key Commands Reference

| Purpose | Command |
|:---|:---|
| Fly app status | `fly status --app noni-api` |
| Fly logs | `fly logs --app noni-api --recent` |
| Fly restart | `fly apps restart noni-api` |
| Fly rollback | `fly deploy --image noni-api:<tag> --app noni-api` |
| Smoke test | `make smoke-prod` |
| Backup now | `make backup-now` |
| Restore drill | `make restore-drill` |

---

## 8. Contact Reference

| Role | Name | Contact |
|:---|:---|:---|
| On-Call Primary | [FILL IN] | [FILL IN] |
| Engineering Lead | [FILL IN] | [FILL IN] |
| CEO | [FILL IN] | [FILL IN] |
| Security Contact | [FILL IN] | [FILL IN] |

**Vendor Support:**
- Fly.io: https://fly.io/support
- Clerk: https://clerk.com/support
- Stripe: https://support.stripe.com
- Supabase: https://supabase.com/support
- Cloudflare: https://support.cloudflare.com
