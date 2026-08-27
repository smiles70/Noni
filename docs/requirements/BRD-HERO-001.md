# Business Requirements Document — HERO-001

**Process:** v9.51
**ID:** BRD-HERO-001
**Date:** 2026-08-27
**Owner:** Product
**Source:** `.ai/intake/2026-08-27-landing-hero-redesign.md`

## Business goal

Increase first-visit trust and clarity for older adults and caregivers by
replacing the current landing page with a calm, single-focus hero that
explicitly states Noni's value and offers a clear, low-pressure next step.

## Objectives

1. Reduce landing-page cognitive load for adults 55+.
2. Communicate the primary value proposition above the fold without scrolling.
3. Remove all references to third-party brands (e.g., MetLife).
4. Preserve the geragogy-first design contract and avoid urgency or dark patterns.

## In scope

- Redesign of `frontend/src/components/LandingPage.tsx`.
- Reuse of the existing `landing.page` UI state envelope.
- Replacement of hero image, headline, subheadline, and primary/secondary CTAs.
- Removal of any borrowed or third-party brand text, logos, or imagery.

## Out of scope

- New backend endpoints.
- New UI state envelopes.
- New components outside the V1 inventory.
- Subscription or pricing changes.

## Success measures

- Landing page renders without RenderGuard violations.
- Page passes `npm run type-check` and `npm run build`.
- Lighthouse accessibility score ≥ 90.
- No MetLife or third-party references in `dist/` bundle.

## Assumptions

- The existing `landing.page` envelope (`max_primary_actions=5`, `max_visible_text_levels=3`) is sufficient for the new layout.
- A Noni-appropriate hero image is available or will be selected before implementation.
