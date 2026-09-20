# PS-BID17-008 — Retell agent live-answer path unverified (budget-gated)

**Status:** owner-gated | **Severity:** P1 verification gap
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

## Acceptance

- Owner (or delegate) clicks the widget once on `/caregiver` and once
  on `/for-communities`; confirms the correct persona agent answers.
- Optional: one call to the toll-free line confirms the voice path.
