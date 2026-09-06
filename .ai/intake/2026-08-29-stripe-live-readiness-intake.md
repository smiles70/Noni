# Intake — Stripe Live Readiness for First Paying Customer

**Date:** 2026-08-29  
**Requester:** Product / Engineering  
**Process:** v9.51  
**Scope:** Move Mynaani's production payment flow from `mock` to live Stripe, operationalize Redis/Celery, and end-to-end verify the first real purchase, gift, and refund on `www.mynaani.com`.  
**Derived from:** Process v9.51 discovery scan and `docs/design/payment-flow.html` current vs target flow.

---

## Motivation

The payment provider abstraction and Stripe code path are complete, but `noni-api-production.up.railway.app` is still running `PAYMENT_PROVIDER=mock`. The first paying customer cannot transact until live Stripe keys, a live product/price, webhook registration, Redis-backed Celery, product seeding, and domain-aligned redirect URLs are in place.

---

## Batched Requirements

Each batch groups items that can be completed together without conflict. Batches are ordered by dependency.

### Batch A — Stripe Account and Product (external, product/owner)

| # | Item | Evidence target |
|---|------|-----------------|
| 1 | Create or confirm the live Stripe account under the Mynaani business entity. | Stripe dashboard account active. |
| 2 | Complete activation (bank account, tax info, identity verification). | Account status = "enabled" in Stripe. |
| 3 | Create the live product "Mynaani Modules 4-5" in Stripe. | Product ID `prod_...` documented. |
| 4 | Create a one-time USD price for the self-purchase tier. | Price ID `price_...` documented. |
| 5 | Create a one-time USD price for the caregiver-gift tier (or decide to use one price). **Warning:** `create_checkout` in `backend/api/routes/billing.py` always charges `product.stripe_price_id` regardless of `is_gift`; a separate gift price requires a code change before it can be charged. | Price ID(s) documented; decision recorded. |
| 6 | Decide final published price (self-purchase and gift) and update ADR 0021 if the numbers change. | ADR 0021 amended or intake note. |

### Batch B — Live Secrets in Railway Production (infra/owner)

| # | Item | Evidence target |
|---|------|-----------------|
| 7 | Set `PAYMENT_PROVIDER=stripe` in Railway production variables. **Ordering constraint:** this flip must happen only AFTER `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` are both set — `StripePaymentProvider.__init__` raises `RuntimeError` on empty secrets, which would 500 every billing endpoint (including `/health`). | `GET /api/v1/billing/health` returns `provider: stripe`. |
| 8 | Set `STRIPE_SECRET_KEY=sk_live_...` in Railway production variables. | Health endpoint reports `stripe_mode: live`. |
| 9 | Set `STRIPE_WEBHOOK_SECRET=whsec_...` in Railway production variables. | Webhook verification passes. |
| 10 | Set `STRIPE_PRICE_ID_MODULES_4_5` to the live self-purchase price ID. | `checkout` creates a Stripe session with the correct price. |
| 11 | Set `STRIPE_SUCCESS_URL=https://www.mynaani.com/purchase/success` (clean, no query params). | Stripe redirect lands on the success page. |
| 12 | Set `STRIPE_CANCEL_URL=https://www.mynaani.com/purchase/cancel`. | Cancel returns to the cancel page. |
| 13 | Set `FRONTEND_URL=https://www.mynaani.com` for any backend-initiated redirects. | Any redirect uses the right origin. |

### Batch C — Database Product Row (engineering)

| # | Item | Evidence target |
|---|------|-----------------|
| 14 | Resolve the `_seed_dev_products` vs `scripts/seed_products.py` data drift (`display_name`, `price_cents`, `content_version`). | Single source of truth documented. |
| 15 | Run `python -m scripts.seed_products` in the production Railway environment. | `products.code='modules_4_5'` row exists with correct `stripe_price_id`. |
| 16 | Remove or gate the `_seed_dev_products()` runtime seed so it does not re-run in `mock` mode during production boot (it already only runs when `PAYMENT_PROVIDER=mock`, but can race). | No duplicate-key race in production logs. |
| 17 | Back up the production `products` table before the seed run. | Backup label or `pg_dump` artifact. |
| 18 | Verify the `modules_4_5` product is `active=true` and has the live `stripe_price_id`. | Row query. |

### Batch D — Webhook and Celery Infrastructure (engineering)

| # | Item | Evidence target |
|---|------|-----------------|
| 19 | Provision a Redis broker in Railway (or Upstash) and set `REDIS_URL` for production. | `REDIS_URL` is non-empty and reachable. |
| 20 | Register the Stripe webhook endpoint `https://noni-api-production.up.railway.app/api/v1/billing/stripe-webhook` with events `checkout.session.completed` and `charge.refunded`. **Must use the `/api/v1/` path** — the legacy `/api/billing/stripe-webhook` returns a 302 redirect, which Stripe does not follow, so deliveries would silently fail. `docs/stripe-setup.md` and `infra/scripts/stripe-bootstrap.sh` still reference the legacy path and need correcting. | Webhook endpoint listed in Stripe dashboard with the v1 URL. |
| 21 | Deploy a Railway worker service or start command that runs `celery -A backend.tasks.celery_app worker`. | Worker process visible in Railway logs. |
| 22 | Verify the webhook route enqueues `process_stripe_webhook` and the worker executes it. | `processed_webhook_events` table populated. |
| 23 | Add Cloudflare WAF allowlist for Stripe webhook IP ranges (Sprint 25.2). | `/api/v1/billing/stripe-webhook` blocks non-Stripe IPs. |

### Batch E — Domain, CORS, and Frontend Build (engineering)

| # | Item | Evidence target |
|---|------|-----------------|
| 24 | Confirm `CORS_ORIGINS` includes `https://mynaani.com` and `https://www.mynaani.com`. | Preflight `OPTIONS` calls succeed. |
| 25 | Confirm the Cloudflare Pages build uses `VITE_API_BASE_URL=https://noni-api-production.up.railway.app`. | No `noni-api.fly.dev` or `localhost` references in the bundle. |
| 26 | Confirm `https://www.mynaani.com/purchase/success` and `/purchase/cancel` routes render correctly. | Manual visit returns 200. |
| 27 | Confirm `mynaani.com` apex forwarding to `www.mynaani.com` is stable. | Both origins load the app. |

### Batch F — End-to-End Verification (QA)

| # | Item | Evidence target |
|---|------|-----------------|
| 28 | Self-purchase smoke test: use Stripe test card, pay, return to app, and confirm entitlement is granted within 30 seconds. | `Entitlement` row created and paywall removed. |
| 29 | Gift-purchase smoke test: buy as gift, receive gift token, redeem with a second account, and confirm entitlement. **Blocked by a code defect (see "Defects discovered" below):** in live Stripe mode the gift token is lost during the Stripe redirect, so the buyer never sees the code. The defect must be fixed before gift sales go live; only self-purchase can launch without it. | Gift claim succeeds after the defect is fixed. |
| 30 | Refund smoke test: issue a refund in Stripe dashboard, confirm `charge.refunded` is received and entitlement is revoked. | `Entitlement.revoked_at` is set. |

---

## Defects discovered during triple-check (require code fixes before full launch)

| ID | Defect | Impact | Where |
|----|--------|--------|-------|
| D1 | Gift token lost in live Stripe flow. `PaywallPage.tsx` appends `gift_token` to the Stripe checkout URL, but Stripe redirects back to `STRIPE_SUCCESS_URL?cs={CHECKOUT_SESSION_ID}` only — `gift_token`, `is_gift`, `purchase`, and `product` query params are all dropped. The buyer never sees the gift code. | Gift purchases unusable in live mode. Self-purchase unaffected. | `frontend/src/components/PaywallPage.tsx`, `frontend/src/components/PurchaseSuccessPage.tsx`, `backend/services/payment_provider.py` |
| D2 | Gift price never charged. `create_checkout` uses `product.stripe_price_id` for both self and gift purchases; there is no per-tier price lookup. | The $59 gift tier silently charges the self-purchase price. | `backend/api/routes/billing.py` line ~141 |
| D3 | Success page shows no product details in live mode. Stripe redirects with only `?cs=...`; the page's `product`/`provider` params are empty, so the confirmation card shows a blank product name. | Cosmetic but confusing for the customer. | `frontend/src/components/PurchaseSuccessPage.tsx` |
| D4 | Stale webhook URLs in docs/scripts. `docs/stripe-setup.md` uses `/api/billing/webhook` and `/api/billing/stripe-webhook`; `infra/scripts/stripe-bootstrap.sh` points at the retired Fly host. Both would register endpoints Stripe cannot deliver to. | Whoever follows the old docs registers a dead webhook. | `docs/stripe-setup.md`, `infra/scripts/stripe-bootstrap.sh` |

Recommended handling: fix D1–D3 in a small pre-launch sprint (backend can pass a `client_reference_id`/session lookup, or the success page can call a `GET /api/v1/billing/purchase-status?cs=...` endpoint); update D4 docs in the same change. Self-purchase-only launch is possible after Batches A–E plus item 28 without D1/D2 if the gift buttons are hidden or a decision is made to charge one price.

---

## Explicit Non-Goals

- Do not change the B2B2C organization access-code flow.
- Do not rename the product code `modules_4_5`.
- Do not add new payment providers.
- Do not build a self-service refund UI in this intake.
- Do not change the auth provider to a real identity provider in this intake (mock auth may remain for the pilot, but it is tracked separately).

---

## Success Criteria

1. `GET /api/v1/billing/health` on production returns `{"provider":"stripe","stripe_mode":"live"}`.
2. A signed-in learner on `www.mynaani.com` can buy Modules 4-5 with a real card.
3. A learner can buy the same product as a gift and a second account can redeem it.
4. A refund in the Stripe dashboard revokes the learner's entitlement.
5. The production bundle contains no `noni-api.fly.dev` or `localhost` references.

---

## Open Questions

1. What is the final approved price for self-purchase and the gift tier?
2. Is the Stripe account under the same business entity that owns `mynaani.com`?
3. Will Celery run as a separate Railway service or as an additional start command on the existing API service?
4. Should staging remain on `STRIPE_SECRET_KEY=sk_test_...` permanently?
5. Who holds the SOPS age key to update `infra/.env.prod.sops.yaml` if that file is still the source of truth?

---

## Dependencies and Batching Logic

- **Batch A** is external and blocks everything else.
- **Batch B** can be done as soon as Batch A gives the price/webhook IDs.
- **Batch C** and **Batch D** are independent of each other once Batch B is done, but both must finish before end-to-end verification.
- **Batch E** can proceed in parallel with C and D because the live API is not required for bundle/domain checks.
- **Batch F** requires all prior batches to be complete.
