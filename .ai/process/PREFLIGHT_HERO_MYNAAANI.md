# Pre-Flight Check — HERO-004 Phase 0

**Process:** v9.51
**Date:** 2026-08-27
**Phase:** 0 — Image swap pre-flight

## Scope

Confirm the `formynaani.png` source can be used as the landing hero
background and that the crop plan is safe under the contract exemption.

## Checklist

| # | Check | Method | Result | Owner |
|---|---|---|---|---|
| 1 | Source file exists | `ls /home/hazbyn/Downloads/formynaani.png` | ✅ | Engineering |
| 2 | Target directory exists | `ls frontend/public/` | ✅ | Engineering |
| 3 | Image is a PNG | File extension | ✅ | Engineering |
| 4 | MetLife UI can be hidden by Noni card and `object-position` | Visual plan | ✅ | Engineering |
| 5 | ADR 0029 still accepted | `docs/decisions/0029-landing-hero-contract-exemption.md` | ✅ | Engineering |

## Findings

- `formynaani.png` is a full-page screenshot of the MetLife landing page.
- The left side contains the desired photograph of two people.
- The right side contains the original MetLife action card, which the
  Noni card will cover.
- The top and bottom contain browser chrome and taskbar, which can be
  cropped using `object-position`.

## Gotchas

1. The image is a screenshot, so the browser chrome and taskbar must be
   cropped with CSS.
2. The source resolution may not be ideal for full-bleed desktop.
3. The MetLife logo may peek out if the crop is too high.
4. For production, this must be replaced with a rights-cleared photograph.

## Pre-flight outcome

**Phase 0 is GO.**
