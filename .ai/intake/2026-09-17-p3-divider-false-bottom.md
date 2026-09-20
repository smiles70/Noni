# Intake — WS-C: divider false-bottom remediation (LAST)

- Priority: P3 — cosmetic polish after wayfinding + CTA land
- Date: 2026-09-17
- Persona: shared — /caregiver + /for-communities.
- Research: `.ai/research/2026-09-17-long-scroll-marketing-ux.md` (WS-C)

## Finding

`<hr>` + generous whitespace between 9–10 sections matches the
Contentsquare "false bottom" pattern — visitors read it as page end
and stop scrolling (source 7). Information-scent theory: each
section's tail must signal the next or the rate-of-gain collapses
(56–59).

## Scope

1. Reduce the visual weight of section separators — keep the hairline
   semantics but tighten margin/padding so a section boundary reads
   as a pause, not a wall.
2. Ensure each section's closing line hints at what follows (scent) —
   light copy touch, no urgency language.
3. Verify no divider + whitespace block reaches a height that mimics
   a footer visually.

## Edge cases

- Over-tightening sections can crowd older readers — keep breathing
  room; the fix is signal (scent + slimmer rule), not density.
- Divider color is a shared token — verify contrast stays calm on the
  marketing background, no new color introduced.
- Screen readers: `<hr>` is already presentational; no a11y change.

## Acceptance

- Divider visual height reduced measurably (CSS diff).
- Unit/visual check: sections still distinct; axe stays clean.
- WS-D telemetry gives a before/after depth comparison at 90%.
