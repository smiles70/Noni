# Research: fix `caregiver` E2E locator failures

**Date:** 2026-09-15  
**Research question:** How should `frontend/e2e/caregiver.spec.ts` locate the `for-communities` link and the primary gift CTA so the tests pass across Chromium, Firefox, WebKit, and mobile browsers?

## 1. Source table

| # | Source | Verdict |
|---|--------|---------|
| 1 | Playwright docs — Locators are strict; single-element assertions throw if more than one element matches. | `toBeVisible()` on a multi-match locator is the root cause. |
| 2 | Playwright docs — `locator.first()`, `.last()`, `.nth()` are available but not recommended; better to make the locator unique. | Prefer a user-facing, unique locator over `.first()`. |
| 3 | Playwright best practices — scope repeated objects to a container, use `getByRole` with accessible name, and treat strictness as feedback. | Use `getByRole('link', { name: /For senior facilities/ })` scoped to a region, or use a unique text match. |
| 4 | GitHub / microsoft/playwright #10611 — `strict mode violation` means the query describes a category, not one element. | Need a narrower query. |
| 5 | StackOverflow Q&A on Playwright strict mode — `locator.filter({ hasText })` or `getByRole` with `exact` can disambiguate. | `exact` or `filter` are options. |
| 6 | Playwright docs — `getByRole('heading', { name })` relies on the accessible name computed from ARIA or content. | If an element is not a heading or its accessible name differs in WebKit, the test will fail in that engine. |
| 7 | GitHub / microsoft/playwright #21487 — WebKit accessibility tree can differ from Chromium; `getByRole` may find different results. | The WebKit failure is a browser-specific accessibility mismatch. |
| 8 | Hashnode — Playwright best practices: `getByText` for visible content, `getByRole` for accessible objects, `getByTestId` for unstable cases. | For a CTA that is a visible link, `getByRole('link', { name: /.../ })` is appropriate. |

## 2. Decision matrix

| Approach | `for-communities` | Gift CTA | Pros | Cons |
|---|---|---|---|---|
| A. Keep `locator('a[href="/for-communities"]')` and add `.first()` | Passes | Old heading still fails | Minimal change | `.first()` is brittle; doesn't fix WebKit; not best practice |
| B. Use `getByRole('link', { name: 'For senior facilities' }).first()` | Passes | Old heading still fails | User-facing, scoped by text | Still `.first()`; doesn't fix WebKit |
| C. Use `getByRole('link', { name: /our community program/ })` | Passes (unique) | Update heading to match actual H1 | Matches real page, no `.first()`, no WebKit heading issue | Changes test expectation from "For senior facilities" to body link; still valid |
| D. Use `getByRole('heading', { name: /Give calm, self-paced AI learning/ })` | Replace old link check | Passes | Tests the real H1, works across engines | Requires changing the gift-journey test assertion |

## 3. Selected approach

- Replace the strict `a[href="/for-communities"]` assertion with a unique, user-facing locator: `getByRole('link', { name: /our community program/ })`.
- Replace the outdated `getByRole('heading', { name: /Buy mynaani as a gift/i })` with the actual H1 text: `getByRole('heading', { name: /Give calm, self-paced AI learning/i })`.
- Keep the whitepaper URL checks and the CTA checks that already pass.

## 4. Edge cases

| Edge case | Impact | Remediation |
|---|---|---|
| The "our community program" text changes | Test breaks | Use a regex that is unlikely to change, e.g., `/community program/` |
| The H1 text changes | Test breaks | Use a `data-testid` if the H1 text is intentionally dynamic, but the page is static |
| Multiple `For senior facilities` links cause strictness elsewhere | Test breaks | Already narrowed to `our community program` |
| WebKit heading still not found | Could indicate a real accessibility issue | Check that the `<h1>` is rendered and not hidden; if hidden, use `getByText` with `visible` filter |

## 5. Codebase conflict check

- `frontend/e2e/caregiver.spec.ts` is the only file to change.
- No existing rules in `AGENTS.md` conflict.
- The `CaregiverPage.tsx` text is stable.

## 6. Recommendation

Implement approach C/D: update the two problematic locators in `caregiver.spec.ts` to match the actual accessible text on the page. Re-run `npm run test:e2e -- e2e/caregiver.spec.ts` to confirm green.
