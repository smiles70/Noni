---
description: 1440-degree regression perspective for P11/P23 — window.setTimeout → globalThis fix
---

# 1440-Degree Regression Perspective: P11/P23 Timer Fix

The 720-degree test covers 6 dimensions × 2 passes (once for syntax, once for runtime). The 1440-degree test covers **12 dimensions × 2 passes** — every angle of the change verified, with both pre-change and post-change baselines compared.

## Dimension Map

| Dimension | What It Tests | Pass 1 (Before Fix) | Pass 2 (After Fix) | Tool |
|-----------|--------------|---------------------|-------------------|------|
| **D1** Syntax / Static Analysis | TypeScript compilation | Baseline | Must be identical | `npx tsc --noEmit` |
| **D2** Lint / Code Style | No new warnings | Baseline | Must be identical | `npx eslint src/api/client.ts` |
| **D3** Static Source Guard | No `window.setTimeout` in shared code | Fails (found 3) | Must pass | `grep -r "window\.setTimeout" src/` |
| **D4** Browser Environment | `globalThis.setTimeout` works in browser | N/A | Pass | Browser console or Playwright |
| **D5** Node/Vitest Environment | `globalThis.setTimeout` works in vitest | N/A | Pass | `npx vitest run` |
| **D6** Behavioral Equivalence | Timeout fires at correct ms, abort triggers | Baseline | Must match | Unit test with fake timers |
| **D7** Retry Integration | `_sleep()` in `_requestWithRetry()` works | Baseline | Must match | Unit test: retry with delays |
| **D8** Memory / Resource | Timers always cleared (no leak) | Baseline | Must match | Unit test: verify `clearTimeout` called |
| **D9** Edge Cases | Zero, negative, very large timeout | Baseline | Must handle gracefully | Unit test: edge case matrix |
| **D10** Cross-Platform | Works in all target environments | N/A | Pass | Browser + Node + vitest |
| **D11** Build Pipeline | CI build succeeds | Baseline | Must pass | `npm run build` in CI |
| **D12** Regression Guard | Automated guard against reintroduction | N/A | Pass | Dedicated test file |

## Test Implementation

### D3 — Static Source Guard Test

```typescript
// frontend/src/__tests__/no-window-settimeout.test.ts
import { describe, it, expect } from "vitest";
import * as fs from "fs";
import * as path from "path";

describe("P11/P23 regression guard: no window.setTimeout in shared code", () => {
  it("api/client.ts must not contain window.setTimeout or window.clearTimeout", () => {
    const clientPath = path.resolve(__dirname, "../api/client.ts");
    const content = fs.readFileSync(clientPath, "utf-8");
    expect(content).not.toMatch(/window\.setTimeout/);
    expect(content).not.toMatch(/window\.clearTimeout/);
  });
});
```

### D6 — Behavioral Equivalence Test

```typescript
// Test: timeout fires at correct ms and abort triggers
vi.useFakeTimers();
const controller = new AbortController();
const timeoutId = globalThis.setTimeout(() => controller.abort(), 5000);
vi.advanceTimersByTime(5000);
expect(controller.signal.aborted).toBe(true);
globalThis.clearTimeout(timeoutId);
vi.useRealTimers();
```

### D7 — Retry Integration Test

```typescript
// Test: _sleep() in retry loop advances correctly
vi.useFakeTimers();
const start = Date.now();
const sleepPromise = _sleep(750);
vi.advanceTimersByTime(750);
await sleepPromise;
expect(Date.now() - start).toBeGreaterThanOrEqual(750);
vi.useRealTimers();
```

### D8 — Memory / Resource Test

```typescript
// Test: clearTimeout is always called even on fetch failure
const setTimeoutSpy = vi.spyOn(globalThis, "setTimeout");
const clearTimeoutSpy = vi.spyOn(globalThis, "clearTimeout");
// ... trigger fetch that throws ...
expect(clearTimeoutSpy).toHaveBeenCalled();
setTimeoutSpy.mockRestore();
clearTimeoutSpy.mockRestore();
```

### D9 — Edge Cases

| Case | Expected |
|------|----------|
| `timeout = 0` | Immediate abort or immediate resolution (implementation-defined, but must not crash) |
| `timeout = -1` | Treated as 0 or immediate by browser/Node spec |
| `timeout = 2^31 - 1` | Maximum safe 32-bit signed int; must not overflow |
| `timeout = Infinity` | Treated as 0 by spec |

## Pass/Fail Criteria

All 12 dimensions must pass in Pass 2 with results **identical to or better than** Pass 1.

| Dimension | Pass 1 Result | Pass 2 Target | Status |
|-----------|--------------|---------------|--------|
| D1 Syntax | ✅ Pass | ✅ Identical | Required |
| D2 Lint | ✅ Pass | ✅ Identical | Required |
| D3 Source Guard | ❌ Fail (3 occurrences) | ✅ Pass | Required |
| D4 Browser | ❌ Blocked (tests crash) | ✅ Pass | Required |
| D5 Vitest | ❌ Blocked (tests crash) | ✅ Pass | Required |
| D6 Equivalence | Baseline | ✅ Match baseline | Required |
| D7 Retry | Baseline | ✅ Match baseline | Required |
| D8 Memory | Baseline | ✅ Match baseline | Required |
| D9 Edge Cases | Baseline | ✅ Match baseline | Required |
| D10 Cross-Platform | ❌ Fail (Node missing window) | ✅ Pass | Required |
| D11 Build | Baseline | ✅ Pass | Required |
| D12 Guard | ❌ Not present | ✅ Present + pass | Required |

## Execution Order

```bash
# Pass 1: Baseline
npx tsc --noEmit                    # D1
npx eslint src/api/client.ts      # D2
grep "window\.setTimeout" src/api/client.ts  # D3 (expect 3 hits)
npx vitest run src/api/__tests__/client.test.ts  # D4-D9 (expect crash/skip)
npm run build                       # D11

# Apply fix
sed -i 's/window\.setTimeout/globalThis.setTimeout/g' src/api/client.ts
sed -i 's/window\.clearTimeout/globalThis.clearTimeout/g' src/api/client.ts

# Pass 2: Verification
npx tsc --noEmit                    # D1
npx eslint src/api/client.ts      # D2
grep "window\.setTimeout" src/api/client.ts  # D3 (expect 0 hits)
npx vitest run src/api/__tests__/client.test.ts  # D4-D9 (expect pass)
npm run build                       # D11
npx vitest run src/__tests__/no-window-settimeout.test.ts  # D12
```

## Sign-Off Checklist

- [ ] D1: `npx tsc --noEmit` passes with zero errors
- [ ] D2: `npx eslint src/api/client.ts` passes with zero warnings
- [ ] D3: `grep "window\.setTimeout" src/api/client.ts` returns empty
- [ ] D4: Browser console `globalThis.setTimeout(() => console.log('ok'), 0)` prints "ok"
- [ ] D5: `npx vitest run` completes without `window is not defined` errors
- [ ] D6-D9: All unit tests in `client.test.ts` pass
- [ ] D10: Verified in both Chrome and Firefox developer console
- [ ] D11: `npm run build` produces `dist/` with no errors
- [ ] D12: Regression guard test passes
- [ ] Git diff shows exactly 3 lines changed in exactly 1 file
