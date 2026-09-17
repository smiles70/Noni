# Intake — WS-B: mid-page CTA at ~50% depth

- Priority: P2 (after WS-A so the menu lands first)
- Date: 2026-09-17
- Persona: split — facility routes /partners, caregiver routes /gift.
- Research: `.ai/research/2026-09-17-long-scroll-marketing-ux.md` (WS-B)

## Finding

Only 30–50% of visitors reach the bottom of multi-section pages; our
primary CTA sits in the last section and the header CTA scrolls away.
Data: repeating the SAME-goal CTA at scroll depths outperforms
competing CTAs by 20–30% (source 55); floating sticky CTAs hurt trust
(49) — repeat inline, don't float.

## Scope

1. `/for-communities`: one inline `PRIMARY_BTN` "Let's talk" →
   `/partners` at ~50% page depth (after the outcomes/program
   section, before pricing — the natural decision point).
2. `/caregiver`: one inline `PRIMARY_BTN` "Gift mynaani" → `/gift`
   at ~50% depth (after the evidence/papers block, matching the
   existing `data-gift-entry` pattern).
3. Calm copy — same destination as the bottom CTA so it reads as a
   repeat, not a competing action (51, 55).
4. No sticky/floating CTA bar — evidence says it reads aggressive.

## Edge cases

- Two visible CTAs must not read as equal-weight competing choices —
  mid-page CTA uses the same label semantics as the bottom one.
- Persona isolation: facility → /partners only; caregiver → /gift
  only. Never cross.
- Mid-page CTA inside an emotional-reading section → place at section
  boundary, not mid-paragraph.
- Mobile: CTA must not crowd the anchor menu — spacing token ≥ lg.

## Acceptance

- CTA visible within first ~50% of scroll on both pages.
- Unit tests: mid-page CTA href correct per persona; labels match
  bottom CTA semantics.
- E2E: mid-page CTA clickable on mobile-iphone (no overlap).
