# PS-BID17-001 — Marketing pages render boxed, not full-bleed (defect)

**Status:** in-progress | **Severity:** P0 visual defect on staging
**Reported:** owner, staging screenshots 2026-09-20
**Parent:** `.ai/intake/2026-09-19-p1-bid17-production-implementation.md`

## Problem statement

`/caregiver` and `/for-communities` render inside a centered ~640–1080px
column with visible gutters — the bid-17 charcoal nav/hero/CTA bands do
not reach the viewport edges. The winning design is edge-to-edge; the
boxed rendering is a defect, not an interpretation.

## Root cause (confirmed in code)

`frontend/src/components/ResponsiveContainer.tsx` wraps **every** route
in `App.tsx` with `maxWidth: MAX_CONTENT_WIDTH[breakpoint]` +
`padding: SPACING[breakpoint].lg`. That measure cap is the geragogy
learner-track protection (ADR-0019 contract) — correct for `/`,
`/curriculum`, `/paywall`, account surfaces. It is wrong for the
ADR-0030 marketing annex, whose design requires full-bleed color bands.

## Options

- **A (recommended):** `ResponsiveContainer` checks `useLocation()` and
  bypasses the cap (`maxWidth:"100%"`, `padding:0`) for the two
  exempted marketing routes only. One-line-scope change; learner
  surfaces untouched; exemption list explicit and auditable.
- **B:** Split `<Routes>` into learner vs marketing trees and mount the
  container only around learner routes. More structural churn, same
  outcome; duplicates route declaration blocks.
- **C:** Negative-margin escape inside the pages (`margin:0 -32px`
  hacks). Fragile against breakpoint changes; rejected.

## Edge cases checked

- Other marketing-ish routes (`/partners`, `/contact`, `/gift`,
  `/c/:slug`) intentionally **not** exempted in this change — they were
  not redesigned and keep the existing measure cap (safe default).
- Skip-link target `#main-content` lives inside the container — with
  `padding:0` it still wraps content; no a11y change.
- `overflowX:hidden` on the container must remain in full-bleed mode to
  prevent band-overflow scroll.

## Acceptance

- Charcoal bands reach viewport edges on both pages at 360–2560px.
- Learner surfaces render identically (cap still applies).
- axe clean (no new landmark/overflow violations).
- Unit pin: container applies full-bleed on `/caregiver`,
  `/for-communities`; capped elsewhere.
