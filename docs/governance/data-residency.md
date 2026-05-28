# Data Residency Statement

**Version:** 1.0.0
**Status:** PENDING VERIFICATION

---

## Current Status

The Supabase project region has not been explicitly verified in the deployment configuration. This document will be completed once the region is confirmed.

## Intended Statement (Template)

> "Noni stores learner data in [REGION] via Supabase (PostgreSQL on AWS [REGION]). Backups are stored in Cloudflare R2 in [R2 REGION]. All data remains within [JURISDICTION] boundaries."

## Verification Steps

1. Log into Supabase Dashboard
2. Navigate to Project Settings -> Infrastructure
3. Note the region (e.g., `us-east-1`, `eu-west-1`, `ap-southeast-1`)
4. Update this document with the confirmed region
5. Add the statement to `frontend/public/privacy.html`

## Related Documents

- `docs/governance/data-classification-policy.md`
- `docs/governance/data-retention-policy.md`
- `frontend/public/privacy.html`
