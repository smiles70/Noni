# P1 — Fix `caregiver` E2E strict-mode `for-communities` locator

## Problem

The `frontend/e2e/caregiver.spec.ts` suite fails on the "links to whitepapers, sources, and the learner/facility surfaces" test because the `a[href="/for-communities"]` Playwright locator is ambiguous. It resolves to 3 elements on `/caregiver`:

1. `For senior facilities` in the caregiver section.
2. `our community program` body link.
3. `For senior facilities` in the footer.

Error (from Playwright): `strict mode violation: locator('a[href="/for-communities"]') resolved to 3 elements`.

A second failure in WebKit: `getByRole('heading', { name: /Buy mynaani as a gift/i })` is not found, which suggests the heading is not exposed as a heading role in WebKit/Safari (or the text is no longer present).

## Trigger

Run `npm run test:e2e -- e2e/caregiver.spec.ts` in the `frontend/` workspace.

## Current impact

- Local multi-browser E2E is not green.
- The `caregiver` spec cannot be used as a reliable browser-compatibility gate.
- The WebKit failure is a real cross-browser accessibility/semantics concern.

## Outcome needed

1. Resolve the `for-communities` locator so the test passes on Chromium, Firefox, WebKit, and mobile devices.
2. Determine whether the "Buy mynaani as a gift" text should be a real heading or whether the test should use a more appropriate role.
3. Keep the test aligned with the calm, accessible design of the caregiver page.

## Scope / non-goals

- In scope: `frontend/e2e/caregiver.spec.ts` and, if necessary, small semantic/aria changes in `frontend/src/components/CaregiverPage.tsx`.
- Out of scope: redesigning the caregiver page, changing production content, or touching unrelated pages.

## References

- Failing test: `frontend/e2e/caregiver.spec.ts`
- Page: `frontend/src/components/CaregiverPage.tsx`
- Playwright output: `test-results/caregiver-Caregiver-market-*/error-context.md`
