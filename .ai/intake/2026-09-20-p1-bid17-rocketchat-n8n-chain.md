# PS-BID17-015 — RocketChat/n8n alert chain unverified + dead N8N config

**Status:** owner-gated verification | **Severity:** P1
**Source:** staging integration check 2026-09-20

## Problem statement

RocketChat is a STANDALONE integration — the CRM service posts alerts
directly to it (inquiry/Retell call → CRM contact+task → RC
`#crm-alerts`). n8n is NOT in that chain (owner correction 2026-09-20). No test has proven the chain
fires end-to-end. Separately: `N8N_WEBHOOK_URL` + `N8N_WEBHOOK_TOKEN`
are set on the staging API and declared in `config.py` as N8N-HELP-001,
but **no backend code consumes them** — dead config that looks live.

## Verified vs. not

- ✅ Design intent documented (research memo: RC is internal-only, p19
  boundary holds — never visitor-facing).
- ❓ CRM → RocketChat alert actually fires on a real filing
  (standalone integration — CRM posts directly).
- ❓ Why `N8N_WEBHOOK_URL` exists in this repo's env with no consumer —
  removed consumer, or unfinished wiring?

## Resolution path

- Submit one real `/contact` or `/partners` inquiry on staging → check
  whether a CRM contact + `#crm-alerts` message appears.
- OR place one Retell widget/callback test → same check.
- Decide whether `N8N_WEBHOOK_URL`/`TOKEN` should be wired or removed
  (dead config invites confusion; N8N-HELP-001 may be unfinished work).

## Acceptance

- A real alert lands in `#crm-alerts` from a staging submission, or the
  gap is documented as intentional.
- N8N env vars: consumed by code or removed from staging env.
