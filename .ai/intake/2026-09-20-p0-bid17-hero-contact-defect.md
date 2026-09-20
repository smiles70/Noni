# PS-BID17-003 — Phone/email contact block sits in the hero (defect)

**Status:** in-progress | **Severity:** P0 design-fidelity defect on staging
**Reported:** owner, staging screenshots 2026-09-20
**Parent:** `.ai/intake/2026-09-19-p1-bid17-production-implementation.md`

## Problem statement

`SupportContact` (tel: + mailto: line) renders inside the hero on both
bid-17 pages. The bid-17 mock carries the phone line only in the closing
CTA band — the hero shows the gold CTA + "See the learner experience"
link, nothing else. I mounted SupportContact in the hero to preserve the
integration, but the placement contradicts the approved design.

## Fix (design-faithful, contract-preserving)

- Remove `SupportContact` from the hero on both pages.
- CTA band keeps the large tel: line (mock fidelity) and gains the
  mailto line — SupportContact mounts there with a new `tone="dark"`
  prop (its learner-palette colors fail contrast on charcoal).
- Preserved verbatim: toll-free E.164 link, AI-answered disclosure,
  help@mynaani.com, persona-scoped journeys untouched.
- The standalone display-number link in the band is replaced by the
  component so the disclosure always travels with the number
  (SupportContact's own contract).

## Edge cases checked

- e2e pins on `a[href="tel:+18774094144"]` still resolve (component
  renders the same href; strict-mode `.first()` already in place).
- Retell ChatWidget stays in the hero — untouched.
- Dark-tone colors use ADR-0034 tokens (mutedOnDark/bodyOnDark),
  AA-verified on charcoal.

## Acceptance

- Hero matches mock: headline, sub, gold CTA, text link, story card.
- CTA band shows phone + email with AI-answered disclosure.
- axe clean incl. mobile; unit pin: no SupportContact in hero region.
