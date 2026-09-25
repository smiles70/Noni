# PS-BID17-008 — Retell agent live-answer path unverified (budget-gated)

**Status:** RESOLVED — owner confirmed widget answers on staging | **Severity:** P1 verification gap
**Source:** staging integration check 2026-09-20

## Problem statement

The chat widget mounts with correct persona agent IDs and the public
key is baked into the staging bundle — but nothing proves a Retell
agent actually answers. Agent-side failures (deleted agent, domain-lock
mismatch on `staging.noni-web.pages.dev`, quota exhaustion) are
invisible until someone clicks.

## Verified vs. not

- ✅ Widget script reachable (200), agent IDs per journey
  (`gift` → `agent_646d…`, `facility` → `agent_719b…`), public key
  baked, cleanup-on-SPA-nav, no-op when env unset.
- ✅ Webhook signature verification active (401 unsigned).
- ❓ Agent live answer + domain-lock acceptance on the staging domain
  (CON-BID17-K4: new domains must be registered in Retell console).
- ❓ Toll-free voice line answer path (can't dial via CLI).

## Constraints

- Shared Retell budget ~50 interactions/month (CON-BID17-K5) — each
  widget test spends budget; keep to 1–2 interactions.
- Domain-lock check is free: Retell console → agent → allowed domains
  must include `staging.noni-web.pages.dev`.

## Deep-dive findings (Retell API via token, 2026-09-20)

- Both chat agents confirmed live + persona-correct:
  `agent_646d…` = "MyNaani Chat Assistant" (gift),
  `agent_719b…` = "MyNaani Chat Assistant — Facility" — both
  llm=retell-llm, version 0 (matches baked `data-agent-version`).
- `RETELL_CALLBACK_AGENT_ID` = `agent_f475…` "Callback Assistant
  (staging)" → correctly webhooks to **staging** CRM.
- FINDING A → PS-013: both chat agents' webhooks point to **prod** CRM.
- FINDING B → PS-014: toll-free `+18774094144` has no inbound agent
  bound in Retell (receptionist agent exists but unattached).
- Recent call list shows prod callback-agent activity (`not_connected`
  ×5 — outbound attempts, not staging).

## Remaining acceptance

- One manual widget click per page (budget: 2 interactions) — confirms
  domain-lock acceptance + agent answer; still owner/manual.
- Domain-lock config lives on the publishable key in Retell console —
  not API-visible; manual check required.


Owner confirmed 2026-09-20: chat widget works on staging (agents
answer, domain-lock accepts staging.noni-web.pages.dev). Closed.
