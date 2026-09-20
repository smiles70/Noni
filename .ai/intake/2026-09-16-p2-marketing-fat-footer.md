# Intake — P2: Fat footer for marketing surfaces

**Date:** 2026-09-16
**Requester:** user
**Workstream:** WS-2 — scrollable marketing pages
**Research:** `.ai/research/2026-09-16-marketing-fat-footer.md`
**Status:** approved direction (GetSetUp-aligned fat footer replacing
current minimal footers) — pending content model sign-off

## Problem statement

Replace the current minimal `<footer>` on `/caregiver` and
`/for-communities` (tagline + 1–2 cross-links) with a GetSetUp-aligned
fat footer: centered brand mark, primary nav row, divider, legal row
(Privacy · copyright). One shared `Footer` component, used by both
pages.

## Reference structure (GetSetUp)

- Centered logo
- Nav row: Host a Session · About Us · Careers · Help Center ·
  Press · Partner With Us
- Hairline divider
- Left: Privacy Policy · Terms of Service — Right: © year. All
  rights reserved.

## Proposed mapping to mynaani IA (only routes that exist)

- Brand mark (mynaani logo, small, centered)
- Nav row: For learners (/) · For caregivers (/caregiver) ·
  For senior facilities (/for-communities) · Gift (/gift) ·
  Research (#b2b-papers anchor / whitepapers) · Help or Contact
- Legal row: Privacy Policy (/privacy) · [Terms — page doesn't exist]
  · © {year} mynaani. All rights reserved.

## Hard constraints

- Semantic `<footer>` at body level → `contentinfo` landmark (top-level,
  one per page).
- Geragogy/senior-a11y: semantic link groups (Baymard), large targets,
  calm density — the fat footer is a reference for *structure*, not
  link count. Cap nav row at ~6 links.
- Existing footers already render correctly; this is a component
  extraction + upgrade, preserving the cross-links each page has.
- Both pages are scrollable marketing surfaces — no viewport
  constraints unlike WS-1.
- Keep `marketing.caregiver` / B2B contract exemptions consistent.

## Approach (selected — shared component, Option E from parent memo)

Extract a `Footer.tsx` component (design tokens, i18n-ready strings),
render it from both pages. Structure: brand → nav row → divider →
legal row. Responsive: nav row wraps/stacks on mobile.

## Work plan

**Epic:** MKT-FOOTER-001 — shared fat footer
- **Block 1 — component:** `Footer.tsx` (props for current-page
  context or per-page link sets), brand mark, nav, legal row
- **Block 2 — integration:** replace inline footers on
  CaregiverPage + ForCommunitiesPage
- **Block 3 — a11y:** contentinfo landmark, grouped nav semantics,
  contrast on `COLORS.surface`, target sizes, focus states
- **Block 4 — tests:** unit (component + page-level), e2e updates
  (caregiver.spec/community.spec footer assertions), axe clean,
  mobile stack check

**Tracks:** component → per-page integration → tests → staging UAT.

## Verification

- Unit: footer renders nav + legal row; privacy link present.
- E2E: footer visible on both pages; axe clean; mobile stacking.
- Regression: existing page specs updated for new footer copy.
- UAT on staging: both pages, desktop + mobile.

## Gaps requiring user input

1. Final nav-row link set (proposal above; GetSetUp's Careers/Press/
   About have no mynaani equivalents).
2. Terms of Service: omit link or create `/terms` page.
3. Whether `Contact` is mailto (matches current pattern) or `/help`.
4. Should the shared footer also land on other scrollable pages
   (/help, /privacy) now or later?

## Non-goals

- No landing-page footer (WS-1 handles that).
- No changes to the fixed hero.
- No newsletter signup / social icons — not in current IA.
