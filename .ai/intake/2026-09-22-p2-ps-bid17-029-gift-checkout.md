# PS-BID17-029 — /gift checkout restyle to MARKETING grammar

**Priority:** P2 · **Parent:** PS-BID17-028 · **Status:** scoped
Preserve: `startGuestCheckout` → Stripe `checkout_url` redirect, email
validation, gift ChatWidget, SupportContact, Go-back path. Fix the
duplicate `<ChatWidget>` mount (L120+L122) — keep one, inside the card.
Same-commit unit + e2e pins; journey-loop guard n/a (pre-checkout).
