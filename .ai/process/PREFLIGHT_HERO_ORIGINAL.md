# Pre-Flight Check — HERO-006 Find High-Resolution Original Image

**Process:** v9.51
**Date:** 2026-08-27
**Phase:** 0

## Scope

Confirm the search plan is safe and will not modify code, only research.

## Checklist

| # | Check | Method | Result | Owner |
|---|---|---|---|---|
| 1 | Reference file exists | `ls /home/hazbyn/Downloads/formynaani.png` | ✅ | Engineering |
| 2 | Source campaign documented | `METLIFE_PHOTO_ORIGIN_RESEARCH.md` | ✅ | Engineering |
| 3 | No code changes required | This search is read-only | ✅ | Engineering |

## Search plan

1. Try to retrieve the original asset from the MetLife dev page by guessing
   common asset paths and checking network headers.
2. Search the Warren Seuradge case-study image list for matching filenames.
3. Search photographer portfolios and agency sites for the frame.
4. Use web search for cached / mirrored versions of the image.
5. Check the Wayback Machine for `dev.mam.metlife.com/dep/landing`.
6. Search by exact pixel dimensions and `formynaani` filename.

## Outcome

**Phase 0 is GO.**
