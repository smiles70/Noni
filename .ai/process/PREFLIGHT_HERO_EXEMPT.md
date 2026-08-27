# Pre-Flight Check — HERO-002 Phase 0

**Process:** v9.51
**Date:** 2026-08-27
**Phase:** 0 — Exemption pre-flight

## Scope

Confirm the landing page contract exemption is ready and that the redesign
can proceed without affecting other screens.

## Checklist

| # | Check | Method | Result | Owner |
|---|---|---|---|---|
| 1 | ADR 0029 marked Accepted | `docs/decisions/0029-landing-hero-contract-exemption.md` | ✅ | Product |
| 2 | Exemption scoped to `LandingPage.tsx` only | Review ADR conditions | ✅ | Engineering |
| 3 | `landing.page` envelope supports Card, Heading, Body, Button | `backend/models/ui_state_envelope.py` | ✅ | Engineering |
| 4 | Reference image available and described | Chat image | ✅ | Product |
| 5 | No new components outside V1 inventory needed | Review MetLife elements | ✅ | Engineering |
| 6 | Existing image asset `/nonisplash.jpg` available | `frontend/public/` | ✅ | Engineering |
| 7 | `HowItWorksDialog` still works with secondary CTA | Code review | ✅ | Engineering |
| 8 | Props `onBegin`, `onSignIn`, `onHelp` available | `LandingPage.tsx` Props | ✅ | Engineering |
| 9 | Exemption does not require backend changes | No new endpoints | ✅ | Engineering |
| 10 | Rubric and gap analysis reviewed | `.ai/process/LANDING_HERO_*` | ✅ | Product |

## Findings

- ADR 0029 allows a landing-page-only contract exemption.
- No backend changes are required; the redesign is purely frontend.
- The `landing.page` envelope already authorizes `Heading`, `Body`, `Button`, and `Card`.
- The floating "Need help?" bubble can be implemented as a `Button` component with fixed positioning; no new component type is needed.

## Lessons learned and gotchas

1. **Floating elements in CSS are not visible to `RenderGuard`.** The guard checks the
   proposal components and token usage, not absolute/fixed position. We must
   manually ensure the floating bubble does not cover the primary CTA on small screens.

2. **Exemption scope must be explicit in code.** Add `data-contract-exemption="landing.hero"`
   to the hero section, action card, and help bubble so future audits can find the
   exempt elements.

3. **Hero image copyright / quality.** The placeholder `nonisplash.jpg` may not show
   an older adult. A production-quality, rights-cleared image should be sourced before
   final release, but it is not a blocker for the redesign.

4. **Button count.** The card can show up to 5 buttons (1 primary + 4 secondary)
   without exceeding the `landing.page` `max_primary_actions=5` ceiling.

5. **Large font sizes do not break `RenderGuard`, but they are not in tokens.**
   The guard checks `visibleTextLevels`, not `fontSize`. We must document the
   overridden `fontSize` values in the code and ADR.

6. **Mobile stacking.** The floating card should not overflow on 320 px viewports.
   Use `maxWidth` and `boxSizing: border-box`.

## Pre-flight outcome

**Phase 0 is GO.**

Implementation of Phase 1 can begin.
