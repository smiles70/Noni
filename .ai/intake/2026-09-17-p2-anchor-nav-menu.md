# Intake — WS-A: "On this page" anchor menu (wayfinding)

- Priority: P2 — highest-value structural aid (sources 41–50)
- Date: 2026-09-17
- Persona: shared — /caregiver + /for-communities (marketing annex,
  not learner contract).
- Research: `.ai/research/2026-09-17-long-scroll-marketing-ux.md` (WS-A)

## Finding

Both pages are 9–10 stacked sections with zero orientation aids.
NN/g 2023: users now naturally engage TOC links; Wikimedia: persistent
TOC cuts navigational scrolling and raises traversal (+26% scroll
depth in A/B data).

## Scope

1. Shared `OnThisPage` nav component: "On this page" label + one link
   per `aria-labelledby` section, derived from a single `SECTIONS`
   array per page (id + label) — no duplicated section lists to drift.
2. Placement: below the hero, in normal flow on desktop; collapsed
   (details/summary or horizontal scroll row) on <768px. NOT fixed —
   the landing-strip overlap lesson applies to any sticky element
   here.
3. Anchors: `scroll-margin-top` on each section so headings land clear
   of the header; `prefers-reduced-motion`-aware scroll; focus moves
   to the destination heading (a11y).
4. Active-section highlight via IntersectionObserver (optional if it
   stays cheap — no scroll-jank).
5. Labels must carry information scent — use the real section
   headings, not clever names (source 56).

## Edge cases

- Anchor menu must not intercept pointer events over CTAs
  (mobile-iphone flake class — e2e cover required on that project).
- Section renamed → single SECTIONS source keeps menu and anchors in
  sync; a test asserts every SECTIONS id exists in the rendered page.
- Very long label list on mobile → horizontal scroll row or collapsed
  details; never a second sticky strip.
- Screen reader → nav landmark "On this page"; jump lands focus on the
  section heading.

## Acceptance

- Every section reachable in ≤1 click; jump lands heading in view.
- Unit tests: menu renders all sections; ids match aria-labelledby;
  no pointer-event conflicts.
- E2E (chromium + mobile-iphone): click anchor → heading visible;
  page still axe-clean.
