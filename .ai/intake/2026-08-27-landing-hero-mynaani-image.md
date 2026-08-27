# Intake — HERO-004 Swap to Mynaani Family Hero Image

**Date:** 2026-08-27
**Process:** v9.51
**Source:** User file `Downloads/formynaani.png`.
**Scope:** Use `formynaani.png` as the landing-page hero background and
adjust layout/cropping so the subject is visible while the MetLife UI is
hidden behind the Mynaani card.

## Image

- Original file: `/home/hazbyn/Downloads/formynaani.png`
- Target path: `frontend/public/hero-mynaani.png`
- Content: older adult and younger family member in a kitchen setting.

## Cropping / layout requirements

The source file is a full-page screenshot that includes browser chrome,
MetLife branding, and the original action card. The Mynaani layout must show
only the family photograph on the left and hide the rest behind the Mynaani
card or by cropping:

- Use `object-position` to keep the two people on the left.
- Shift the vertical crop to avoid the top browser chrome and bottom
taskbar.
- Keep the Mynaani action card on the right so it covers the MetLife card.

## Risks

- The source is a screenshot, not a clean photo asset.
- MetLife logo/branding may still be partially visible if the crop is not
tight.
- Final production should replace this with a rights-cleared image.

## In scope

- Copy the image into `frontend/public/`.
- Update `LandingPage.tsx` to use `/hero-mynaani.png`.
- Update `object-position` and card placement.
- Process artifacts (phase inventory, pre-flight, lessons learned, graph).

## Out of scope

- Image editing or copyright clearance.
- New backend or contract changes.

## Acceptance

- `npm run type-check` and `npm run build` pass.
- Live page shows the two people on the left and no visible MetLife card.
- No `metlife` / `legal plan` strings in `dist/`.
