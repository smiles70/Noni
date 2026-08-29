# Intake — Mobile Hero Card Transparency

**Date:** 2026-08-29
**Process:** v9.51
**Source:** User request (session 2026-08-29)
**Scope:** `frontend/src/components/LandingPage.tsx` mobile hero card background opacity

---

## Trigger

The user reported that the mobile hero card overlay is solid white and should not be. The requested fix is to make the background 50% transparent so the underlying image remains visible through the card.

---

## Source Artifact

- **Type:** `SourceArtifact`
- **ID:** `user-request-2026-08-29-hero-card-transparency`
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95

---

## Persona & Journey

- **Persona ID:** `P-older-adult-learner`
- **Persona Name:** Older adult learner (55+)
- **Needs:** A calm, readable landing page with visual context (faces/people) not obscured by opaque UI.

- **Journey ID:** `J-landing-first-visit`
- **Journey Name:** Learner visits the landing page for the first time

---

## Gap

- **Gap ID:** `GAP-001`
- **Description:** The mobile hero action card in `LandingPage.tsx` uses `rgba(250, 250, 248, 0.65)`, which the user perceives as solid white and wants more transparent.
- **Rubric link:** Geragogy Contract §3 — cognitive load, predictable spatial relationships, dignified imagery.
- **Evidence:** `frontend/src/components/LandingPage.tsx` lines 217–225.
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95

## Decision

- **Decision ID:** `DEC-001`
- **Statement:** Change the mobile hero card `backgroundColor` to 50% transparent (`rgba(250, 250, 248, 0.5)`). Do not change the desktop card.
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95

## Requirements

- **Requirement ID:** `REQ-001`
- **Statement:** Mobile hero card background must use an alpha value of 0.5.
- **Priority:** must
- **verified_by:** `Test-001`
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95

- **Requirement ID:** `REQ-002`
- **Statement:** Text on the mobile hero card must remain readable against the semi-transparent background.
- **Priority:** must
- **verified_by:** `Test-002`
- **extraction_method:** `rule_based`
- **confidence:** 0.90

## Acceptance Criteria

| ID | Criterion | Method |
|---|---|---|
| AC-001 | Mobile hero card `backgroundColor` alpha is `0.5` | `grep` / visual inspect |
| AC-002 | `npm run type-check` and `npm run build` pass | CI |
| AC-003 | No regression on desktop card (desktop still fully opaque) | E2E screenshot / manual QA |

---

## Out of Scope

- Production promotion is not in this intake until staging is reviewed.
- No changes to help bubble, hero image art direction, or button colors.
- No modifications to `docs/library/CONTRACT.md` or other process files.

---

## Suggested Next Action

1. Create feature branch from `staging`.
2. Edit `frontend/src/components/LandingPage.tsx` mobile `cardStyle` `backgroundColor` to `rgba(250, 250, 248, 0.5)`.
3. Run `npm run type-check` and `npm run build`.
4. Commit and merge to `staging`.
5. Deploy to staging for review.

---

## Knowledge-Graph Delta

```text
SourceArtifact:user-request-2026-08-29-hero-card-transparency  defined_by  PROCESS_V9.51_SPEC.md
Persona:P-older-adult-learner                                part_of     Journey:J-landing-first-visit
Journey:J-landing-first-visit                                served      Epic:EPIC-landing-hero-polish
Epic:EPIC-landing-hero-polish                                refined_by  Requirement:REQ-001
Epic:EPIC-landing-hero-polish                                refined_by  Requirement:REQ-002
Gap:GAP-001                                                 blocks      Requirement:REQ-001
Decision:DEC-001                                            planned_by  smiles70
```
