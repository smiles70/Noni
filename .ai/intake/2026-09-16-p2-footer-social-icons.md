# Intake — Real social media icons in the fat footer

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** Social presence shipped as text-only links ("Instagram",
"TikTok", "YouTube"). Owner asked for the actual platform icons — the
text-only output was a miss.

## Goal

- Inline SVG brand icons for Instagram, TikTok, and YouTube in the fat
  footer's social row.
- Geragogy exception: the V1 contract is text-first and prohibits icons
  without an ADR — owner has explicitly approved icons for this surface;
  document the exception in `docs/decisions/`. Per the contract's
  icon-exception rule, each icon is still accompanied by its platform
  name (icon + text label, icon aria-hidden).
- Icons: 24px, `currentColor`, inside 44px touch targets, `target=_blank`
  + `rel="noopener noreferrer"`, visible focus ring.
- Keep backend-served hrefs/labels; only the icon choice lives in the
  frontend.

## Acceptance

- Three icon+label links render in the footer social row.
- Screen readers announce "mynaani on Instagram" style labels.
- axe clean; unit + e2e coverage updated.
