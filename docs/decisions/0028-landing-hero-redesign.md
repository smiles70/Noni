# ADR 0028 — Landing Hero Redesign

**Status:** Accepted
**Date:** 2026-08-27
**Process:** v9.51
**Owner:** Product

## Context

The current Noni landing page does not communicate value or a clear first
step quickly enough for older adults and caregivers. Competitive analysis
and senior-friendly UX research show that a warm hero image, a single
headline, and a small set of clear CTAs improve trust and conversion for
this audience.

## Decision

Redesign the `LandingPage.tsx` hero using the existing `landing.page` UI
state envelope. The new page will:

- Show a warm, Noni-appropriate hero photograph.
- Display one headline and one sentence of body text.
- Offer one primary CTA ("Begin learning") and up to two secondary CTAs.
- Remove all third-party brand references.
- Remain fully within the `CONTRACT.md` V1 component inventory and design rules.

## Consequences

### Positive

- Faster value communication.
- Higher trust for older adults and caregivers.
- No new backend or envelope work required.

### Negative / Risks

- Hero image must be sourced or created; wrong imagery can feel generic.
- Two-column layout must degrade gracefully on mobile.
- Additional CTAs must not exceed `landing.page` interaction limits.

## Compliance

This decision stays within ADR 0019 (UI state envelopes), ADR 0021
(pricing, not relevant here), and `CONTRACT.md` Section I (design
vocabulary).

## Related

- `docs/requirements/BRD-HERO-001.md`
- `docs/requirements/FRD-HERO-001.md`
- `docs/requirements/PRD-HERO-001.md`
- `.ai/process/LANDING_HERO_REDESIGN_RESEARCH.md`
- `.ai/process/PHASE_INVENTORY_HERO.md`
