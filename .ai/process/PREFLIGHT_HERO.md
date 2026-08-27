# Pre-Flight Check — Phase 0: HERO-001 Landing Hero Redesign

**Process:** v9.51
**Date:** 2026-08-27
**Phase:** 0 — Design lock + asset selection

## Scope

Confirm the redesign can proceed without expanding the UI contract or
introducing new backend dependencies.

## Checklist

| # | Check | Method | Result | Owner |
|---|---|---|---|---|
| 1 | BRD/FRD/PRD created and traceable | File existence | ✅ | Engineering |
| 2 | ADR 0028 drafted | `docs/decisions/0028-landing-hero-redesign.md` | ✅ | Product |
| 3 | `landing.page` envelope exists and is sufficient | `backend/models/ui_state_envelope.py` | ✅ | Engineering |
| 4 | No new UI components needed | Review V1 inventory | ✅ | Engineering |
| 5 | No new backend endpoints needed | Review `ui_envelope.py` | ✅ | Engineering |
| 6 | Headline/subheadline copy respects geragogy | Manual review of `BRD-HERO-001` | ✅ | Product |
| 7 | Hero image placeholder path decided | `FRD-HERO-001` | ✅ | Design |
| 8 | CTA set fits `max_primary_actions ≤ 5` | Count in proposal | ✅ | Product |
| 9 | No third-party brand strings in source | `grep -R "metlife\|legal plan" frontend/src/` | ✅ | Engineering |
| 10 | Phase inventory and pre-flight exist | File existence | ✅ | Engineering |

## Findings

- The `landing.page` envelope authorizes all components needed for the new
  hero: `Heading`, `Body`, `Button`, `Card`, `Divider`, `List`,
  `PendingBanner`, `BlockedNotice`.
- The proposed layout uses 1 H1, 1 body, 1 card, and 2–3 buttons. This is
  within `max_primary_actions=5` and `max_visible_text_levels=3`.
- The current `frontend/src/components/LandingPage.tsx` already uses the
  `landing.page` envelope; the redesign can be done by updating the
  component only.

## Known issues and edge cases

1. **Hero image source** — a Noni-appropriate image is not yet in the repo.
   A placeholder path should be used if the final image is not available.
2. **Mobile two-column collapse** — the layout must collapse gracefully; the
   `reflow_permitted=False` constraint means the mobile layout should be a
   deterministic single column, not a reactive reflow.
3. **CORS / CDN** — if the hero image is served from an external CDN, the
   domain must be allowed by the CSP.
4. **Bundle size** — a large hero image can affect LCP. Optimize before final.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Image not available at start | Low | Use a gradient or solid background as fallback; replace later |
| CTA wording causes confusion | Medium | Test with older adult; keep language direct |
| Accessibility contrast fail | Low | Use only contract-approved colors and tokens |

## Pre-flight outcome

**Phase 0 is GO.**

The implementation can begin with Phase 1 (component update). No contract
amendments or new backend work are required.

## Signatures / owner approval

- Product: TBD
- Engineering: TBD
- Design: TBD
