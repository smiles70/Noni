# Noni Standard Operating Procedures (SOP)

**Version:** 1.0.0
**Owner:** SRE / Platform Engineering
**Last Reviewed:** 2026-05-28
**Review Cadence:** Quarterly

---

## SOP-01: Production Deployment

**Purpose:** Deploy new code to production safely.
**Risk Level:** Medium

### Prerequisites
- [ ] CI passed on PR (`pytest`, `npm test`, `pre-commit`)
- [ ] Required secrets present in Fly (`make secrets-audit` clean)
- [ ] Backup from within last 24 hours confirmed

### Procedure
1. **Verify preflight:**
   ```bash
   make secrets-audit
   make smoke-prod
   ```

2. **Trigger deploy:**
   ```bash
   make deploy-prod
   ```
   Runs: Supabase migrations -> Fly deploy -> Cloudflare Pages deploy -> smoke test.

3. **Monitor deploy:**
   ```bash
   fly logs --app noni-api
   ```
   Watch for `Application startup complete`.

4. **Verify post-deploy:**
   ```bash
   make smoke-prod
   curl https://noni-api.fly.dev/health
   curl https://noni-api.fly.dev/metrics
   ```

5. **Watch metrics for 10 minutes:**
   - Error rate < 0.1%
   - p99 latency < 500ms

### Rollback (if deploy fails)
```bash
fly releases list --app noni-api
fly deploy --image noni-api:<previous_tag> --app noni-api
make smoke-prod
```

---

## SOP-02: Database Backup

**Purpose:** Create a point-in-time backup.
**Frequency:** Daily automated; ad-hoc before risky operations.
**Retention:** 30 days in Cloudflare R2.
**RPO Target:** 15 minutes.

### Procedure
```bash
make backup-now
```

Verify in R2:
```bash
wrangler r2 object list noni-backups | grep "noni-prod-$(date -u +%Y%m%d)"
```

---

## SOP-03: Restore Drill (Quarterly)

**Purpose:** Verify backups are restorable.
**Frequency:** Quarterly (Jan, Apr, Jul, Oct).
**RTO Target:** 1 hour.

### Procedure
```bash
make restore-drill
```

Review output:
- Ephemeral Postgres container starts.
- `pg_restore` completes without ERROR/FATAL.
- Schema count matches production.

Document results in `docs/operations/restore-drill-YYYY-QN.md`.

---

## SOP-04: Secret Rotation

**Purpose:** Rotate a compromised or scheduled secret.
**Frequency:** Quarterly for `SECRET_KEY` and `SESSION_SECRET`; immediately if leak suspected.

### Procedure
1. Decrypt SOPS file:
   ```bash
   sops --decrypt infra/.env.prod.sops.yaml > /tmp/.env.prod
   ```

2. Generate new secret:
   ```bash
   NEW_SECRET=$(openssl rand -hex 32)
   ```

3. Update SOPS file:
   ```bash
   sops --encrypt /tmp/.env.prod > infra/.env.prod.sops.yaml
   ```

4. Set in Fly:
   ```bash
   fly secrets set SECRET_KEY="$NEW_SECRET" --app noni-api
   fly deploy --app noni-api
   ```

5. Verify:
   ```bash
   make smoke-prod
   ```

6. Shred temp file:
   ```bash
   shred -u /tmp/.env.prod
   ```

---

## SOP-05: SSL Mode Verification

**Purpose:** Ensure production DB connections enforce TLS.
**Frequency:** Monthly.

### Procedure
1. Check current Fly secret:
   ```bash
   fly ssh console --app noni-api
   echo $DATABASE_URL
   ```

2. Verify `sslmode=require` is present.

3. If missing:
   ```bash
   fly secrets set DATABASE_URL="postgresql+asyncpg://...?sslmode=require" --app noni-api
   fly deploy --app noni-api
   ```

---

## SOP-06: Dependency Security Audit

**Purpose:** Scan dependencies for known vulnerabilities.
**Frequency:** Weekly automated or manual monthly.

### Procedure
```bash
# Python
pip install safety
safety check -r requirements.txt

# Node
cd frontend
npm audit

# Container (if Trivy available)
trivy image noni-api:latest
```

---

## SOP-07: Fly Secrets Audit

**Purpose:** Verify all required secrets are present.
**Frequency:** Monthly.

### Procedure
```bash
scripts/audit-fly-secrets.ps1
```

Verify against `.env.example`:
```bash
diff <(grep -E '^[A-Z].*=' infra/.env.example | cut -d= -f1 | sort) \
     <(fly secrets list --app noni-api | tail -n +3 | awk '{print $1}' | sort)
```

---

## SOP-08: Scaling Fly Machines

**Purpose:** Increase or decrease compute capacity.
**Trigger:** Sustained CPU > 70% or latency p99 > 500ms.

### Procedure
```bash
fly status --app noni-api
fly scale count 4 --app noni-api   # Add machines
fly scale vm shared-cpu-2x --app noni-api  # Or upgrade VM
```

Scale down post-incident:
```bash
fly scale count 2 --app noni-api
```
