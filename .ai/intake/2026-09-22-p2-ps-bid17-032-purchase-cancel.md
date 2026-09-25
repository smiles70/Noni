# PS-BID17-032 — /purchase/cancel restyle + entitlement-check fix (SHARED)

**Date:** 2026-09-22 · **Priority:** P2 · **Parent:** PS-BID17-028
**Persona:** SHARED — learner self-purchase AND caregiver gift checkout.
**Skill check:** `journey-loop-guard` (purchase-cancel — mandatory;
guard rule: must not route entitled learner back to paywall).
Jev plan gate: entitlement check right fix **0.56** (hedged —
implement conservatively: suppress the CTA when entitled, don't
re-route silently).

## Problem statement

Two issues on one 46-line page:
1. Pre-bid-17 AccountStyles grammar (drift).
2. **Guard exposure:** "Return to paywall" CTA fires unconditionally.
   An entitled learner who cancels a stray checkout gets offered the
   paywall — a loop the guard explicitly forbids.

## Must preserve / fix

- Keep "Continue with free modules" → `/curriculum`.
- FIX: check entitlement (billing status endpoint already used by
  PurchaseSuccessPage family); if entitled → suppress the paywall CTA
  (show paid-track continue instead), if not → keep `/paywall`.
- Aligned-neutral grammar (shared surface — Jev pick).

## Edge cases

- Entitlement check failure → fail-safe to current behavior
  (show paywall CTA) — cancel page must never block on a network call.
- Caregiver cancelling a gift checkout has no entitlement — paywall
  CTA is still wrong for them? No: cancel is shared but the gift
  checkout cancel lands here too; caregiver sees "free modules" copy —
  copy audit needed for the gift-cancel mode (note in implementation).

## Acceptance criteria

- [ ] Entitlement-aware CTA — no paywall loop for entitled learners.
- [ ] Fail-safe on entitlement check error.
- [ ] Aligned-neutral grammar; same-commit unit + e2e pins.
