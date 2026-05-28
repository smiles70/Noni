# Noni Recovery Runbook

**Version:** 1.0.0
**Owner:** SRE / Platform Engineering
**Last Reviewed:** 2026-05-28

---

## RTO / RPO Targets

| Metric | Target |
|:---|:---|
| Recovery Time Objective (RTO) | 1 hour |
| Recovery Point Objective (RPO) | 15 minutes |

---

## Scenario 1: Database Restore from Backup

**Trigger:** Data corruption, accidental deletion, ransomware.

### Prerequisites
- Latest backup confirmed in Cloudflare R2
- `pg_restore` and `psql` installed
- Fly CLI authenticated

### Procedure
1. Identify the backup to restore:
   ```bash
   wrangler r2 object list noni-backups | sort
   ```

2. Download backup:
   ```bash
   wrangler r2 object get noni-backups/noni-prod-YYYYMMDD.dump /tmp/restore.dump
   ```

3. Stop application (to prevent writes during restore):
   ```bash
   fly scale count 0 --app noni-api
   ```

4. Restore to Supabase:
   ```bash
   pg_restore --clean --if-exists \
     --dbname "$DATABASE_URL_DIRECT" \
     /tmp/restore.dump
   ```

5. Verify schema and row counts:
   ```bash
   psql "$DATABASE_URL_DIRECT" -c "\dt"
   psql "$DATABASE_URL_DIRECT" -c "SELECT count(*) FROM accounts;"
   ```

6. Restart application:
   ```bash
   fly scale count 2 --app noni-api
   make smoke-prod
   ```

---

## Scenario 2: Fly App Total Failure

**Trigger:** Fly platform outage, app won't start, machines unhealthy.

### Procedure
1. Check Fly status page: https://status.fly.io

2. If Fly platform is down:
   - Wait for Fly resolution (documented RTO not applicable -- vendor outage).
   - Communicate to users via status page.

3. If app-specific failure:
   ```bash
   fly status --app noni-api
   fly logs --app noni-api --recent
   ```

4. Restart machines:
   ```bash
   fly apps restart noni-api
   ```

5. If restart fails, rollback to last known good:
   ```bash
   fly releases list --app noni-api
   fly deploy --image noni-api:<previous_tag> --app noni-api
   make smoke-prod
   ```

---

## Scenario 3: Supabase Database Outage

**Trigger:** Supabase platform incident, connection pool exhausted.

### Procedure
1. Check Supabase status: https://status.supabase.com

2. If Supabase incident:
   - No action possible except waiting.
   - Communicate to users via status page.
   - Estimated recovery: 1-2 hours (based on historical Supabase incidents).

3. If connection pool exhausted:
   ```bash
   fly scale count 4 --app noni-api  # Distribute load
   ```

---

## Scenario 4: Clerk Auth Outage

**Trigger:** Users cannot log in; Clerk status page shows incident.

### Procedure
1. Check Clerk status: https://status.clerk.io

2. If Clerk incident:
   - Enable mock auth as emergency fallback (degrades security):
     ```bash
     fly secrets set AUTH_PROVIDER=mock --app noni-api
     fly deploy --app noni-api
     ```
   - Monitor Clerk status.
   - Revert to `AUTH_PROVIDER=clerk` when Clerk recovers.

---

## Verification Checklist

After any recovery:
- [ ] `curl https://noni-api.fly.dev/health` returns 200
- [ ] `make smoke-prod` passes
- [ ] Auth flow works (test login)
- [ ] Curriculum loads
- [ ] Checkout flow works (test mode)
