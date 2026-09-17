# Intake — mobile-iphone E2E flake: landing CTA click timeouts (recurring)

**Date:** 2026-09-16
**Status:** open — second occurrence on main CI
**Prior art:** `.ai/recovery/2026-09-16-mobile-iphone-click-timeout.md`

## Problem statement

The `mobile-iphone` Playwright project fails with `locator.click` 30s
timeouts on the landing hero CTA → curriculum path. Identical signature
across two consecutive main CI runs on `dbb1fca` (run `35162697031`,
attempt 1 and re-run attempt 2):

- `e2e/landing.spec.ts` — primary CTA advances to curriculum view
- `e2e/curriculum.spec.ts` — reachable via primary CTA; How-it-works
  dialog exit; axe check
- `e2e/contrast.spec.ts` — curriculum view + curriculum menu

6 failed / 554 passed each time. All other projects (chromium, firefox,
webkit desktop, mobile-pixel) pass. The identical suite passed on
staging UAT at the same SHA — timing-sensitive flake, not a product
regression. Production deploy + post-deploy smoke are green.

## Prior mitigation (from recovery doc)

- `pointer-events: none` on the `LandingFooter` strip wrapper;
  `pointer-events: auto` re-enabled on links/copyright.
- Suspected cause at the time: fixed `bottom: 0; z-index: 2` strip
  painting over the hero CTA on iPhone-size viewports; action card
  `maxHeight: calc(45% - 96px)` leaving insufficient bottom margin.

Mitigation reduced but did not eliminate the flake — it recurred on
main CI twice today.

## Research questions

1. Is the residual cause WebKit-emulated hit-target/actionability
   (element receiving events vs. bounding box at viewport edge), or a
   rendering race (Retell script injection, font loading, plate blur)?
2. Does `force: true` or a longer timeout on the specific CTA locator
   mask a real mobile UX defect, or is the emulator's actionability
   check itself the problem?
3. Should the 6 tests be quarantined to a separate non-blocking project
   while the root cause is fixed?

## Constraints

- Hero is a fixed single viewport — do NOT change its layout (AGENTS.md).
- Do not mask a real mobile usability defect with `force: true` without
  verifying the element is genuinely clickable on a real device.

## Acceptance criteria

- Two consecutive green CI e2e runs on main, OR the 6 tests quarantined
  with a documented tracking issue.
- Root cause identified and recorded in `.ai/recovery/`.
