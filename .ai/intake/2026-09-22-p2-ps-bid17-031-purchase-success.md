# PS-BID17-031 — /purchase/success restyle (SHARED surface)

**Date:** 2026-09-22 · **Priority:** P2 · **Parent:** PS-BID17-028
**Persona:** SHARED — serves both caregiver (`isGift` → "/" CTA) and
learner self-purchase (`→ /paid-curriculum`). Not caregiver-exclusive.
**Skill check:** `journey-loop-guard` (purchase-success surface —
mandatory). Jev plan gate: safe **0.75**; grammar pick:
**aligned-neutral** — token alignment only, no annex/hero styling,
because the learner also lands here.

## Problem statement

`/purchase/success` runs pre-bid-17 AccountStyles. It is the post-Stripe
landing for both the gift checkout and self-purchase — a shared
transaction surface that must not adopt caregiver-annex styling.

## Must preserve (pinned — journey-loop-guard)

- `isGift` CTA split: gift → `/`, self → `/paid-curriculum`
- Session/entitlement confirmation flow, mock-checkout compat
- Conditional `<ChatWidget journey="gift" />` (gift mode only)
- Persona split — gift mode must not show learner-curriculum CTA;
  self mode must not show gift content

## Treatment

Aligned-neutral: MARKETING paper bg + paperCard + token-aligned CTA,
NO hero band, NO annex marketing copy. Neutral for both personas.

## Edge cases

- `isGift` detection must remain session-driven, not URL-spoofable.
- Pending/polling state (entitlement confirm) must not reflow.
- Axe exclusion precedent for widget embed applies.

## Acceptance criteria

- [ ] Aligned-neutral grammar, both modes.
- [ ] CTA split contract pinned (unit + e2e exist — keep green).
- [ ] Same-commit test pins.
