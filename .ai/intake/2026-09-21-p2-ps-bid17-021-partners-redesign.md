# PS-BID17-021 — /partners retains pre-bid-17 design (form page)

**Date:** 2026-09-21 · **Priority:** P2 · **Parent:** PS-BID17-020 (scope A,
Jev pick) · **Status:** implementing
**Skills invoked:** `senior-living-agency` (B2B register + visual
conventions), `agency-intake` n/a (no dropped assets). Jev gates run at
plan and post-change stages — research memo records both.

## Problem statement

`/partners` (PartnershipInquiryPage) still renders the pre-redesign
grammar: `AccountStyles` card system, `accentDesatGreen` rounded hero
band, muted-blue links/buttons. Visitors arriving from the redesigned
`/for-communities` hit a page that looks like a different company —
Jev-scored trust-seam 0.75, user-visible 0.84.

## Root cause

Bid-17 phase-2 scope was `/caregiver` + `/for-communities` only; the
forms pages were never in the diff (confirmed via `git show --stat`).

## Redesign plan (MARKETING grammar, senior-living conventions)

- **Hero:** charcoal/charcoalDeep gradient band, kicker
  ("PARTNERSHIPS"), H1_DARK, SUB_DARK copy (existing — kept verbatim),
  phone CTA preserved (tel link, same contact_phone source).
- **Page:** `MARKETING.paper` background; form on `paperCard` with
  `RADIUS.lg` + subtle shadow — the "case-study card" convention applied
  to the form container.
- **CTA:** gold primary button (`MARKETING.gold` on `charcoalDeep` text)
  matching the bid-17 CTA register.
- **Preserved exactly:** field names, payload shape, `partner-inquiry`
  endpoint, honeypot field + hidden styling, mailto fallback, radio
  groups (all-visible choices), 44px targets, 16px+ inputs,
  `ChatWidget journey="facility"`, tracker-visible DOM.
- **Out of scope:** copy changes, new fields, endpoint changes.

## Edge cases

- Form usability outranks grammar drama — dark hero + light form card;
  the form itself stays high-contrast light-surface (radio inputs need
  light backgrounds to read).
- `accentDesatGreen` hero → charcoal is a palette-family change allowed
  by ADR-0034 marketing annex (MARKETING tokens only; zero inline hex).
- mailto fallback path must survive any style refactor.
- Submitted/thank-you state gets the same grammar (charcoal hero stays).

## Acceptance criteria

- [ ] MARKETING grammar present: charcoal hero band, paper bg, gold CTA.
- [ ] POST body identical; honeypot intact; mailto fallback intact.
- [ ] Unit test + e2e pin land in the same commit.
- [ ] axe clean; no new bundle bloat beyond budget.
- [ ] Staging-verified; prod untouched.
