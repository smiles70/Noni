---
name: journey-loop-guard
description: >-
  Run whenever a change touches a curriculum end-state, paywall,
  purchase-success, purchase-cancel, gift-redemption, or progress-resume
  surface. Verifies that the routing respects an active paid entitlement
  and does not create a paywall/purchase loop, a reset-to-free-track, or a
  cross-device progress regression.
---

# Journey loop and paywall guard

This skill applies to any change that affects how learners move between a
free tier, a paywall, a paid tier, or a purchase success/cancel surface.

## When to use

Run this guard when the task touches any of the following:

- Curriculum end-of-track CTAs or `onSequenceComplete` handlers.
- Paywall/upsell pages that offer a "Buy" or "Continue" CTA.
- Purchase success/cancel pages and their primary/secondary CTAs.
- Gift redemption success CTAs.
- Progress resume helpers, `localStorage` progress, or `goCurriculum`/
  `goPaidCurriculum`-style routing functions.

## Checklist

1. **Entitlement-aware free-track completion**
   - If the learner already has the paid product, the end-of-free-track CTA
     must not route to a paywall.
   - It should route directly to the paid track entry point.
   - If the frontend cannot check entitlement, flag that the route must be
     supplied by the parent or a context that can.

2. **Entitlement-aware paywall surface**
   - If the learner already has the paid product, the paywall must not show
     only a "Buy" CTA.
   - It should offer a "Continue to paid track" CTA that routes to the paid
     track entry point.

3. **Resume helpers are not used after access is granted**
   - Never use a progress-based resume function (e.g. `goCurriculum`) in a
     post-purchase or post-redemption flow.
   - Those helpers use local-only progress and will send an entitled learner
     with no paid progress back to the free track.
   - After purchase/redemption, go straight to the paid track entry point.

4. **Purchase cancel surface does not loop entitled learners**
   - A purchase cancel page should not route an already-entitled learner back
     to the paywall.
   - The secondary CTA should route to a safe, non-looping destination such
     as the home page or the paid track.

5. **Progress sync is explicit and documented**
   - If a feature depends on progress resuming across devices, the progress
     must be stored server-side.
   - If progress is local-only (`localStorage`, `sessionStorage`, etc.), the
     code and any resume surface must not imply cross-device resume.

## Evidence required

For every change that this guard applies to, the implementation must ship:

- A journey-contract unit test covering each primary CTA route.
- An E2E test (Playwright or equivalent) that reproduces the end-to-end flow.
- An updated `AGENTS.md` or project rules section if a new loop class is
  discovered.
