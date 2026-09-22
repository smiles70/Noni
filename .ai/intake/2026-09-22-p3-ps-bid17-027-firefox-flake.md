# PS-BID17-027 — firefox help-callback flake: "Get help with this lesson" timeout

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** open
**Found during:** prod e2e matrix; failed once, green on retry (6.4s).
Not attributable to forms diff (Jev 0.05).

## Problem statement

`e2e/help-callback.spec.ts:23` — under firefox on prod, the
`getByRole("heading", { name: "Get help with this lesson" })` locator
times out at the default 5s expect timeout. The heading renders after a
click-driven view swap; firefox's rendering pipeline on this content
can exceed 5s under parallel-worker load.

## Root cause hypothesis

Not a product bug — a test-timing edge: the assertion fires before the
swapped view settles. Chromium/webkit pass consistently; firefox retries
green, confirming flake not defect.

## Options

- **A — Wait-for-load-state before the assertion** (selected):
  `await page.waitForLoadState("networkidle")` or bump that one
  expect's timeout. Keeps the pin, kills the flake.
- **B — `test.retry` in config.** Rejected — masks real regressions.
- **C — Leave it.** Rejected — flakes erode CI trust.

## Acceptance criteria

- [ ] The spec passes firefox 3 consecutive runs.
- [ ] No assertion weakened — same content still required.
