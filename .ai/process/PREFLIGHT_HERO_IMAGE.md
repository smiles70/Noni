# Pre-Flight Check — HERO-003 Phase 0

**Process:** v9.51
**Date:** 2026-08-27
**Phase:** 0 — Layout pre-flight for full-page hero image

## Scope

Confirm the full-page image layout can proceed under the existing contract
exemption and that the placeholder image path is known.

## Checklist

| # | Check | Method | Result | Owner |
|---|---|---|---|---|
| 1 | ADR 0029 remains Accepted | `docs/decisions/0029-landing-hero-contract-exemption.md` | ✅ | Product |
| 2 | Existing image path is known | `public/nonisplash.jpg` | ✅ | Engineering |
| 3 | `object-position: left center` is supported in CSS | CSS reference | ✅ | Engineering |
| 4 | No new components needed | Review layout diff | ✅ | Engineering |
| 5 | Mobile overflow can be controlled | `maxWidth` and `boxSizing` in card | ✅ | Engineering |
| 6 | Card remains accessible and readable | Contrast check with overlay | ✅ | Engineering |

## Findings

- `object-position: left center` will shift the subject to the left edge of
the image box, leaving more empty image area on the right for the card.
- The placeholder `nonisplash.jpg` is available in `public/`.
- ADR 0029 already permits the landing page exemption; no new ADR required.

## Lessons learned and gotchas

1. **The image file itself is not being replaced in this phase.** We are only
   changing how the existing placeholder is displayed. The user must provide
   or license the final MetLaw-style full-page photograph.

2. **`object-position` only helps if the source image has the subject on the
   left.** If the replacement image has the subject centered or on the right,
   the value must be updated (e.g., `right center` or `center`).

3. **Overlays should be subtle on full-page images.** A heavy overlay makes a
   full-page photo look muddy. A lighter or no overlay is preferable when the
   text sits in a solid card.

4. **The card must keep `boxSizing: border-box` so padding does not cause
   overflow at narrow viewports.**

## Pre-flight outcome

**Phase 0 is GO.**
