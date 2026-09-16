# Intake — Add Facebook icon, drop "Follow us on" label

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** Social row lacks Facebook; the "Follow us on" lead-in label
consumes horizontal space that the icon itself can use.

## Goal

- Add Facebook to `social_links` (backend-served) and `SOCIAL_ICONS`
  (frontend, Simple Icons CC0 path).
- Remove the "Follow us on" lead-in — the icon+label links speak for
  themselves; the freed space hosts the Facebook icon.
- Preserve `aria-label="mynaani on …"` per ADR-0033.

## Acceptance

- Four icon+label links render; no lead-in text.
- axe + unit + e2e green.
