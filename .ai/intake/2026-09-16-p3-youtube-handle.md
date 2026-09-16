# Intake — Update YouTube social link to the real channel

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** The footer YouTube link points at a placeholder
(`youtube.com/@mynaani`). Owner supplied the real channel:
`@MyNanni_Learning`.

## Goal

- `social_links` YouTube href →
  `https://www.youtube.com/@MyNanni_Learning`
- Keep frontend `FALLBACK` in sync.
- Update the backend test assertion.

## Acceptance

- Footer YouTube link resolves to the real channel; tests + staging green.
