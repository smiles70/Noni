# PS-BID17-025 — Landing `/` fails 48px touch-target under mobile-iphone (prod)

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** open
**Found during:** PS-BID17-021/022 post-deploy e2e matrix. Landing page
untouched by the forms diff — pre-existing.

## Problem statement

`e2e/responsive.spec.ts` — "all buttons meet minimum touch target on `/`"
fails under mobile-iphone (iPhone SE, 375px): one control measures
42.86px wide vs the 48px floor. Geragogy contract requires ≥44px/48px
targets for older-adult motor control.

## Investigation needed

- Identify which button/anchor under-measures (dump the loop's failing
  locator — the spec iterates all buttons/links on `/`).
- Likely candidates: a text link, a nav item, or the footer link row
  whose tap area is text-width only.
- Fix = padding/min-width on the control via tokens, never inline.

## Acceptance criteria

- [ ] Failing control identified and named here.
- [ ] All controls on `/` ≥48px at iPhoneSE viewport.
- [ ] No visual regression at desktop widths.
