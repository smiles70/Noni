# PS-BID17-017 — PRODUCTION has no Celery worker and no Redis broker

**Status:** NEEDS OWNER ACTION — prod infra/config | **Severity:** P0 latent defect
**Source:** production cross-check 2026-09-20

## Problem statement

Production Railway project has **only `noni-api` + `Postgres`** — no
`noni-worker`, no `Redis`. Staging has all four. Code paths that call
`.delay()` on prod:

- `billing.py:226` — `process_stripe_webhook.delay()` (Stripe webhook
  deferral — raises inside the request post-signature)
- `gifts.py:87` — `send_gift_claimed.delay()` (gift redemption email)
- `webhook_handler.py:106` — `send_gift_receipt.delay()` (gift receipt)
- `telemetry.py:48` — `record_telemetry_event.delay()` (only when
  `TELEMETRY_ASYNC=True` — not set on prod, safe)

`REDIS_URL` unset → `broker_url` falls back to `redis://localhost:6379/0`
→ `.delay()` raises ConnectionError inside the request path.
`task_always_eager` is not configured, so there is no in-process
fallback.

## Current vs. latent blast radius

- `PAYMENT_PROVIDER=mock` on prod → no real Stripe webhooks → the
  billing dispatch is dormant. **The moment REQ-006 flips live, every
  webhook 500s and Stripe retries until it gives up** — verified by
  code path, not speculation.
- Gift receipt/claimed emails: mock checkout path may not reach the
  dispatch — but any path that does will error.
- `CAP-INT-WORKER` is unmet on production.

## Remediation (owner decision)

1. Provision `Redis` + `noni-worker` services in the production
   Railway project (mirror staging: same repo, worker start command,
   `REDIS_URL` auto-wired).
2. OR if deferred processing is intentionally descoped on prod: make
   `.delay()` calls graceful (try/except + synchronous fallback for
   gift emails; fail-loud for Stripe webhook).
3. Must be resolved BEFORE Stripe live mode is enabled (REQ-006) —
   webhook processing 500s otherwise.

## Acceptance

- `railway service list` (production) shows `noni-worker` + `Redis`
  Online, worker logs show `celery ready` + broker connected; OR a
  documented owner decision + code change removing dispatch.
- A test `.delay()` on prod completes without ConnectionError.
