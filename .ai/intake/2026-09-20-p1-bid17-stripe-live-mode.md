# PS-BID17-009 — Stripe live-mode proof exists only on production

**Status:** owner-gated (production promotion) | **Severity:** P1
verification gap — by design, not a defect
**Source:** staging integration check 2026-09-20

## Problem statement

Staging billing reports `provider=mock, stripe_mode=mock` — correct by
design (`MockCheckoutPage`, REQ-006 live checkout is production-only).
No staging test can prove live Stripe works; the live path is only
exercisable on production.

## Verified vs. not

- ✅ `stripe-webhook` endpoint live on staging (400 on empty body —
  signature validation engaged, not a crash).
- ✅ Gift flow entry (`/gift`, `data-gift-entry` markers) in bundle.
- ✅ `billing/health` contract present (AC-001 expects
  `provider=stripe, stripe_mode=live` on prod).
- ❓ Live-mode checkout, live webhook signature, real charge path —
  production-only by design.

## Known related gap (graph)

`GAP-001` — gift token lost in live Stripe redirect — tracked
separately; verify gift-mode `/purchase/success` attribution on the
first real live checkout.

## Acceptance

- On production promotion (owner-gated): run
  `GET /api/v1/billing/health` → expect `provider=stripe`,
  `stripe_mode=live`; verify Stripe dashboard shows the webhook
  endpoint receiving events; complete one live gift checkout
  end-to-end (owner transaction) confirming gift-mode success routing.
