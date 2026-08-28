# Intake — Mobile Hero Image Dynamic Adjustment

**Date:** 2026-08-28
**Process:** v9.51
**Source:** Mobile dynamic-adjustment rubric and gap assessment (session 2026-08-28)
**Scope:** `frontend/src/components/LandingPage.tsx` and related responsive-image assets

---

## Trigger

The staging review on an iPhone 13 Pro Max revealed that the current desktop-oriented hero image, `hero-mynaani.jpg`, is being mirrored (`transform: scaleX(-1)`) and the action card is being nudged downward (`bottom: 180`) to try to keep the subject's face visible. This is a procedural workaround, not a structural mobile solution. The mobile dynamic-adjustment rubric scored the app **66 / 100**, placing it in the Process v9.51 "Block major UI change" band for MLDC Responsive Readiness.

---

## Source Artifact

- **Type:** `SourceArtifact`
- **ID:** `gap-assessment-2026-08-28`
- **Path:** `memory.txt` (session summary), `PROCESS_V9.51_SPEC.md` §7, `docs/library/CONTRACT.md`
- **Version:** current `staging` branch at commit `5d81b58`
- **extraction_method:** `rule_based` + `llm_inferred`
- **confidence:** 0.85

---

## Persona & Journey

- **Persona ID:** `P-older-adult-learner`
- **Persona Name:** Older adult learner (55+)
- **Needs:** Calm, predictable, visually trustworthy landing experience; faces in imagery signal dignity and credibility; content must not be obscured.

- **Journey ID:** `J-public-landing`
- **Journey Name:** First-time visitor reaches the Mynaani landing page on a mobile device
- **Step:** Assess trust and understand the offering

---

## Epic

- **Epic ID:** `EPIC-landing-mobile-adaptation`
- **Title:** Make the landing hero composition genuinely responsive on mobile
- **extraction_method:** `llm_inferred`
- **confidence:** 0.90

---

## Decision

- **Decision ID:** `DEC-hero-mobile-art-direction`
- **Statement:** Stop mirroring and nudging the same desktop hero image. Instead, create a mobile-specific portrait crop and use `<picture>` to serve it. This is the only way to guarantee the faces stay visible while keeping the card and CTA in a stable, non-overlapping position. Once that is in place, `LandingPage` can drop the `data-contract-exemption` hero hacks and re-score much higher on both the MLDC Responsive and Geragogy contracts.
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95
- **Supersedes:** previous `DEC-hero-mirror-nudge` (ad-hoc `scaleX(-1)` and `bottom: 180` adjustments)

---

## Gaps

### Gap-001 — No art-directed mobile hero image

- **Gap ID:** `GAP-001`
- **Description:** A single uncropped `hero-mynaani.jpg` (landscape, ~1.7 MB) is served to all viewports. No `<picture>`, `srcset`, or per-breakpoint asset exists.
- **Rubric dimension:** Image adaptation / art direction
- **Current score:** 3 / 10
- **Blocked by:** missing `hero-mobile.jpg` portrait crop; missing `<picture>` markup
- **Evidenced by:** `LandingPage.tsx` uses `transform: scaleX(-1)` and `objectPosition: "left center"` as a CSS workaround
- **extraction_method:** `rule_based`
- **confidence:** 0.95

### Gap-002 — Hero composition is fixed and non-reflowing

- **Gap ID:** `GAP-002`
- **Description:** The landing hero is `position: fixed; inset: 0` with the action card `position: absolute`. It cannot reflow to device aspect ratio or safe area.
- **Rubric dimension:** Fluid layout & reflow
- **Current score:** 7 / 10
- **Evidenced by:** `LandingPage.tsx` lines 244-267
- **extraction_method:** `rule_based`
- **confidence:** 0.90

### Gap-003 — Touch-target E2E assertion is below token contract

- **Gap ID:** `GAP-003`
- **Description:** `e2e/responsive.spec.ts` asserts `44 px` minimum, while `responsiveTokens.ts` specifies `MIN_TOUCH_TARGET.mobile = 48`.
- **Rubric dimension:** Touch targets
- **Current score:** 8 / 10
- **Evidenced by:** `frontend/src/styles/responsiveTokens.ts`, `frontend/e2e/responsive.spec.ts`
- **extraction_method:** `rule_based`
- **confidence:** 0.95

### Gap-004 — E2E responsive coverage is limited to landing

- **Gap ID:** `GAP-004`
- **Description:** Playwright responsive tests only visit `/`. Lesson, paywall, account, and redemption routes are not covered.
- **Rubric dimension:** E2E responsive coverage
- **Current score:** 4 / 10
- **Evidenced by:** `frontend/e2e/responsive.spec.ts` only tests landing page
- **extraction_method:** `rule_based`
- **confidence:** 0.95

### Gap-005 — Hero action card uses non-token values

- **Gap ID:** `GAP-005`
- **Description:** The mobile card position (`bottom: 180`) and translucent `rgba(250, 250, 248, 0.65)` are not from the closed token set.
- **Rubric dimension:** Theme compliance / token alignment
- **Current score:** 7 / 10
- **Evidenced by:** `LandingPage.tsx` card and CARD styles
- **extraction_method:** `rule_based`
- **confidence:** 0.90

---

## Requirements

### Requirement-001 — Mobile hero asset must be art-directed

- **Requirement ID:** `REQ-001`
- **Statement:** Provide a portrait-cropped hero image for mobile viewports so the subject's face remains visible when a narrow portrait aspect ratio is used.
- **Type:** `functional`
- **Priority:** must
- **serves_persona:** `P-older-adult-learner`
- **part_of_journey:** `J-public-landing`
- **refines:** `EPIC-landing-mobile-adaptation`
- **verified_by:** `Test-001`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.90

### Requirement-002 — Hero image must be served with `<picture>`

- **Requirement ID:** `REQ-002`
- **Statement:** Use the `<picture>` element with a `media` query to deliver the portrait crop on mobile and the existing landscape crop on tablet/desktop/wide.
- **Type:** `technical`
- **Priority:** must
- **depends_on:** `REQ-001`
- **verified_by:** `Test-002`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.90

### Requirement-003 — Remove hero image workarounds

- **Requirement ID:** `REQ-003`
- **Statement:** Remove `transform: scaleX(-1)`, non-token `bottom` nudging, and translucent `rgba` workarounds from `LandingPage.tsx` once `<picture>` art direction is in place.
- **Type:** `technical`
- **Priority:** must
- **depends_on:** `REQ-001`, `REQ-002`
- **verified_by:** `Test-003`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.90

### Requirement-004 — Responsive E2E must assert 48 px touch targets

- **Requirement ID:** `REQ-004`
- **Statement:** Update `e2e/responsive.spec.ts` to assert `48 px` minimum touch targets on mobile, matching `MIN_TOUCH_TARGET.mobile`.
- **Type:** `quality`
- **Priority:** should
- **verified_by:** `Test-004`
- **extraction_method:** `rule_based`
- **confidence:** 0.95

### Requirement-005 — Expand responsive E2E to multiple routes

- **Requirement ID:** `REQ-005`
- **Statement:** Add responsive Playwright tests for `/lessons`, `/paywall`, `/account`, and `/redeem` in addition to `/`.
- **Type:** `quality`
- **Priority:** should
- **verified_by:** `Test-005`
- **extraction_method:** `rule_based`
- **confidence:** 0.95

---

## User Stories

### US-001 — Mobile visitor sees the whole face in the hero

- **User Story ID:** `US-001`
- **Statement:** As an older adult learner visiting on a phone, I want the person in the hero image to be fully visible, so I feel the product is designed for people like me.
- **Acceptance:**
  - On a 375×812 and a 430×932 viewport, the subject's face is not covered by the action card.
  - The image does not appear mirrored or distorted.
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

### US-002 — Landing CTA remains reachable

- **User Story ID:** `US-002`
- **Statement:** As an older adult learner, I want the primary CTA to be clearly visible and tappable, without it blocking the image.
- **Acceptance:**
  - The card is positioned without overlapping key visual content.
  - The primary button is at least 48 px tall and wide.
  - The button text is not wrapped mid-word.
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

---

## Capabilities

- **Capability ID:** `CAP-001`
- **Statement:** The app can deliver different hero image crops for different viewport size classes.
- **implements:** `REQ-001`, `REQ-002`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

- **Capability ID:** `CAP-002`
- **Statement:** The E2E suite validates 48 px touch targets across all public routes on mobile viewports.
- **implements:** `REQ-004`, `REQ-005`
- **extraction_method:** `rule_based`
- **confidence:** 0.90

---

## Acceptance Criteria

| ID | Criterion | Method | Evidence |
|---|---|---|---|
| AC-001 | `hero-mobile.jpg` exists, is ≤ 250 KB, and is a portrait crop with the subject's face near the vertical/horizontal center | manual review | image dimensions and file size in `frontend/public/` |
| AC-002 | `<picture>` with `media="(max-width: 767px)" srcset="/hero-mobile.jpg"` and fallback `<img src="/hero-desktop.jpg">` renders in `LandingPage.tsx` | code review | `LandingPage.tsx` diff |
| AC-003 | `transform: scaleX(-1)`, `bottom: 180`, and `rgba` translucency are removed from the landing hero | code review | `LandingPage.tsx` diff |
| AC-004 | Rubric dimension F (Image adaptation) scores ≥ 8 / 10 | rubric re-grade | updated rubric in `memory.txt` or `.ai/process/LANDING_HERO_RUBRIC.md` |
| AC-005 | `e2e/responsive.spec.ts` asserts `48` px for mobile viewport | test run | Playwright report |
| AC-006 | No horizontal overflow and all buttons ≥ 48 px on `/`, `/lessons`, `/paywall`, `/account`, `/redeem` | E2E pass | Playwright report |

---

## Dependencies

- **Dependency ID:** `DEP-001`
- **From:** `REQ-002` (serve with `<picture>`)
- **To:** `REQ-001` (portrait crop asset)
- **Relation:** `depends_on`

- **Dependency ID:** `DEP-002`
- **From:** `REQ-003` (remove workarounds)
- **To:** `REQ-002` (art direction in place)
- **Relation:** `depends_on`

- **Dependency ID:** `DEP-003`
- **From:** `REQ-004` (E2E 48 px)
- **To:** `GAP-003` (44 px assertion gap)
- **Relation:** `blocked_by`

---

## Evidence

- **Evidence ID:** `EV-001`
- **Type:** `rubric_score`
- **Value:** 66 / 100 on the mobile dynamic-adjustment rubric
- **Artifacts:** `memory.txt`, this intake

- **Evidence ID:** `EV-002`
- **Type:** `screenshot`
- **Description:** iPhone 13 Pro Max staging preview `f2b999a6.noni-web.pages.dev` showing hero face partially covered before the current card nudges.
- **Artifacts:** user-submitted chat images

- **Evidence ID:** `EV-003`
- **Type:** `code_reference`
- **Value:** `LandingPage.tsx` lines 253-268 (fixed hero, `scaleX(-1)`)
- **Artifacts:** `frontend/src/components/LandingPage.tsx`

---

## Out of Scope

- No new backend endpoints or content changes.
- No changes to `CONTRACT.md` global rules.
- No production promotion; this intake targets `staging` verification.

---

## Suggested Next Action

1. Generate `frontend/public/hero-mobile.jpg` (portrait, face-centered, < 250 KB).
2. Generate `frontend/public/hero-desktop.jpg` (existing landscape crop, renamed or kept as fallback).
3. Replace the current `<img>` in `LandingPage.tsx` with a `<picture>` element.
4. Remove `transform: scaleX(-1)`, non-token `bottom: 180`, and `rgba` transparency.
5. Re-position the action card using the 8px token grid and `useViewport`.
6. Update `e2e/responsive.spec.ts` to assert 48 px and extend route coverage.
7. Re-run the rubric; target score ≥ 85 / 100.

---

## Knowledge-Graph Delta

This intake adds or updates the following canonical nodes and edges:

```text
SourceArtifact:gap-assessment-2026-08-28  defined_by  PROCESS_V9.51_SPEC.md
Persona:P-older-adult-learner              part_of     Journey:J-public-landing
Journey:J-public-landing                   served      Epic:EPIC-landing-mobile-adaptation
Epic:EPIC-landing-mobile-adaptation        refined_by  Requirement:REQ-001
Requirement:REQ-001                        verified_by Test:Test-001
Requirement:REQ-001                        depends_on  Asset:hero-mobile.jpg
Decision:DEC-hero-mobile-art-direction     supersedes  Decision:DEC-hero-mirror-nudge
Gap:GAP-001                                blocks      Requirement:REQ-001
Capability:CAP-001                         implements  Requirement:REQ-001
Evidence:EV-001                            evidenced_by SourceArtifact:gap-assessment-2026-08-28
```

This intake is ready for the **Canonical Artifact Generator** to merge into `.ai/process/KNOWLEDGE_GRAPH.json` and for the **MLDC Responsive Validation Agent** to re-run once implementation is complete.
