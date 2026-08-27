# ADR 0029 — Landing Page Contract Exemption (Proposed)

**Status:** Proposed
**Date:** 2026-08-27
**Process:** v9.51
**Owner:** Product

## Context

Competitive research of 15 older-adult-focused sites (including AARP,
Medicare.gov, Senior Planet, NIA, Ask Grace, and Arlow) shows that most
landing pages for this audience use:

- Larger hero headlines (24–48 px).
- Larger, more visually dominant CTA cards.
- Stronger benefit communication above the fold.
- More relatable, high-quality photography.

Noni’s `CONTRACT.md` (Section I.C) currently caps headings at 1.4× body
size (≈22 px), which is at the low end of the AARP heuristic range and
below common practice. The question is whether to grant a controlled
exemption for the landing page only.

## Options

### 1. No exemption — keep contract as-is

- Maintain 22 px headline and current token constraints.
- Close gaps by improving image, adding trust notes, and refining CTA card.

### 2. Partial exemption for landing page only

- Allow headline up to 32 px on the landing page.
- Allow larger border radius (up to 16 px) and a subtle CTA card shadow.
- Keep all other application screens under `CONTRACT.md`.

### 3. Full rewrite of contract heading rule

- Raise the global heading cap to 2× body size.
- Requires updating every other component and envelope proposal.
- Wide blast radius.

## Recommendation

**Option 2** — a controlled landing-page exemption — is the smallest
change that addresses the competitive gap without reopening the entire
contract.

## Consequences

### Positive

- Landing page can more closely match the reference image and top
  competitor pages.
- Headline and CTA become more visually dominant without changing the
  overall geragogy tone.

### Negative

- Creates a contract exception that must be clearly scoped.
- Sets a precedent; any future page-level exceptions require their own ADR.
- Requires re-verifying the `landing.page` envelope and `RenderGuard`
  proposal.

## Conditions if accepted

1. Exemption applies **only** to `frontend/src/components/LandingPage.tsx`.
2. No other screen may use the increased heading size.
3. A `data-contract-exemption="landing.hero"` attribute must mark exempt
   elements for audit.
4. Lighthouse accessibility and WCAG 2.2 AA must still pass.
5. Build must still pass `verify-bundle.mjs`.

## Related

- `.ai/process/LANDING_HERO_COMPETITIVE_RESEARCH.md`
- `.ai/process/LANDING_HERO_GAP_ANALYSIS.md`
- `.ai/process/LANDING_HERO_RUBRIC.md`
- `docs/decisions/0028-landing-hero-redesign.md`
- `docs/library/CONTRACT.md` Section I.C and Section VI
