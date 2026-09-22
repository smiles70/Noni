# Intake — /c/:slug + /org residual redesign (scope B candidates)

**Date:** 2026-09-21 · **Priority:** P3 · **Parent:** PS-BID17-020 · **Status:** scoped — awaiting owner call
**Skill check:** `senior-living-agency` (B2B surfaces). Jev drift gate
(PS-BID17-020) scored these two pages 0.07 consistent — same drift as the
forms pages — but ranked them outside the forms-only fix (all-b2b 0.25).

## Scope

Two communities-path surfaces still render pre-bid-17 grammar after
021/022 ship:

| Route | Component | Notes |
|-------|-----------|-------|
| `/c/:slug` | PartnerPage.tsx (76 lines) | Hosted partner doorway — partner-brand slot must survive any grammar pass |
| `/org` | OrgDashboardPage.tsx (251 lines) | Auth-gated ops UI — marketing grammar may be wrong; needs its own register call |

## Considerations

- `/c/:slug` is visitor-facing via campaign links — the drift is
  user-visible (Jev 0.84 on the general question) but the surface's job
  is partner-branded calm, not marketing conversion.
- `/org` is operational — density and utility outrank marketing grammar;
  Jev's forms-only pick implicitly deprioritized it.
- Both need per-surface Jev plan gates if scheduled; `/org` may warrant
  "aligned-but-operational" styling rather than the full marketing band
  treatment.

## Acceptance criteria (when scheduled)

- [ ] Owner decides per-surface treatment (full grammar vs aligned-minimal).
- [ ] Partner-brand slot on `/c/:slug` preserved.
- [ ] Same-commit tests + staging verification as with 021/022.
