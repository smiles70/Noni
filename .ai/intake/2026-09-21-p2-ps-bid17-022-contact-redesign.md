# PS-BID17-022 — /contact retains pre-bid-17 design (shared form page)

**Date:** 2026-09-21 · **Priority:** P2 · **Parent:** PS-BID17-020 (scope A,
Jev pick) · **Status:** verified-staging — awaiting owner UAT + prod sign-off
**Skills invoked:** `senior-living-agency` (grammar) + persona rules from
AGENTS.md — `/contact` is a **shared surface**: persona-neutral copy, no
gift pricing, no facility tiers, **no chat widget**.

## Problem statement

`/contact` (ContactPage) retains the pre-redesign grammar — same
`AccountStyles` card + `accentDesatGreen` hero signature as `/partners`.
It is the "Talk to us" destination linked from shared chrome, so the
visual seam is hit by BOTH personas, not just B2B.

## Root cause

Same as PS-BID17-021 — outside bid-17 phase-2 scope.

## Redesign plan

- Same MARKETING grammar as /partners: charcoal hero (kicker "TALK TO
  US"), paper bg, paperCard form card, gold CTA.
- **Preserved exactly:** `contact-inquiry` endpoint + payload, honeypot,
  mailto fallback, field set (4 fields + honeypot), phone CTA from
  `loadFooterContent`, persona-neutral copy verbatim, **no ChatWidget**
  (shared-surface rule — /partners has one, /contact must not gain one).
- Submitted state gets the same grammar.

## Edge cases

- Shared surface: grammar is B2B-consistent but copy stays neutral — no
  facility register words ("occupancy", "NOI") and no learner register
  ("your learning journey") in new chrome.
- `/org` and `/c/:slug` deliberately excluded (scope A) — documented,
  not forgotten.

## Acceptance criteria

- [ ] MARKETING grammar present; copy unchanged; no ChatWidget added.
- [ ] POST body identical; honeypot + mailto fallback intact.
- [ ] Unit + e2e pins same commit; axe clean.
- [ ] Staging-verified; prod untouched.

## Verification

Staging verified 2026-09-21: grammar live, no ChatWidget (shared-surface rule held), honeypot intact, axe 0. Same Jev gate as 021.
