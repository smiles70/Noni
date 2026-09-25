# PS-BID17-024 — /gift axe color-contrast violation (firefox, prod)

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** open
**Found during:** PS-BID17-021/022 post-deploy e2e matrix (615 tests, prod).
Not attributable to the forms restyle (Jev 0.05) — /gift untouched by the diff.

## Problem statement

`e2e/gift.spec.ts` axe check on `/gift` fails under firefox on prod with
one `color-contrast` violation (impact: serious, 1 node). Same page passes
under chromium/webkit — firefox computes contrast on the actual rendered
glyph color; likely a token whose computed color differs under firefox's
rendering (e.g., a muted/gold text on dark band).

## Investigation needed

- Identify the failing node (run the spec locally with `--project=firefox`
  and dump `axe.violations[0].nodes` target selector).
- Check whether the element uses `MARKETING.mutedOnDark` or a mid-tone
  token on a dark background near the AA 4.5:1 boundary.
- Fix = token value bump (ADR-0034 palette annex) or foreground swap —
  never an inline hex.

## Acceptance criteria

- [ ] Failing node identified and named in this ticket.
- [ ] `/gift` passes axe under firefox AND chromium AND webkit.
- [ ] Token change (if any) stays inside the MARKETING/COLORS closed set.
