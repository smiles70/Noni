# Intake — Move paid boundary to Module 2

**Date:** 2026-09-06 · **Process:** v9.51 · **Gate:** staging → PR → owner merge

## Finding (4-pass scan, verified in code)
Free = Modules 0–2 (~84KB, ~57% of content); paid = M3–5.
Boundary sits at `paid_bundle_dep` on module-3+ routes in
`backend/api/routes/curriculum.py`.

## Decision (owner-approved, research-backed)
Free = M0+M1 (~43%, still above Coursera's ~17% "first module" norm);
paid = M2–M5. M1 delivers a complete result ("use an AI assistant safely,
keep your judgment") — matches "result, not syllabus" (DigitalDefynd) and
the felt-value-before-wall conversion principle.

## Changes
- `paid_bundle_dep` added to module-2 unit/lesson/next routes (mirror m3+).
- `/menu` docstring + comments: "Modules 3+" → "Modules 2+".
- Paywall copy: "Modules 3, 4, and 5" → "Modules 2, 3, 4, and 5".
- Org access codes unaffected (grant PAID_BUNDLE_CODE entitlement).
- Stripe keys remain parked until boundary is merged.
