# Preflight — Mobile Hero Art Direction

**Process:** v9.51
**Intake:** `.ai/intake/2026-08-28-mobile-hero-responsive-intake.md`
**Decision:** `DEC-hero-mobile-art-direction`
**Target:** Replace the mirrored/nudged hero with a mobile-specific portrait crop and `<picture>` art direction.
**Target MLDC Responsive Readiness score:** ≥ 85 / 100 (current 66 / 100)
**Target rubric dimension F (Image adaptation):** ≥ 8 / 10 (current 3 / 10)

---

## Branching and Conflict-Avoidance Strategy

1. **Integration branch:** `staging` already holds the latest mobile-readiness work and the `2026-08-28` intake.
2. **Feature branch:** `feat/mobile-hero-art-direction` is cut from `staging`.
3. **Batch commits happen only on the feature branch.**
4. **No pushes to `main`.**
5. **Final merge:** `feat/mobile-hero-art-direction` → `staging` only after the feature branch passes the `PREFLIGHT` and `BUILD` gates.
6. **Staging deploy:** `staging` is pushed to GitHub only after the merge, triggering the existing `Deploy Staging` workflow.

This keeps the production branch untouched and prevents the staging workflow from firing on every intermediate commit.

---

## Batch Plan

### Batch 0 — Branch and commit the intake

| Step | Action | Output |
|---|---|---|
| 0.1 | `git checkout staging` | clean `staging` |
| 0.2 | `git checkout -b feat/mobile-hero-art-direction` | feature branch |
| 0.3 | Stage and commit `.ai/intake/2026-08-28-mobile-hero-responsive-intake.md` | `intake` in git |
| 0.4 | Run `git status` and confirm only intended files are modified | no surprises |

**Gate:** `PREFLIGHT` — workspace clean, only `intake` committed, branch is on `feat/mobile-hero-art-direction`.

---

### Batch 1 — Prepare mobile and desktop hero assets

| Step | Action | Output |
|---|---|---|
| 1.1 | Inspect current `frontend/public/hero-mynaani.jpg` dimensions and subject placement | asset metadata |
| 1.2 | Generate `frontend/public/hero-mobile.jpg` — portrait crop, 3:4 or 9:16 aspect, face centered, ≤ 250 KB | mobile asset |
| 1.3 | Keep `frontend/public/hero-desktop.jpg` (or rename the existing landscape asset if a cleaner name is needed) | desktop asset |
| 1.4 | Remove any leftover hero variants that are not referenced (`hero-1mynaani.jpg` if not needed) | no dead assets |
| 1.5 | Commit asset changes | `feat/mobile-hero-art-direction` + assets |

**Tooling fallback:**
- If ImageMagick `convert` is installed, use `convert hero-mynaani.jpg -crop ... +repage hero-mobile.jpg`.
- Otherwise use `Pillow` with a small Python script in `/tmp`.

**Gate:** `ASSET REVIEW` — both images render, mobile crop clearly shows the subject, file sizes are appropriate.

---

### Batch 2 — Refactor `LandingPage.tsx` with `<picture>` art direction

| Step | Action | Output |
|---|---|---|
| 2.1 | Replace the single `<img src="/hero-mynaani.jpg">` with `<picture>`: `<source media="(max-width: 767px)" srcset="/hero-mobile.jpg"><img src="/hero-desktop.jpg" alt="" ...>` | art-directed markup |
| 2.2 | Remove `transform: isMobile ? "scaleX(-1)" : "scaleX(1)"` from the hero `<img>` | no mirroring |
| 2.3 | Change `objectPosition` to a token-safe focal point (e.g. `center center`) or remove the override | clean CSS |
| 2.4 | Remove the card `bottom: 180` non-token value. Reposition the action card using `SPACING` tokens (e.g. `bottom: SPACING.xl` or `top` based on the new crop) | token-compliant layout |
| 2.5 | Revert the translucent `rgba(250, 250, 248, 0.65)` card background to `COLORS.surface` or a token-approved surface; if transparency is still needed, propose an ADR or add `surfaceTranslucent` to `tokens.ts` | contract-compliance |
| 2.6 | Remove the `data-contract-exemption="landing.hero"` attributes only if the new layout no longer overlaps the hero image; keep them if the card still floats | evidence-based exemption review |
| 2.7 | Commit changes | `feat/mobile-hero-art-direction` + refactored landing page |

**Gate:** `BUILD` — `npm run type-check` and `npm run build` pass; `npm run lint` has no new errors.

---

### Batch 3 — Update responsive E2E tests

| Step | Action | Output |
|---|---|---|
| 3.1 | In `e2e/responsive.spec.ts`, change the touch-target assertion from `44` to `48` for `iPhoneSE` and other mobile viewports | aligned test contract |
| 3.2 | Add mobile viewport tests for `/lessons`, `/paywall`, `/account`, and `/redeem` routes (basic load + no horizontal scroll + all buttons ≥ 48 px) | broader coverage |
| 3.3 | Add an art-direction assertion for the landing hero: on `iPhoneSE` the `<picture>` source is `hero-mobile.jpg`, on `Desktop` it is `hero-desktop.jpg` | art-direction coverage |
| 3.4 | Commit changes | `feat/mobile-hero-art-direction` + E2E updates |

**Gate:** `E2E` — Playwright responsive spec passes. If the full suite cannot run, the targeted `responsive.spec.ts` must pass.

---

### Batch 4 — Local preview and manual QA

| Step | Action | Output |
|---|---|---|
| 4.1 | Run the Vite dev server or build and serve `dist/` locally | local preview |
| 4.2 | Verify the landing page on 375×812 and 430×932 (iPhone 13 Pro Max) viewports | subject's face visible, card not overlapping |
| 4.3 | Verify desktop 1440×900 and 1920×1080 viewports | landscape crop stable, CTA visible |
| 4.4 | Screenshot the results and attach to the session | visual evidence |
| 4.5 | Commit only if fixes are needed from QA | optional patch commit |

**Gate:** `MANUAL QA` — no clipping, no overlap, no distortion, no horizontal overflow.

---

### Batch 5 — Merge to `staging` and deploy

| Step | Action | Output |
|---|---|---|
| 5.1 | `git checkout staging` | on `staging` |
| 5.2 | `git merge feat/mobile-hero-art-direction --no-ff` | merge commit |
| 5.3 | Push `staging` to `origin/staging` | GitHub Actions `Deploy Staging` triggers |
| 5.4 | Wait for workflow success | new Cloudflare preview URL |
| 5.5 | Update `FRONTEND_URL` and `CORS_ORIGINS` in Railway staging to the new preview URL | backend allows new origin |
| 5.6 | `railway restart --service noni-api --environment staging` | backend picks up variables |
| 5.7 | `curl https://noni-api-staging.up.railway.app/health` | backend healthy |
| 5.8 | Open the new preview on a mobile viewport and confirm the hero | staging verified |

**Gate:** `STAGING SMOKE` — `/health` 200, preview loads, faces visible, CTA reachable, no console errors.

---

## Rollback Plan

- **Before Batch 5:** any batch can be abandoned by deleting `feat/mobile-hero-art-direction`; `staging` and `main` are untouched.
- **After Batch 5 but before `main` merge:** revert the merge commit on `staging` (`git revert <merge-commit> -m 1`) and run the `Deploy Staging` workflow again; the old `hero-mynaani.jpg` will be reinstated.
- **After `main` merge:** open a follow-up `feat/hero-rollback` branch, restore the previous landing page, and create a normal PR/merge.

---

## MLDC Gate Meaning for This Work

| Score | Status | Verdict |
|---|---|---|
| ≥ 85 | MLDC aligned | Feature branch can merge to `staging` |
| 80–84 | Controlled | Merge with documented exemption for any remaining token issue |
| 70–79 | Review required | Fix before merge |
| < 70 | Block | No merge to `staging` |

The re-grade happens at the end of **Batch 4** using the same mobile dynamic-adjustment rubric. The intake's acceptance criteria (`AC-004`) require dimension F to reach ≥ 8 / 10 and the total score to reach ≥ 85 / 100.

---

## Ontology / Knowledge-Graph Updates

This preflight is the canonical artifact that implements `Decision:DEC-hero-mobile-art-direction` and refines the following nodes:

```text
PREFLIGHT:hero-art-direction  derived_from   Intake:2026-08-28-mobile-hero-responsive-intake
PREFLIGHT:hero-art-direction  planned_by     smiles70
PREFLIGHT:hero-art-direction  owned_by       Devin
Batch:1                       refines        Requirement:REQ-001
Batch:2                       refines        Requirement:REQ-002
Batch:2                       refines        Requirement:REQ-003
Batch:3                       refines        Requirement:REQ-004
Batch:3                       refines        Requirement:REQ-005
Batch:4                       verified_by    ManualQA
Batch:5                       verified_by    StagingSmoke
```

Once Batch 5 is complete, the `Canonical Artifact Generator` should ingest this preflight and update `.ai/process/KNOWLEDGE_GRAPH.json` with the new `Evidence`, `Test`, and `Capability` nodes.
