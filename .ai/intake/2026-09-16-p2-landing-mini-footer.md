# Intake — P2: Landing mini-footer (translucent legal strip)

**Date:** 2026-09-16
**Requester:** user
**Workstream:** WS-1 — landing surface
**Research:** `.ai/research/2026-09-16-landing-footer.md`
**Status:** approved direction (mini-footer, translucent, minimal
legal-required language) — pending copy/contact/terms decisions

## Problem statement

Add a mini-footer to the landing page: a slim, translucent strip
pinned to the bottom edge of the fixed viewport, carrying only the
legal-required language — copyright, Privacy, Contact. Reference
research: NN/g mini-footer pattern; Material bottom-bar constraints;
CCPA §7011(d) conspicuous-privacy-link requirement on the homepage.

## Hard constraints (do not violate)

- Hero stays `position: fixed; inset: 0; overflow: hidden` — the page
  must not scroll. Strip renders *inside* the viewport layer.
- No layout shift to hero image, logo plate, action card, or B2B stack.
- New element needs `data-contract-exemption="landing.hero"` like all
  hero children.
- Geragogy: calm, few, clearly-labelled links; ≥24px targets
  (WCAG 2.5.8 AA), aim 44px; 4.5:1 contrast over the photo.
- `<footer>` nested inside the hero `<section>` loses `contentinfo`
  role (W3C APG) — strip must be a body-level footer or carry explicit
  `role="contentinfo"`.
- Signed-in bottom-right widgets (help/chat) must not collide with the
  strip.

## Content (minimal legal set)

`© {year} mynaani` · `Privacy` → /privacy · `Contact` → mailto or
/help (pending user call — see gaps)

No brand logo (plate already upper-left). No Terms link until `/terms`
exists. No help-widget duplication.

## Approach (selected — Option B from research memo)

Body-level `<footer>` (or `role="contentinfo"` container) with
`position: fixed; bottom: 0`, ~48px tall, translucent plate matching
`LOGO_PLATE` treatment, link row right-aligned, copyright left.

## Work plan

**Epic:** LEGAL-NAV-001 — landing legal strip
- **Block 1 — component:** `LandingFooter` (or inline) — DOM position,
  landmark role, plate style, responsive collapse
- **Block 2 — a11y:** contrast scrim, focus rings, target sizes,
  safe-area-inset, forced-colors fallback
- **Block 3 — tests:** unit (render + links), e2e assertions in
  smoke.spec (strip visible, privacy link reachable, axe clean),
  responsive checks at short viewports

**Tracks:** design tokens (reuse COLORS/SPACING/TYPE) → component →
tests → staging UAT.

## Verification

- Unit: renders legal links; privacy link href=/privacy.
- E2E: strip visible signed-out AND signed-in; axe WCAG 2.1 AA clean;
  no horizontal scroll added; touch targets ≥24px.
- Regression: existing landing specs unchanged; hero fixed-viewport
  contract intact.
- UAT on staging: visual check at desktop + iPhone SE + landscape.

## Gaps requiring user input

1. Contact target: `mailto:help@mynaani.com` vs public `/help` link.
2. Copy source: hardcoded vs backend-served.
3. Whether signed-in state shows `/help` link instead of mailto.

## Non-goals

- No scroll, no fat footer, no link columns on `/`.
- No changes to `/caregiver` or `/for-communities` footers (WS-2).
- No `/terms` or `/accessibility` page creation.
