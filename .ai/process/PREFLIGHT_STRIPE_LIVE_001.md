> **Deprecated:** legacy platform retired; production runs on Railway.

# Preflight — STRIPE-LIVE-001: Production Stripe + mynaani.com

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-stripe-live-001.md`

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 1 | Intake approved | GO | Product | `2026-08-27-stripe-live-001.md` |
| 2 | Stripe account exists | HOLD | Product | Need live Stripe account created |
| 3 | mynaani.com DNS in Cloudflare | HOLD | Product | Confirm Cloudflare nameservers and records |
| 4 | Mock payment flow proven | GO | Engineering | ADR 0021 / B2B2C-IMPL-001 merged |
| 5 | Payment provider abstraction ready | GO | Engineering | `backend/services/payment_provider.py` supports `stripe` |
| 6 | Build verification script exists | GO | Engineering | `frontend/scripts/verify-bundle.mjs` |
| 7 | Secrets management plan | HOLD | Product | Need target platform (Railway/legacy-platform/Cloudflare) |

## Go / no-go

**HOLD** for two external gates: Stripe account and Cloudflare DNS. Once those are available, go for implementation.

## Open questions

1. Is the backend staying on Railway or the legacy platform?
2. Is the frontend static on Cloudflare Pages or a Railway/legacy-platform container?
3. Do we use `api.mynaani.com` or `mynaani.com/api`?
4. Is the Stripe account under the business entity that owns mynaani.com?
5. Tax / 1099-K / VAT handling for $39 and $59 products?
