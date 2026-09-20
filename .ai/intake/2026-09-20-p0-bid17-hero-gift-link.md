# PS-BID17-011 — "Gift mynaani →" link in hero is not in bid-17 mock (defect)

**Status:** fixing | **Severity:** P0 design-fidelity defect on staging
**Reported:** owner, staging screenshots 2026-09-20

## Problem statement

`/caregiver` hero shows a "Gift mynaani →" link under the CTAs — not in
the approved mock. I added it to preserve `data-gift-entry="hero"`
attribution coverage.

## Contract analysis

`data-gift-entry` has three pinned values: `hero`, `gift-section`,
`footer-cta` (CaregiverPage.test.tsx). No code consumer reads them —
they are attribution markers for downstream analytics/CRM. The hero
funnel position must remain attributable.

## Fix

- Remove the visible hero link.
- Move `data-gift-entry="hero"` onto the nav "Give a gift" link — the
  nav is the top-of-funnel gift entry; marker value and funnel position
  preserved exactly, visual matches mock.
- `gift-section` and `footer-cta` markers untouched.

## Edge cases

- Nav link already navigates to `/gift` — same destination, no new
  journey surface.
- Test pin updated same commit (marker moves, value unchanged).
