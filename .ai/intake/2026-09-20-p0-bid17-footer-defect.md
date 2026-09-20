# PS-BID17-002 — Marketing footer is the learner-track green fat footer (defect)

**Status:** in-progress | **Severity:** P0 visual defect on staging
**Reported:** owner, staging screenshots 2026-09-20
**Parent:** `.ai/intake/2026-09-19-p1-bid17-production-implementation.md`

## Problem statement

`/caregiver` and `/for-communities` end in the shared green fat footer
carried from the original pages. It visually belongs to the learner
palette and breaks the bid-17 charcoal system at the page's exit.

## Root cause

`Footer` (`frontend/src/components/Footer.tsx`) is a shared
backend-served component (`/api/v1/site/footer`, MKT-FOOTER-001 pin) with
learner-palette styling hard-coded. The bid-17 mock footer is a slim
charcoal strip: icon + tagline only.

## Options

- **A (recommended):** Add a `variant="dark"` prop to the shared
  `Footer` — same backend-served labels/links (brand, doormat nav,
  Privacy/Terms, socials, copyright — all retained per MKT-FOOTER-001 and
  legal necessity), restyled onto charcoal with ADR-0034 tokens. Both
  redesigned pages pass the variant; all other routes unchanged.
- **B:** Literal bid-17 slim footer (icon + tagline only). Drops
  Privacy/Terms/socials — breaks MKT-FOOTER-001 and removes legal links
  from a public surface; rejected unless owner explicitly wants it.
- **C:** A second hard-coded marketing footer component. Forks the
  backend-served content contract; rejected.

## Edge cases checked

- Backend payload unchanged — variant is presentation-only; no API work.
- Contrast on charcoal: footer link/muted text must use
  `MARKETING.mutedOnDark`/`bodyOnDark` (≥4.5:1 verified in UAT).
- Social-icon sprites may need dark-surface inversion — verify icons
  remain visible on charcoal.
- Persona isolation: footer content identical for both personas.

## Acceptance

- Both pages render the dark footer; every link/label still
  backend-served and reachable.
- axe WCAG 2.1 AA clean on both pages incl. mobile viewports.
- Other routes render the existing green footer unchanged.
- Unit pin: `variant="dark"` renders same links with charcoal styling.
