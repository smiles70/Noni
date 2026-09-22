# PS-BID17-020 — Communities-path pages retain pre-bid-17 design

**Date:** 2026-09-21 · **Priority:** P2 · **Status:** investigated — awaiting scope decision
**Skill check:** `senior-living-agency` invoked (B2B surfaces); `error-taxonomy`
not applicable (no gate failure). Jev gate run — `.ai/research/2026-09-21-b2b-design-drift-jev.md`.

## Problem statement

The owner observed that several pages on the communities path do not match
the new bid-17 design; the forms pages appear to retain the original look.
Required: full deep inventory + Jev assessment of whether the drift is real
and whether exclusion was in scope.

## Inventory (confirmed in git + code, not assumed)

Bid-17 (8a4629c + PS-BID17-001..012 fixes) touched ONLY:

| Surface | Component | Status |
|---------|-----------|--------|
| `/caregiver` | CaregiverPage.tsx (917-line rewrite) | redesigned |
| `/for-communities` | ForCommunitiesPage.tsx (1075-line rewrite) | redesigned |
| footer bands + `/sources` | tokens.ts +27 (MARKETING group), SourcesPage | redesigned |
| **`/partners`** | PartnershipInquiryPage.tsx (499-line form) | **pre-bid-17 design** |
| **`/contact`** | ContactPage.tsx (335-line form) | **pre-bid-17 design** |
| **`/c/:slug`** | PartnerPage.tsx (76-line partner doorway) | **pre-bid-17 design** |
| **`/org`** | OrgDashboardPage.tsx (251 lines, auth-gated) | **pre-bid-17 design** |

Marker: redesigned pages carry 41–43 `MARKETING` token refs + charcoal
hero + proof band + uppercase register; the four untouched pages carry
zero. All share `design/tokens.ts` — the drift is structural (layout
grammar), not palette.

## Jev gate (jev-1.13.0, 9 questions, state = inventory evidence)

| Q | Result |
|---|--------|
| /partners consistent with new grammar | 0.05 — no |
| /contact consistent | 0.05 — no |
| /c/:slug consistent | 0.07 — no |
| /org consistent | 0.07 — no |
| Exclusion was in-scope (intentional) | 0.66 — likely yes (bid-17 was phase-2: caregiver+communities only) |
| Drift creates a trust seam on the B2B conversion path | 0.75 — yes |
| Drift is user-visible | 0.84 — yes |
| Priority scope | forms-only 0.66 (all-b2b 0.25, none 0.03) |
| Severity | moderate-trust-risk 0.83 |

## Options

- **A — Redesign the two forms pages first (Jev's pick).** `/partners` +
  `/contact` sit directly on the conversion path a visitor reaches from
  `/for-communities`. Smallest surface, highest seam value.
- **B — Redesign all four.** Adds `/c/:slug` (partner doorway — visitors DO
  hit it via campaign links) + `/org` (auth-gated, lower exposure).
- **C — Leave as-is.** Rejected: visitor-visible drift on a paid-conversion
  path (0.84 visibility, 0.75 seam).

## Edge cases

- `/c/:slug` is a hosted doorway — partner-branded by design; a redesign
  must preserve the partner-brand slot, not force Mynaani grammar.
- `/org` is auth-gated operational UI — visual consistency matters less
  than density/utility; a marketing-grammar pass may be wrong for it.
- Forms pages embed CRM tracker + honeypot — redesign must not touch
  `submit_partner_inquiry`/`submit_contact_inquiry` payload contracts.
- New styling must reuse `design/tokens.ts` MARKETING group — no inline
  hex (ADR-0034 palette rule).

## Acceptance criteria

- [ ] Owner picks scope: A (forms) or B (all four).
- [ ] Selected pages carry MARKETING grammar; zero new inline hex.
- [ ] Form payload contracts + honeypots untouched; CRM ingest still 204.
- [ ] Same-commit unit + e2e pins; axe clean; staging verify before prod.
