# PS-BID17-023 — Playwright `isVisible` reports honeypot inputs as visible

**Date:** 2026-09-21 · **Priority:** P3 · **Status:** documented — monitoring
**Skill check:** `error-taxonomy` — classified `e2e-failure` (test-semantics
edge, not a product defect). Surfaced during PS-BID17-021/022 staging
verification.

## Problem statement

`locator.isVisible()` returns `true` for the honeypot `input[name="website"]`
on `/partners` and `/contact` even though the control sits at
`position:absolute; left:-9999px; opacity:0; pointer-events:none`. Playwright
computes visibility from `display`/`visibility`/bounding box — opacity and
offscreen offsets do not count as hidden. A future test author could read
`isVisible() === true` as "honeypot broken" (or write a guard that wrongly
fails), producing a false regression signal.

## Root cause (confirmed)

Playwright visibility semantics are layout-based; the honeypot deliberately
uses opacity + offscreen positioning so bots' DOM walkers find a fillable
input while humans never see it. Verified on staging 2026-09-21: input
present, `isVisible() = true`, offscreen per computed style. Behavior is
unchanged from the pre-redesign implementation — not introduced by 021/022.

## Options

- **A — Document + pin semantics (selected).** This ticket records the
  semantics; the smoke/e2e pins assert honeypot *absence for humans* via
  bounding-box position (left < -1000), not `isVisible`.
- **B — Switch honeypot to `display:none`.** Rejected — display:none inputs
  are filtered by more bot parsers and some autofill flows; the
  offscreen+opacity pattern is the deliberate design.
- **C — Custom matcher.** Overkill for one field.

## Edge cases

- Bot parsers that skip `display:none`/`visibility:hidden` fields still see
  the honeypot — preserved.
- Screen readers: `aria-hidden="true"` + `tabIndex=-1` already applied.
- If a future change converts the honeypot to `display:none`, the e2e pin
  and this ticket must be revisited (bot-detection coverage changes).

## Acceptance criteria

- [x] Ticket documents the semantics so it is not misread as regression.
- [x] Existing verification treats honeypot correctness as DOM-presence +
      offscreen position, not `isVisible`.
- [ ] (Optional) add a `boundingBox` position pin to the forms e2e —
      tracked as follow-up, non-blocking.
