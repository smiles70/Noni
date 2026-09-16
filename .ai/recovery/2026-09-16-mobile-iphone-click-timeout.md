# Recovery — mobile-iphone click timeouts in staging UAT e2e

**Run:** `35096109813` on `fix/ci-green-deployed-e2e` → staging
**Category:** e2e-failure (Playwright + WebKit / mobile-iphone)
**Tool:** error-taxonomy skill

## Failure pattern

- `locator.click: Test timeout of 30000ms exceeded.` on
  `mobile-iphone` for:
  - `landing.spec.ts` — primary CTA "How it works" click + axe
  - `curriculum.spec.ts` — HowItWorksDialog interactions
- 6 tests failed across 570 total in the full UAT suite.
- Other projects (chromium, firefox, webkit desktop, mobile-pixel)
  passed.

## Likely trigger

This failure started after `LandingFooter.tsx` landed (mini-footer
strip pinned to the bottom of the fixed hero). The new strip was at
`position: fixed; bottom: 0; z-index: 2`, the same z-index as the
floating action card (`z-index: 2`). On iPhone-size viewports the
strip could paint on top of the hero CTA, and/or the action card's
`maxHeight: calc(45% - 96px)` left insufficient bottom margin,
causing WebKit's actionability checks to time out instead of clicking.

## Steps taken

1. **Defensive pointer-events:** `pointer-events: none` on the strip
   wrapper; `pointer-events: auto` on the links and copyright text so
   they remain clickable but the hero CTA isn't blocked.
2. **Card height:** Reduced the mobile action card `maxHeight` from
   `calc(45% - 96px)` to `calc(45% - 160px)`, leaving ~64 px for the
   mini-footer strip and safe area.
3. **Re-pushed to staging** for verification on the real device matrix.

## Verification needed

- Next staging UAT run (post-fix) should show 0 mobile-iphone click
  timeouts.
- If the issue persists, capture the Playwright trace/screenshot from
  `test-results/` and inspect the actual overlap in WebKit.
