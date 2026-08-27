# Phase Inventory — HERO-004 Mynaani Hero Image

**Process:** v9.51
**Date:** 2026-08-27
**Source:** `.ai/intake/2026-08-27-landing-hero-mynaani-image.md`
**Exemption:** `docs/decisions/0029-landing-hero-contract-exemption.md`

## Summary

| Phase | Name | Status | Owner | Exit gate |
|---|---|---|---|---|
| 0 | Image swap pre-flight | Completed | Product / Engineering | Source file verified, crop plan defined |
| 1 | Copy + update LandingPage | Completed | Engineering | `hero-mynaani.png` used, `object-position` adjusted |
| 2 | Build + bundle | Completed | Engineering | Type-check, build, bundle guard, no brand leaks |
| 3 | Live smoke | Completed | Engineering | `noni-web.pages.dev` shows new hero |
| 4 | Process closeout | Completed | Engineering | Graph and inventory updated |

## Phase 0 — Image swap pre-flight

**Inputs:**
- `/home/hazbyn/Downloads/formynaani.png`
- `frontend/src/components/LandingPage.tsx`
- `frontend/public/`

**Checks:**
1. Source image exists and is readable.
2. Target public directory exists.
3. `LandingPage.tsx` uses a configurable `src`.
4. Contract exemption still applies.

**Outputs:**
- `PREFLIGHT_HERO_MYNAAANI.md` signed off.

## Phase 1 — Copy + update

**Tasks:**
1. `cp /home/hazbyn/Downloads/formynaani.png frontend/public/hero-mynaani.png`.
2. Update `LandingPage.tsx` `src` to `/hero-mynaani.png`.
3. Adjust `object-position` to `left 55%` (or similar) to show the two people.
4. Verify the Noni card sits on the right.

## Phase 2 — Build + bundle

**Tasks:**
1. `npm run type-check`.
2. `npm run build`.
3. `grep -R "metlife\|legal plan" dist/`.

## Phase 3 — Live smoke

**Tasks:**
1. Push to `main`.
2. Wait for Cloudflare Pages deploy.
3. Visual check at `https://noni-web.pages.dev/`.

## Phase 4 — Process closeout

**Tasks:**
1. Update `KNOWLEDGE_GRAPH.md`.
2. Update `PHASE_INVENTORY_HERO_MYNAAANI.md`.
3. Create `LESSONS_LEARNED_HERO_MYNAAANI.md`.
