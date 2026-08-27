# Intake — HERO-003 Full-Page Hero Image Update

**Date:** 2026-08-27
**Process:** v9.51
**Source:** User feedback and MetLife Legal Plans reference image.
**Scope:** Make the `LandingPage.tsx` hero image a full-page, full-bleed
photograph with the subject anchored on the left, matching the MetLife
reference layout more closely.

## Problem

The current hero image is full-bleed, but the subject is centered and the
action card on the right can obscure the subject. The desired outcome is a
full-page image where the subject (or subjects) is clearly on the left and
the floating action card sits on the right, like the MetLaw reference.

## Proposed change

1. Update `frontend/src/components/LandingPage.tsx`:
   - Use `object-position: left center` so the subject is anchored on the left.
   - Lighten or remove the dark overlay so the image feels more open.
   - Keep the card on the right but adjust its width and shadow.
   - Ensure the image fills the viewport on all screen sizes.

2. Replace the image asset when a rights-cleared, MetLaw-style full-page
   photograph is available. Until then, the implementation uses
   `public/nonisplash.jpg` as the configured placeholder.

## In scope

- CSS / layout changes to `LandingPage.tsx`.
- Update to `RenderProposal` if new spacing/radius values are used.
- Process artifacts (phase inventory, pre-flight, lessons learned, graph).

## Out of scope

- Acquiring or licensing a new image.
- New UI components or backend endpoints.
- Contract text changes (ADR 0029 already covers the landing page).

## Acceptance

- `npm run type-check` and `npm run build` pass.
- Live page shows the image subject on the left.
- The action card remains readable on the right.
- No MetLife / legal-plan strings in `dist/`.
