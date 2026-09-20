# ADR 0034 — Dark marketing palette (bid-17) for caregiver + communities surfaces

**Status:** Proposed (staging review — requires human approval before production)
**Date:** 2026-09-19
**Process:** v9.51
**Owner:** Product
**Related:** ADR-0030 (marketing-surfaces annex), ADR-0033 (footer icons/form
controls), LOGO-TRADEMARK-001, `.ai/intake/2026-09-19-p1-bid17-production-implementation.md`,
`.ai/research/2026-09-19-bid17-production-integration-inventory.md` (§9 register, §11 sources, §12 matrices).

## Context

The owner-approved bid-17 redesign of `/caregiver` and `/for-communities`
uses a palette outside the closed token set: charcoal surfaces
(`#26292e`, `#1d1f22`), a teal accent (`#2e8c7f`), a gold CTA
(`#c9a24d`), and a warm paper content background (`#f5f3ee`).

Two governance facts make this an ADR rather than an implementation detail:

1. `tokens.ts` is a closed set — new hex values require an ADR (AF-10 in
   the senior-living rubric auto-fails un-ADR'd tokens).
2. Geragogy guidance treats dark-mode default as an anti-pattern for older
   adults. The owner has nonetheless approved the dark bid-17 theme for
   both marketing surfaces (K-1, resolved 2026-09-19, ep-047). The
   evidence review (Piepenbrock 2013; Dobres et al. 2017; NN/g 2020)
   confirms positive polarity measurably outperforms negative polarity
   for older readers — so this ADR approves the dark theme **with
   structural mitigations**, not unconditionally.

## Decision

A bounded `MARKETING` token block is added to `frontend/src/design/tokens.ts`
with exactly these values — the approved bid-17 palette, no more:

- `charcoal` `#26292E`, `charcoalDeep` `#1D1F22`, `charcoalFoot` `#141619`
- `teal` `#2E8C7F`, `tealBright` `#6FC2B4` (kickers/links on dark only)
- `tealInk` `#1F6357` (kickers/links on light only)
- `gold` `#C9A24D` (CTA fill on dark; on light surfaces the existing
  `accentDesatGreen` remains the CTA token)
- `paper` `#F5F3EE`, `paperCard` `#FFFFFF`, `paperEdge` `#E2E0D8`
- `bodyOnDark` `#D4D8DC`, `quoteOnDark` `#EEF0F2`, `mutedOnDark` `#B9BEC4`
- `inkSoft` `#4A4D52`, `mutedOnPaper` `#6B6759`, `faintOnPaper` `#55524A`
- `darkCardBorder` `#3A3E43` (hairlines on charcoal — decorative only)

Constraints:

1. **Scope:** these tokens may be used only on `data-contract-exemption`
   marketing surfaces (`/caregiver`, `/for-communities`). Learner,
   curriculum, paywall, gift-checkout, and account surfaces remain on the
   V1 contract palette.
2. **Contrast floor (WCAG 2.1 AA):** body-size text on charcoal must
   measure ≥4.5:1 (never rounded); large-scale text ≥3:1. `mutedOnDark`
   is for secondary text only at ≥16px. `tealBright` is for kickers,
   links, and emphasis on dark — not body copy.
3. **Hybrid structure (evidence-mitigation):** dense reading sections
   stay on `paper`; charcoal is reserved for nav, hero, business-case,
   and closing CTA bands. This preserves positive polarity where the
   long-form reading happens (S-09/S-10).
4. **Logo:** `mynaani-icon-linework-dark.svg` on both pages (nav + footer)
   per K-6 / LOGO-TRADEMARK-001 icon <80px rule.
5. No motion beyond the existing opacity-fade contract; no sticky/fixed
   overlays on mobile (prior pointer-event incident); focus ring must
   remain visible on every interactive element on dark.

## Consequences

- `tokens.ts` gains a scoped `MARKETING` export; the closed set is
  unchanged for governed surfaces.
- The two marketing pages adopt the bid-17 visual system with the
  exemption marker retained for audit.
- axe e2e plus a manual contrast pass on gradient regions (automated
  color-contrast returns "incomplete" over gradients — resolved by
  measured pairs, per AC-BID17-006).
- Any future marketing-surface palette change requires amending this
  ADR or a new one — tokens remain the only legal hex source.
