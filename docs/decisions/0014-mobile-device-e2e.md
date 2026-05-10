# 0014 - Mobile device emulation in the E2E matrix

## Status

Accepted (Sprint 16).

## Context

Sprint 12 expanded the Playwright matrix to chromium + firefox + webkit, but every project was a desktop viewport. Older adults disproportionately use tablets and phones. A desktop-only matrix would miss tap-target regressions, mobile-Safari-specific bugs, and viewport-overflow issues.

Adding mobile emulation through Playwright's bundled `devices` profiles costs no new browser binaries (Pixel 5 reuses chromium; iPhone 13 reuses webkit) and roughly +1 minute of CI time per project.

## Decision

- Add two Playwright projects:
  - **`mobile-pixel`** -> `devices["Pixel 5"]` (393x851 viewport, chromium engine, mobile UA, touch).
  - **`mobile-iphone`** -> `devices["iPhone 13"]` (390x844 viewport, webkit engine, mobile UA, touch).
- The 4 existing specs run unchanged across all 5 projects.
- The axe WCAG 2.1 AA scan now executes against mobile-emulated DOMs as well.
- No iPad project for now; revisit with usage data.

## Consequences

- Tap-target, viewport-overflow, and mobile-Safari-specific bugs are caught at PR time.
- E2E job grows from ~3 to ~5 minutes.
- Total E2E permutations: 4 specs x 5 projects = 20 instances per push.
- A mobile-only flake means investigation, not a skip flag.
