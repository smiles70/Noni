# Intake — YouTube footer handle correction (second fix)

**Date:** 2026-09-16
**Status:** in progress
**Prior:** `.ai/intake/2026-09-16-p3-youtube-handle.md`

## Problem

Footer YouTube link points to `https://www.youtube.com/@MyNanni_Learning`
(double-n "Nanni"). Correct handle is
`https://www.youtube.com/@MyNaani_learning` (single-n "Naani").

## Scope

- `backend/content/site_chrome.py` — social link href.
- `backend/tests/test_site_chrome.py` — assertion update.
- Verify other surfaces (Footer.tsx renders from the same chrome data;
  check for hardcoded copies).
