# Preflight — B2B2C-IMPL-001: Organization sponsorship and access codes

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-b2b2c-impl-001.md`  
**Date:** 2026-08-27

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 1 | Intake approved | GO | Product | `2026-08-27-b2b2c-impl-001.md` |
| 2 | GTM-001 research exists | GO | Product | `GTM_RESEARCH_001.md` |
| 3 | Mock payment flow stable | GO | Engineering | ADR 0021/0022 committed |
| 4 | Entitlement service exists | GO | Engineering | `backend/services/entitlements.py` |
| 5 | Billing models extensible | GO | Engineering | `backend/models/billing.py` |
| 6 | Frontend paywall exists | GO | Engineering | `PaywallPage.tsx` |
| 7 | Database migrations possible | CAUTION | Engineering | Add `organizations`, `org_licenses`, `access_codes` |
| 8 | Admin auth surface missing | CAUTION | Engineering | Needs admin gating or staff-only endpoints |
| 9 | Scope controlled | GO | Product | No public org self-signup; no admin dashboard in v1 |

## Go / no-go

**GO** for Phase 1 (data model + backend endpoints). No-go for public admin dashboard in this phase.

## Known risks

1. **Data model:** org licensing introduces new tables and a migration. Backward compatibility with existing B2C purchases is required.
2. **Code entry surface:** must not confuse B2C users; keep it as a secondary option on the paywall.
3. **Security:** access codes can be guessed or brute-forced if too short. Use long random tokens (>= 32 chars) with rate limiting.
4. **Audit:** every org redemption must produce a billing audit event.
