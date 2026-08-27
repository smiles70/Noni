# Intake — Contract-Exempt Hero Landing Page Redesign

**Date:** 2026-08-27
**Process:** v9.51
**Source:** ADR 0029 and MetLife Legal Plans hero landing page reference image.
**Scope:** Redesign `frontend/src/components/LandingPage.tsx` under a
contract exemption for the landing page only.

## Trigger

Competitive research (`LANDING_HERO_COMPETITIVE_RESEARCH.md`) and the gap
analysis (`LANDING_HERO_GAP_ANALYSIS.md`) showed that the existing
contract-compliant hero is visually quieter than the top 15 older-adult
sites. ADR 0029 grants a controlled exemption for the landing page only.

## Exemption

Per `docs/decisions/0029-landing-hero-contract-exemption.md`:

- Headings may exceed 1.4× body size on the landing page.
- A floating CTA card may overlap the hero image.
- A fixed-position help bubble is permitted on the landing page.
- All other application screens remain under `docs/library/CONTRACT.md`.

## Design target

Reproduce the MetLife Legal Plans hero landing page pattern:

1. Full-bleed, warm hero photograph of an older adult with a family member.
2. Right-side white action card with:
   - Large, direct headline.
   - Short subheadline.
   - One prominent primary CTA.
   - Up to four secondary action buttons.
3. Floating "Need help?" bubble at the bottom right.
4. No MetLife, legal-plan, or third-party references.

## In scope

- Rewrite `frontend/src/components/LandingPage.tsx`.
- Use `nonisplash.jpg` as the hero background (placeholder; replace later).
- Update `landing.page` RenderProposal.
- Keep all other components contract-compliant.

## Out of scope

- New backend endpoints or content changes (reuse `/api/landing/page`).
- New UI state envelopes.
- Changes to `RenderGuard` or `CONTRACT.md` global rules.

## Acceptance

- `npm run type-check` passes.
- `npm run build` passes.
- No `metlife` / `legal plan` strings in `dist/`.
- Live page renders at `https://noni-web.pages.dev/`.
- RenderGuard does not block the landing proposal.
