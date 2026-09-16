# Intake — Footer rounded edges + contrast pass

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** The sage-green fat footer is a hard-edged full-bleed block.
Owner wants rounded edges ("round the edges of the green footer box") and
a verified contrast pass on the fonts and the logo.

## Goal

- Give the green footer a card treatment consistent with the design
  system: `RADIUS.lg` corners, inset margins so it reads as a contained
  panel rather than a hard page edge. (GetSetUp/doormat research shows
  the contained-panel pattern is the enterprise norm.)
- Verify WCAG 2.1 AA contrast for every text/link color on the green
  background (`#FAFAF8` on `#4A6D5C` ≈ 5.9:1 — passes; confirm all
  variants incl. legal row and copyright).
- Logo legibility: the brand mark is a dark logo on dark green — put the
  logo on a small surface-colored rounded plate (same treatment as the
  landing hero logo plate) so the mark stays readable.

## Acceptance

- Rounded, inset footer on both `/caregiver` and `/for-communities`.
- All footer text/links ≥4.5:1 contrast on the green.
- Logo sits on a light plate — no dark-on-dark.
- axe clean; e2e updated.
