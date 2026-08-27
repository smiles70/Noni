# Lessons Learned and Gotchas — HERO-001 / HERO-002 Landing Hero

**Process:** v9.51
**Date:** 2026-08-27

## Lessons learned

1. **Contract caps can silently suppress visual impact.**
   The 1.4× body heading cap kept the original landing page below the
   AARP-recommended range and below every top-15 competitor. The gap was
   not obvious until we compared directly.

2. **A single reference image is not enough for a redesign brief.**
   The MetLife image needed competitive research to translate into a Noni-
   appropriate pattern. The first implementation (HERO-001) was too quiet
   because it stayed inside the contract.

3. **Pre-flight helps avoid re-work.**
   The Phase 0 pre-flight surfaced the heading-size and CTA-dominance
   constraints before any HERO-002 code was written.

4. **Competitive research is evidence, not authority to break the contract.**
   The rubric and gap analysis justified an ADR, not an ad-hoc exception.

## Gotchas

1. **RenderGuard does not see CSS position or fontSize overrides.**
   The exemption must be enforced by convention and ADR, not by the guard.

2. **Floating bubble can overlap content or the primary CTA on small screens.**
   Use `z-index` and mobile `bottom`/`right` values that avoid the action card.

3. **Hero image text legibility.**
   If the image has bright areas, white text on it may fail contrast. Use a
   solid card or a subtle overlay behind the card.

4. **Button count ceiling.**
   The `landing.page` envelope allows ≤5 primary actions. The card design
   must not exceed 5 visible buttons.

5. **No MetLife / legal-plan references.**
   Even after rewording, a bundle `grep` must confirm no third-party strings.

6. **Exemption must not spread.**
   Other pages must continue to use `TYPOGRAPHY.headingScale` tokens. Any
   future page wanting an exemption needs its own ADR.
