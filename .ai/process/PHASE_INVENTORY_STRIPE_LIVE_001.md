# Phase Inventory — STRIPE-LIVE-001

| # | Phase | Activity | Status | Owner | Deliverable |
|---|-------|----------|--------|-------|-------------|
| 1 | 0 | Stripe live product + price setup | Pending | Product | Live Stripe product/price IDs, tax settings |
| 2 | 1 | Secrets + environment migration | Pending | Engineering | Production .env / secrets manager entries |
| 3 | 2 | Backend Stripe mode hardening | Pending | Engineering | Verified `PAYMENT_PROVIDER=stripe` flows |
| 4 | 3 | Webhook endpoint + Celery | Pending | Engineering | Live webhook test and entitlement grant |
| 5 | 4 | mynaani.com + Cloudflare deploy | Pending | Engineering | DNS, CORS, build bundle URL updates |
| 6 | 5 | End-to-end live purchase test | Pending | QA | Real card/gift purchase through Stripe |
| 7 | 6 | B2B2C + org codes still work | Pending | QA | Redeem code with live entitlement check |
| 8 | 7 | Closeout | Pending | Process | ADR, KG update, runbook |
