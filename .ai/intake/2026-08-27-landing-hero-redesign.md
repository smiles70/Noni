# Intake — Hero landing page redesign

**Date:** 2026-08-27
**Process:** v9.51
**Source:** MetLife Legal Plans hero landing page inspiration image.

## Problem

The current Mynaani landing page does not immediately communicate value or a
single, clear entry point. User feedback suggests the landing page should
resemble a calm, high-trust "hero" layout: a warm photo of an older adult
with a family member, a clear headline, a short subheadline, and a small
number of explicit action choices.

## Proposed scope

1. Redesign `frontend/src/components/LandingPage.tsx`.
2. Update the `landing.page` UI state envelope if the component proposal
   changes.
3. Remove any MetLife-branded or third-party references; convert the
   visual concept to Mynaani-specific content, colors, and typography.
4. Preserve the geragogy contract: calm, dignified, low-density,
   high-contrast, predictable.
5. Keep a single primary CTA and no more than four secondary paths,
   matching the existing contract ceilings.

## Research questions

- What landing-page patterns convert best with older adults?
- How many distinct entry points can a hero support before it becomes
  cognitively overwhelming?
- How should photography, color, and motion be constrained for geragogy?

## Related

- `.ai/process/LANDING_HERO_REDESIGN_RESEARCH.md`
- `frontend/src/components/LandingPage.tsx`
- `backend/models/ui_state_envelope.py` (`landing.page`)
