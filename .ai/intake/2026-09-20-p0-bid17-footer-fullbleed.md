# PS-BID17-010 — Dark footer renders as a card with visible gutters (defect)

**Status:** fixing | **Severity:** P0 visual defect on staging
**Reported:** owner, staging screenshots 2026-09-20

## Problem statement

The dark footer on `/caregiver`/`/for-communities` renders as a centered
960px charcoal card on the darker `charcoalDeep` wrap — two near-black
blocks flank the footer card. It reads as a bug, not a band.

## Root cause

`FOOTER_DARK` keeps the learner footer's card treatment
(`maxWidth:960`, `borderRadius`, charcoal bg) inside `FOOTER_WRAP_DARK`
(charcoalDeep bg + horizontal padding). Two distinct charcoal tones +
inset card = the two-block artifact.

## Fix

On the dark variant only: wrap and card share `MARKETING.charcoal`,
drop the radius, keep the 960px measure for inner content centering.
The footer becomes one continuous edge-to-edge charcoal band. Default
(green) variant unchanged.

## Edge cases

- `data-site-footer` marker + backend-served content unchanged.
- Hairline/legal row contrast unaffected (same charcoal, AA-verified).
- Landing mini-strip untouched (separate component).
