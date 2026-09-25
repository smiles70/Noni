---
name: ad-agency
description: Full agency bake-off pipeline for Mynaani surfaces — evidence capture, ontology/graph traceability, rubric construction, multi-bid generation, scored assessment, delivery, and audit. Invoke for any marketing-surface redesign, agency-style bid work, or competitive design evaluation.
---

# Ad Agency — Research → Bid → Assess → Deliver → Audit

The codified process from the bid-9→bid-17 agency bake-off. Every stage is
mandatory; every claim traces to the graph or a verifiable artifact.

## Stage 0 — Problem statement

Formal intake BEFORE any design work: what surface, which persona, what the
owner actually asked for, what success looks like. No intake, no pixels.

## Stage 1 — Evidence capture (never inferred)

- **Actual published work, not imagined agency style.** Capture real pages:
  screenshots + HTML structure + copy patterns + **the real imagery** —
  run `agency-intake/extract-images.mjs` per page so the evidence base holds
  the photographs themselves (subjects, treatment, density), not just a
  description of them. Harvested images are evidence for photo briefs —
  never mock assets (copyright). Record in graph as `Agency`/`Vendor`/
  `VisualConvention`/`ProofPattern` nodes.
- **Grammar drift guard (ep-013 lesson):** bids must translate each agency's
  *actual* page architecture — not generic colored-block skeletons wearing
  agency names. If three bids share a skeleton, they're all wrong.
- **Persona evidence separation:** caregiver surfaces get caregiver briefs
  (`cognitive-engagement.pdf`, `geragogy-for-caregivers.pdf`, Tang CAN/AARP/
  JMIR sources); facility surfaces get facility briefs (`the-ai-gap.pdf`,
  `geragogy-the-key-to-learning.pdf`, occupancy/NOI/board register). Leakage
  is an automatic fail (ep-018).

## Stage 2 — Rubric (before bids, not after)

- Build the scoring rubric from the captured evidence FIRST — criteria must
  exist before artifacts so scoring isn't rationalized post-hoc.
- Current instrument: `.devin/skills/senior-living-agency/RUBRIC.md` —
  104 pts, auto-fails AF-1..AF-10, ship threshold ≥88 weighted + zero AF.
- Rubric criteria trace to graph nodes; new criteria need new evidence.

## Stage 3 — Bid generation

- One bid per agency grammar + honest naming (`bid-N-surface.html`).
- Static HTML in `.ai/research/agency-bids/` — self-contained, real assets
  (logo, fonts, hero), real copy, no lorem.
- **Honesty constraints (ep-014):** no invented ethnography ("the objection
  we hear" → "the objection this page must answer"); no fake media (play
  buttons on nonexistent video); no borrowed taglines/trademark lines.
- **Imagery is required where the grammar uses it.** The bid-15/16 gap:
  mocks shipped pure type/layout while real agency pages run photography.
  Placeholder order: (1) on-brief generated proof via Gemini image models
  (Nano Banana — `gemini-3-pro-image` studio / `gemini-2.5-flash-image`
  fast; matches the photo brief's subject/treatment), (2) on any error or
  quota limit, default to Pexels automatically — direct
  `images.pexels.com` downloads need no key. Never ship an image-shaped
  hole; never block on the fallback. Mark PLACEHOLDER in a comment + one-line photo
  brief per image (subject, treatment, placement) so real photography can
  be commissioned. A bid that omits imagery the grammar demands is an
  auto-fail.

## Stage 4 — Assessment

- Score every bid against the rubric — evidence-linked, section by section.
- Second-pass audit is mandatory: re-verify every scored point against the
  actual file (ep-023 caught dead links + a persona-leak second instance).
- axe WCAG 2.1 AA on every candidate — `.run` via repo `axe-playwright`;
  violations are auto-fails, not notes.

## Stage 5 — Delivery

- Winner selection is the OWNER's, recorded in graph (ep-016 pattern).
- Deliverables sync to `~/Downloads/AGENCY_BIDS/` with all assets — files
  must render standalone.
- Version filenames on update (cache-busting, ep-029).

## Stage 6 — Audit & record

- Graph episode per stage: capture, rubric, bids, scores, selection, fixes.
- Invalidate-don't-delete: rejected directions stay in graph `invalidated`.
- Audit doc in `.ai/audit/` for every second-pass or defect fix.
- Honest ceilings recorded (supply items like real testimonials — never
  fabricated to close a rubric gap).

## Anti-patterns (all learned the expensive way)

- Declaring "RESOLVED" before owner sign-off → status is PENDING-SIGNOFF.
- Scoring your own work without a second pass.
- Agency bids that look like the agency, not like Mynaani (ep-015: methods
  yes, skins no — continuity with the product's own identity).
- Persona-leak: B2B register on caregiver pages or vice versa.
- Shipping raster proofs as production assets (logo work → `logo-design-audit`).
- Skipping the research protocol because the change "feels small."

## Related skills

- `senior-living-agency` — sector copy/register engine for B2B surfaces
- `logo-design-audit` — brand asset production/QA
- `journey-loop-guard` — curriculum/paywall/gift flows
- `knowledge-graph-extraction` / `-validation` — graph maintenance
