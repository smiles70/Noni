# Intake — /c/:slug + /org residual redesign (scope B candidates)

**Date:** 2026-09-21 · **Priority:** P3 · **Parent:** PS-BID17-020 · **Status:** implemented (Jev-decided) — staged for verification
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

## Jev decision (2026-09-22, jev-1.13.0)

- `/c/:slug` → aligned-doorway pass (0.63): MARKETING paper bg + paperCard
  panel + gold CTA; NO hero band, partner-brand role preserved. Shipped.
- `/org` → leave (0.85): auth-gated ops tool; marketing grammar would be
  wrong. Untouched, decision recorded.
- Full-grammar on `/c/:slug` rejected (0.31); value-of-both-now 0.48.
