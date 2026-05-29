---
description: Architecture blueprint for P11/P23 — Replace window.setTimeout with globalThis in FetchClient
---

# Blueprint: Universal Timer Fix (P11/P23)

## Problem Statement

`frontend/src/api/client.ts` uses `window.setTimeout` and `window.clearTimeout` for request timeout handling and retry delays. In Node.js/vitest test environments, `window` is undefined, causing:
- Test suite crashes or silent skips
- Frontend unit tests that exercise `FetchClient` cannot run in CI
- The bug masks other frontend regressions because the test suite fails before reaching them

This is **not** a production bug (browsers always have `window`), but it is a **test-infrastructure** bug that blocks the quality gate.

## Root Cause

The FetchClient was written assuming a browser-only environment. `window.setTimeout` is browser-specific. The ECMAScript 2020 standard introduced `globalThis` as the universal global object that works in:
- Browsers (`globalThis === window`)
- Node.js (`globalThis === global`)
- Web Workers (`globalThis === self`)
- Vitest/jsdom (`globalThis` is polyfilled)
- Deno, Bun

## Design Principle

> **Use `globalThis` for all timer operations in shared/isomorphic code. Reserve `window` for browser-only DOM APIs.**

This is the industry-standard pattern (Node.js timers docs, isomorphic-timers-promises package, Vite-based projects).

## Changes Required

### File: `frontend/src/api/client.ts`

**3 occurrences, all in `_request()` and `_sleep()`:**

```diff
- function _sleep(ms: number): Promise<void> {
-   return new Promise((resolve) => window.setTimeout(resolve, ms));
+ function _sleep(ms: number): Promise<void> {
+   return new Promise((resolve) => globalThis.setTimeout(resolve, ms));
 }

- const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
+ const timeoutId = globalThis.setTimeout(() => controller.abort(), timeoutMs);

- window.clearTimeout(timeoutId);
+ globalThis.clearTimeout(timeoutId);
```

### Files That Do NOT Need Changes

| File | Why | Current Usage |
|------|-----|--------------|
| `AccountSettingsPage.tsx` | Browser-only component; never runs in Node | `setTimeout` (implicit `window`) |
| `AuthPendingBanner.tsx` | Browser-only component; never runs in Node | `setTimeout` (implicit `window`) |

These components use `setTimeout` without the `window.` prefix, which is fine — in a browser bundler context, unqualified `setTimeout` resolves to `window.setTimeout` automatically. They never execute in vitest because they require Clerk DOM context.

## Behavioral Guarantee

- `globalThis.setTimeout` returns the **same** type (`number` in browser, `Timeout` in Node) as `window.setTimeout`
- `globalThis.clearTimeout` accepts **both** types transparently
- No behavior change: same delay, same abort signal, same cleanup

## Testing Strategy

### 1440-Degree Regression Perspective

See `docs/blueprints/p11-1440-regression.md` for the full test matrix.

### Regression Guard

A new test in the test suite will scan `src/**/*.ts` and `src/**/*.tsx` and fail if any `window.setTimeout` or `window.clearTimeout` appears outside of test files or browser-guarded blocks.

## Rollback Plan

If `globalThis` causes unexpected issues (extremely unlikely — it's been standard since ES2020):
```bash
git revert HEAD
```

## Risk Assessment

| Factor | Value | Notes |
|--------|-------|-------|
| Blast radius | 1 file | Only `api/client.ts` |
| Lines changed | 3 | Mechanical find-and-replace |
| Production risk | None | `globalThis === window` in browsers |
| Test risk | Low | Vitest already polyfills `globalThis` |
| Rollback time | <1 min | Single revert |
