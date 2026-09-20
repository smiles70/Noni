# Intake — P2: Landing-page footer decision

**Date:** 2026-09-16
**Requester:** user
**Status:** research phase

## Problem statement

Determine whether the landing page should have a footer, and if so what
form it takes. Example supplied: GetSetUp's full-width footer (brand
mark, link columns — Host a Session, About Us, Careers, Help Center,
Press, Partner With Us — plus Privacy Policy, Terms of Service,
copyright row).

## Discovery findings (codebase)

- `frontend/src/components/LandingPage.tsx` — hero is
  `position: fixed; inset: 0; overflow: hidden`. The page **cannot
  scroll** — this is intentional per `AGENTS.md` ("fixed,
  non-scrolling single viewport"; a prior in-flow `100vh` attempt
  shrank the hero and was rolled back). Changing it requires explicit
  approval.
- Surfaces on the hero: logo plate (upper-left), floating action card
  (h1/h2 + primary CTA), B2B stack (Caregiver, Senior facilities,
  top-right), HowItWorksDialog modal.
- **No privacy, terms, help, or contact link exists on `/`** — routes
  `/privacy` and `/help` exist but are unreachable from the landing
  page. Footer is the conventional home for these; their absence is a
  compliance/trust gap independent of aesthetics.
- Existing footer pattern: minimal `<footer>` (tagline + "For
  learners" link) on `ForCommunitiesPage` (line ~687) and
  `CaregiverPage` (line ~527); `HowItWorksDialog` has a dialog footer
  with CTA + caregiver/facility links. No shared Footer component.

## Tension to resolve

A GetSetUp-style footer needs a scrollable page. The landing hero is a
locked single viewport. The decision is therefore not just "add a
footer?" but "which footer form, if any, is compatible with the fixed
hero — or does the fixed hero get an approved exception?"

## Questions for research

1. What do best-in-class immersive landing pages do (footer in
   viewport, pinned strip, modal info affordance, or scroll)?
2. What is legally/operationally required at minimum (privacy link
   under GDPR/CCPA/FTC guidance for a site with auth + payments)?
3. What does geragogy/senior-a11y guidance say about footer link
   density, touch targets, and contrast on image backgrounds?
4. Does a footer on a fixed hero hurt conversion/engagement per
   available evidence?

## Non-goals

- No implementation yet.
- No change to the fixed-viewport hero positioning without explicit
  approval.
- Footers on other pages are out of scope except as pattern reference.

## Acceptance criteria (for the eventual implementation)

- Decision backed by research memo (`.ai/research/`).
- If a footer is added: `contentinfo` landmark, WCAG 2.1 AA contrast
  on hero imagery, no layout shift to hero, E2E + unit coverage.
- Privacy/terms/help reachability from `/` resolved regardless of
  outcome.
