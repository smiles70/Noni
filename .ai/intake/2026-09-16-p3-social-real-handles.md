# Intake — Connect real social account handles

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** Social links point at placeholder URLs.

## Goal

Point the backend-served `social_links` at the real accounts:

- TikTok: `https://www.tiktok.com/@mynaani_learning`
- Instagram: `https://www.instagram.com/mynaani_learning`
- Facebook + YouTube: keep placeholder handles — owner said "we will add
  the others later."

## Acceptance

- `/api/v1/site/footer` returns the two real URLs.
- Unit test updated; staging green.
