# PS-BID17-033 — /purchase/cancel copy is persona-wrong for gift cancels

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** scoped
**Persona:** SHARED — learner self-purchase AND caregiver gift checkout.
**Skill check:** `journey-loop-guard` already satisfied (PS-BID17-032);
this ticket is copy-only, but the surface is shared — persona rules apply.

## Problem statement

`/purchase/cancel` always says: *"You can keep using the free modules
for as long as you like, and you can choose to purchase again at any
time."* That copy is written for the **learner** who cancelled their own
checkout. A **caregiver** who abandoned a *gift* checkout sees the same
words — "free modules" and "purchase again" are learner-track language
on a surface the caregiver also lands on.

Confirmed in code: single copy path, no `is_gift` branch
(`PurchaseCancelPage.tsx` body text, all modes).

## Options

- **A — is_gift query-param copy split.** Stripe cancel_url can carry
  `?is_gift=true`; page branches copy: gift → "The gift was not
  purchased. Nothing was charged — you can try again whenever you're
  ready." + home/back CTA. Matches PurchaseSuccessPage's existing
  `is_gift` param pattern.
- **B — Neutralize the copy.** Rewrite so it serves both: "Nothing was
  charged. You can pick this up again whenever you're ready." —
  single string, no param.
- **C — Route gift cancels elsewhere.** More plumbing than the
  problem deserves.

Jev call (jev-1.13.0): **A — is_gift branch** picked. Neutral copy
scored only 0.55 sufficient and 0.68 risk of weakening the learner's
'free modules' reassurance; the param pattern already exists on
PurchaseSuccessPage. Importance: matters (1.77).

## Edge cases

- `is_gift` param is URL-spoofable — harmless here (copy only, no
  entitlement logic depends on it).
- Entitlement probe behavior (PS-BID17-032) unchanged by copy split.
- Keep geragogy tone rules — calm, no urgency, no blame.

## Acceptance criteria

- [ ] Gift-cancel mode no longer shows "free modules" learner copy.
- [ ] Self-purchase cancel copy unchanged (or neutralized per pick).
- [ ] Same-commit unit pin on the copy branch.
