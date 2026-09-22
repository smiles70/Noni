# PS-BID17-029 — /gift checkout restyle (caregiver persona)

**Date:** 2026-09-22 · **Priority:** P2 · **Parent:** PS-BID17-028
**Persona:** CAREGIVER / GIFT-GIVER — NOT learner. Public page.
**Skill check:** `geragogy` (caregiver annex surface — ADR-0030 family),
`journey-loop-guard` n/a (pre-checkout). Jev plan gate run.

## Problem statement

`/gift` (GiftCheckoutPage) still renders the pre-bid-17 AccountStyles
grammar while `/caregiver` — the page that links to it — is MARKETING.
A caregiver clicking "gift" crosses a visible design seam at the exact
moment they enter a payment flow.

## Jev plan gate (jev-1.13.0)

- Restyle safe while preserving Stripe + validation: **0.59** —
  hedged; transaction surface, implement conservatively.
- Treatment: aligned-doorway pattern (precedent `/c/:slug`) — paper bg,
  paperCard panel, gold CTA. No charcoal hero band on a payment form.
- Batch risk: moderate (1.46).

## Must preserve (pinned)

- `startGuestCheckout` POST → `res.checkout_url` → `window.location.assign`
- Email validation + calm error state
- `<ChatWidget journey="gift" />` — ONE instance (see fix below)
- `<SupportContact />`, "Go back" `onBack`, honeypot-free (no form POST
  to site backend — checkout is Stripe)
- Persona: no learner-curriculum copy, no facility content

## Also fixes

- Duplicate `<ChatWidget>` mount at L120 (inside card) + L122 (outside)
  → keep the single inside-card instance.

## Edge cases

- Stripe redirect must still fire — visual change must not alter the
  submit path, disabled states, or error copy.
- Widget dedupe relies on script id — removing the duplicate React
  mount changes nothing functionally.
- Axe: `#retell-widget-root` exclusion precedent (PS-BID17-024) applies
  if gift spec re-scans — already excluded.

## Acceptance criteria

- [ ] MARKETING-aligned grammar (paper/card/gold), no hero band.
- [ ] One ChatWidget mount; journey="gift" unchanged.
- [ ] Stripe redirect path + validation tests green.
- [ ] Same-commit unit + e2e pins.
