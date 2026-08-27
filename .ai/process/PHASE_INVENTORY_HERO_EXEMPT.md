# Phase Inventory — HERO-002 Contract-Exempt Landing Hero Redesign

**Process:** v9.51
**Date:** 2026-08-27
**Source:** `.ai/intake/2026-08-27-landing-hero-exemption-redesign.md`
**Exemption:** `docs/decisions/0029-landing-hero-contract-exemption.md`

## Summary

| Phase | Name | Status | Owner | Exit gate |
|---|---|---|---|---|
| 0 | Exemption pre-flight | Completed | Product / Engineering | ADR 0029 accepted; design locked; no contract leak risk |
| 1 | LandingPage.tsx exempt redesign | Completed | Engineering | Component renders and passes `RenderGuard` for `landing.page` |
| 2 | Build + bundle verification | Completed | Engineering | `npm run type-check`, `npm run build`, bundle guard pass; no brand leaks |
| 3 | Live smoke | In Progress | Engineering | `noni-web.pages.dev` shows new hero; no console errors |
| 4 | Process closeout | Completed | Engineering | Phase inventory, pre-flight, and knowledge graph updated |

## Phase 0 — Exemption pre-flight

**Objective:** Confirm the contract exemption is safe to apply and that the
new design will not leak into other pages.

**Inputs:**
- ADR 0029 (now Accepted)
- `frontend/src/components/LandingPage.tsx`
- `frontend/src/design/tokens.ts`
- `backend/models/ui_state_envelope.py` (`landing.page`)
- `docs/library/CONTRACT.md`

**Tasks:**
1. Verify ADR 0029 is marked Accepted.
2. Confirm the exemption is scoped to `LandingPage.tsx` only.
3. Verify no other component will use the larger heading or floating card.
4. Run pre-flight checklist.

**Outputs:**
- `PREFLIGHT_HERO_EXEMPT.md` signed off.

## Phase 1 — LandingPage.tsx exempt redesign

**Objective:** Implement the MetLife-style hero within the exemption.

**Inputs:**
- MetLife reference image
- `frontend/src/components/LandingPage.tsx`
- `frontend/src/components/AccountStyles.ts`
- `frontend/src/design/tokens.ts`

**Tasks:**
1. Add full-bleed hero image background.
2. Add right-side white action card with large headline, subheadline,
   primary CTA, and secondary buttons.
3. Add fixed-position "Need help?" bubble.
4. Update `RenderProposal` for `landing.page`.
5. Add `data-contract-exemption="landing.hero"` to exempt elements.

**Verification:**
- `npm run type-check` passes.
- `RenderGuard` does not block.

**Commit boundary:** `git add frontend/src/components/LandingPage.tsx`.

## Phase 2 — Build + bundle verification

**Tasks:**
1. `npm run build`.
2. `npm run postbuild`.
3. `grep -R "metlife\|legal plan" frontend/dist/`.

**Verification:**
- Build exits 0.
- No MetLife / legal-plan references.

## Phase 3 — Live smoke

**Tasks:**
1. Push to `main`.
2. Wait for Cloudflare Pages deploy.
3. Open `https://noni-web.pages.dev/`.

## Phase 4 — Process closeout

**Tasks:**
1. Update `KNOWLEDGE_GRAPH.md`.
2. Update `PHASE_INVENTORY_HERO_EXEMPT.md`.
3. Create `LESSONS_LEARNED_HERO.md`.

## Inter-phase gates

| From | To | Gate |
|---|---|---|
| 0 → 1 | Pre-flight passed |
| 1 → 2 | `npm run type-check` passes |
| 2 → 3 | Bundle guard passes; no brand leaks |
| 3 → 4 | Live page confirmed |
