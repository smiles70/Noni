# PS-BID17-030 — /gift-redeem restyle (caregiver→recipient handoff)

**Date:** 2026-09-22 · **Priority:** P2 · **Parent:** PS-BID17-028
**Persona:** GIFT RECIPIENT (caregiver-side handoff) — NOT the learner
track yet; redemption converts them into an entitled learner.
**Skill check:** `geragogy` + `journey-loop-guard` (redemption surface —
mandatory). Jev plan gate: restyle safe **0.80**.

## Problem statement

`/gift-redeem` (GiftRedeemPage, auth-gated code-entry) runs pre-bid-17
AccountStyles while the caregiver path that produces the gift codes is
MARKETING. The recipient — often an older adult receiving the gift —
lands on the oldest-looking surface in the flow.

## Must preserve (pinned — journey-loop-guard)

- `RequireAuth` gate
- `onClaimed → goPaidCurriculum` — mandated post-redemption route
  (never `goCurriculum`, never `/curriculum`)
- `onBack → /paywall`, `onHelp → /help`
- Code-entry field, claim API call, error/confirmation states
- No facility/gift-pricing leakage to the recipient

## Treatment

Aligned-doorway: MARKETING paper bg + paperCard + gold CTA, no hero
band (redeem is a transaction surface, not marketing).

## Edge cases

- Guard evidence required: unit test pinning `onClaimed` route +
  e2e covering redemption CTA (already exists — keep green).
- Auth-fail state must keep calm copy (no blame).
- Widget-free — do NOT add ChatWidget (recipient is mid-transition).

## Acceptance criteria

- [ ] Aligned grammar, routing contract unchanged + pinned.
- [ ] Same-commit unit + e2e pins.
