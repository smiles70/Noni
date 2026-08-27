# Landing Hero Redesign Research — Mynaani

**Date:** 2026-08-27
**Process:** v9.51

## Reference image

The reference is a MetLife Legal Plans landing page:

- Warm hero photograph of an older adult and a younger adult in a home
  setting.
- Headline: "Your legal plan. Your peace of mind."
- Subheadline: "Select an experience to continue."
- Five large, rounded buttons in a card: Member Access, Administrator,
  Customer Service, Attorney Portal, Notary Portal.
- Floating action bubble (MetIQ) in the lower-right.

## Design principles for older adults

From the literature:

1. **Load under 2.5 seconds, mobile-first, WCAG 2.2 AA.**
2. **Build trust fast:** real photos, calm colors, simple navigation.
3. **One focused CTA above the fold** where possible.
4. **Large, readable text and buttons; strong contrast; no hidden steps.**
5. **Forgiving, respectful language; no urgency, no fear-based nudges.**
6. **Avoid flashy motion; prefer slow, predictable transitions.**

## Direction for Mynaani

### Layout

- Full-width, warm hero image at top (older adult in a calm home/learning
  setting, not a generic stock scene).
- Left side: Mynaani logo, large H1, one-sentence value prop.
- Right side: a single white card with the primary action and a small
  number of secondary paths.
- Keep the floating help bubble as a low-key "Need help?" affordance.

### Copy

- H1: something like "Learn AI at your own pace. With confidence."
- Sub: "Choose where to start."
- Primary CTA: "Begin learning" (goes to `curriculum.menu` or sign-up).
- Secondary: "How it works", "Sign in", "For families" (or similar).

### Components and contract

The `landing.page` envelope already authorizes:
- Heading, Body, Button, Card, Divider, List, PendingBanner, BlockedNotice.

No new components are required. We can use:
- 1 Heading (H1)
- 1 Body (subheadline)
- 1 Card (CTA + secondary buttons)
- Up to 2-3 Buttons inside the card
- 1 Divider if needed

This stays within `max_primary_actions=5` and `max_visible_text_levels=3`.

### No MetLife references

- Replace the photo with a Mynaani-appropriate image (older adult learning).
- Replace "MetLife" / "Legal Plans" with Mynaani brand.
- Replace role-based portals with learner-facing choices.
- Remove the MetIQ bubble or replace with Mynaani help text.

## Next step

Create an ADR and implement the `LandingPage.tsx` redesign under the
existing `landing.page` envelope. Update `docs/decisions/` with the
rationale.
