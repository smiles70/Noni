# Phase Inventory — HERO-003 Full-Page Hero Image Update

**Process:** v9.51
**Date:** 2026-08-27
**Source:** `.ai/intake/2026-08-27-landing-hero-image-update.md`
**Exemption:** `docs/decisions/0029-landing-hero-contract-exemption.md`

## Summary

| Phase | Name | Status | Owner | Exit gate |
|---|---|---|---|---|
| 0 | Layout pre-flight | Completed | Product / Engineering | Image position, card placement, and contract exemption verified |
| 1 | LandingPage.tsx full-page update | Completed | Engineering | Image `object-position` left, card on right, overlay adjusted |
| 2 | Build + bundle | Completed | Engineering | Type-check, build, bundle guard pass; no brand leaks |
| 3 | Live smoke | Completed | Engineering | `noni-web.pages.dev` shows image on left, card on right |
| 4 | Process closeout | Completed | Engineering | Graph and inventory updated |

## Phase 0 — Layout pre-flight

**Objective:** Confirm the full-page image layout is safe under the contract
exemption and does not affect other screens.

**Inputs:**
- HERO-003 intake
- `frontend/src/components/LandingPage.tsx`
- `public/nonisplash.jpg`
- ADR 0029

**Outputs:**
- `PREFLIGHT_HERO_IMAGE.md` signed off.

## Phase 1 — LandingPage.tsx full-page update

**Objective:** Adjust the hero image to be full-page and left-anchored.

**Tasks:**
1. Set image `objectPosition: "left center"`.
2. Lighten or remove the dark overlay.
3. Move the action card slightly right and reduce its width.
4. Add `data-contract-exemption="landing.hero"` to any new elements.

**Commit boundary:** `git add frontend/src/components/LandingPage.tsx`.

## Phase 2 — Build + bundle

**Tasks:**
1. `npm run type-check`.
2. `npm run build`.
3. Bundle guard and brand-leak check.

## Phase 3 — Live smoke

**Tasks:**
1. Push to `main`.
2. Wait for Cloudflare Pages deploy.
3. Visual check at desktop and mobile widths.

## Phase 4 — Process closeout

**Tasks:**
1. Update `KNOWLEDGE_GRAPH.md`.
2. Update `PHASE_INVENTORY_HERO_IMAGE.md`.
3. Create `LESSONS_LEARNED_HERO_IMAGE.md`.

## Inter-phase gates

| From | To | Gate |
|---|---|---|
| 0 → 1 | Pre-flight passed |
| 1 → 2 | `npm run type-check` passes |
| 2 → 3 | Build and bundle guard pass |
| 3 → 4 | Live page verified |
