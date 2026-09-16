# Intake — Update Facebook social link to the real page

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** The footer Facebook link points at a placeholder
(`facebook.com/mynaani`). Owner supplied the real page: `MyNaani`.

## Goal

- `social_links` Facebook href → `https://www.facebook.com/MyNaani`
- Keep frontend `FALLBACK` in sync; update the backend test assertion.
- After this, all four social links resolve to owner-confirmed accounts.

## Acceptance

- Footer Facebook link resolves to the real page; tests + staging green.
