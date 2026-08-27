# Phase Inventory — Landing Hero Redesign (HERO-001)

**Process:** v9.51
**Date:** 2026-08-27
**Source:** `.ai/intake/2026-08-27-landing-hero-redesign.md`
**Scope:** Redesign `frontend/src/components/LandingPage.tsx` within the
existing `landing.page` UI state envelope.

## Summary

| Phase | Name | Status | Primary owner | Exit gate |
|---|---|---|---|---|
| 0 | Design lock + asset selection | Pending | Product / Design | Approved hero image, copy, and CTA set; pre-flight pass |
| 1 | Component update | Pending | Engineering | `LandingPage.tsx` renders with new layout and passes `RenderGuard` |
| 2 | Build + bundle verification | Pending | Engineering | `npm run type-check` and `npm run build` pass; bundle guard passes |
| 3 | Accessibility + mobile verification | Pending | Engineering / QA | WCAG 2.2 AA and mobile single-column checks pass |
| 4 | Process closeout | Pending | Engineering | BRD/FRD/PRD/ADR, knowledge graph, and `CURRENT_STATE.md` updated |
| 5 | Release + smoke | Pending | Engineering | Deployed to Cloudflare Pages; live `/` shows new hero |

## Phase 0 — Design lock + asset selection

**Objective:** Lock the hero image, copy, primary/secondary CTAs, and confirm
contract compliance before any code is written.

**Inputs:**
- `BRD-HERO-001`
- `FRD-HERO-001`
- `PRD-HERO-001`
- `CONTRACT.md`
- `landing.page` envelope from `backend/models/ui_state_envelope.py`

**Tasks:**
1. Finalize headline, subheadline, primary CTA, and secondary CTAs.
2. Select or create a Noni-appropriate hero image.
3. Confirm the `RenderProposal` fits `landing.page` limits.
4. Run the Phase 0 pre-flight check.

**Outputs:**
- `PHASE_INVENTORY_HERO.md` with design selections.
- `PREFLIGHT_HERO.md` signed off.

**Commit boundary:** None (design assets may be external).

## Phase 1 — Component update

**Objective:** Update `frontend/src/components/LandingPage.tsx` with the new
hero layout.

**Inputs:**
- `frontend/src/components/LandingPage.tsx`
- `frontend/src/design/tokens.ts`
- `frontend/src/components/AccountStyles.ts`
- `landing.page` envelope

**Tasks:**
1. Refactor `LandingPage.tsx` to two-column hero.
2. Use only V1 components and contract colors/spacing.
3. Ensure all text and imagery are Noni-branded.
4. Update the `RenderProposal` for the new layout.

**Verification:**
- `npm run type-check` passes.
- RenderGuard does not block the landing proposal.

**Commit boundary:** `git add frontend/src/components/LandingPage.tsx`.

## Phase 2 — Build + bundle verification

**Objective:** Prove the page builds and the bundle is clean.

**Tasks:**
1. `npm run build`.
2. `npm run postbuild` bundle guard.
3. Grep for `metlife` or `legal plan` in `dist/`.

**Verification:**
- Build exits 0.
- Bundle guard passes.
- No disallowed brand strings in `dist/`.

**Commit boundary:** `git add dist/`? No, dist not in source. Commit build config if needed.

## Phase 3 — Accessibility + mobile verification

**Objective:** Confirm the page is usable on small screens and assistive tech.

**Tasks:**
1. Visual check at 320px, 768px, and 1440px viewports.
2. Keyboard navigation check.
3. Contrast check (if tooling available).

**Verification:**
- No horizontal scroll at 320px.
- Body text never drops below 16px.
- Focus order follows visual order.

## Phase 4 — Process closeout

**Objective:** Keep v9.51 artifacts aligned.

**Tasks:**
1. Update `CURRENT_STATE.md`.
2. Update `KNOWLEDGE_GRAPH.md` and `KNOWLEDGE_GRAPH.json`.
3. Update `docs/decisions/0028-landing-hero-redesign.md` status to accepted.

**Verification:**
- Graph is valid.
- Traceability edges are documented.

**Commit boundary:** `git add docs/ .ai/process/`.

## Phase 5 — Release + smoke

**Objective:** Deploy and confirm live.

**Tasks:**
1. Push to `main`.
2. Confirm GitHub Actions Cloudflare Pages build succeeds.
3. Load `https://noni-web.pages.dev/` and verify the new hero.

**Verification:**
- `https://noni-web.pages.dev/` returns the new layout.
- No console errors.

## Inter-phase gates

| From | To | Gate |
|---|---|---|
| 0 → 1 | Design locked and pre-flight passed |
| 1 → 2 | `npm run type-check` passes |
| 2 → 3 | Bundle guard passes; no brand leaks |
| 3 → 4 | Mobile and accessibility checks pass |
| 4 → 5 | Process artifacts committed and graph valid |
| 5 → done | Live page confirmed on Cloudflare Pages |
