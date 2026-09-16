# Research — Fat footer for marketing surfaces (WS-2)

**Date:** 2026-09-16
**Intake:** `.ai/intake/2026-09-16-p2-marketing-fat-footer.md`
**Parent research:** `.ai/research/2026-09-16-landing-footer.md`
(29 verified sources on footer patterns, a11y, legal, geragogy —
reused where directly applicable; this memo adds fat-footer-specific
evidence)
**Question:** What structure/content should a shared fat footer on
`/caregiver` + `/for-communities` take, modeled on GetSetUp?

## Supplemental sources (fat-footer-specific)

| # | Source | Org | Key finding |
|---|---|---|---|
| S1 | ui-patterns.com/patterns/FatFooter | UI-Patterns | Fat footer = sitemap footer. Standard contents: About, ToS, Privacy, sitemap shortcuts, Contact, address/phone, social. Same footer on all pages. Use to shortcut hierarchy — our marketing pages have shallow IA, so a nav row (not multi-column sitemap) fits. |
| S2 | ixdf.org — sitemap footers | Interaction Design Foundation | Repeating navigation in the footer reduces effort — users reaching page bottom shouldn't have to scroll back up. Recommends footer nav on every page. |
| S3 | welie.com footer-sitemap pattern | Welie pattern library | Footer sitemap lets users who scrolled to the bottom jump anywhere; can organize differently than main nav (e.g., LinkedIn, Apple + breadcrumbs). |
| S4 | optimalworkshop.com — footer anatomy | Optimal Workshop | Footer = "reached the bottom" signal + safety net; conventions: privacy, copyright; IKEA example shows fat footer adapting by page depth. |
| S5 | baymard.com/blog/footer-links-ecommerce | Baymard (from parent) | Semantically group footer links under headings; mobile footers depend on clear group headings more than desktop. |

## Inherited sources (from parent memo, most load-bearing here)

- NN/g Footers 101 (verified): doormat nav — repeat global nav in
  footer for long pages; utility links minimum.
- GOV.UK footer (verified): link set = Privacy, Accessibility,
  Cookies, Terms, help; consistent help links (WCAG 3.2.6).
- CCPA §7011(d) (verified): conspicuous "privacy" link — footer is
  the conventional conspicuous location.
- W3C APG landmarks: top-level `<footer>` → contentinfo; one per page.
- WCAG 2.2 SC 2.5.8: ≥24px targets.
- NIA/NLM senior-friendly checklist: consistent nav placement,
  careful link labels.
- AuditBuffet: shared Footer component in root layout pattern.

## Structure decision

GetSetUp's footer is a **single-row doormat nav + legal row**, not a
multi-column sitemap — right-sized for a shallow IA. Mynaani's IA is
equally shallow (~5 public surfaces), so the GetSetUp *structure*
(centered brand → nav row → hairline → legal row) maps directly.
What does NOT map: GetSetUp's link inventory (Careers, Press, About,
Host a Session have no mynaani equivalents).

**Proposed content model** (all existing routes):

| Region | Content | Rationale |
|---|---|---|
| Brand | mynaani mark, centered, small | GetSetUp parity; reinforces brand at page end |
| Nav row | For learners · For caregivers · For senior facilities · Gift · Research · Help | Doormat nav (NN/g) covering all public surfaces; ≤6 links per geragogy density cap |
| Legal row | Privacy Policy · © {year} mynaani | CCPA §7011(d); GOV.UK minimum set |

Per-page variant: the current-page link de-emphasized or replaced by
the cross-links each page already shows (preserve existing behavior).

## Decision matrix

| Option | Verdict |
|---|---|
| Shared `Footer.tsx`, GetSetUp structure, ≤6 nav links | **Selected — High confidence** |
| Multi-column sitemap footer | Rejected — IA too shallow; adds scanning load for seniors |
| Keep current minimal footers | Rejected — missing legal row (CCPA), no doormat nav benefit |
| Full GetSetUp clone incl. Careers/Press | Rejected — no such pages exist |

## Edge cases (WS-2 specific; inherits parent memo's 30)

| # | Edge case | Remediation |
|---|---|---|
| F1 | Current-page self-link in nav row | Dim/omit own link per page (caregiver footer keeps "For senior facilities", drops "For caregivers") |
| F2 | "Research" anchor — `/caregiver` and `/for-communities` use different section ids (`#b2b-papers` etc.) | Point at the page's own papers section, or `/for-communities#b2b-papers` canonically |
| F3 | Mobile stacking | Wrap nav row, keep legal row split — Baymard: mobile needs clear grouping |
| F4 | `/terms` doesn't exist | Omit until created (flagged in intake) |
| F5 | Help auth-gate | `Contact` mailto signed-out; `/help` only if signed-in — shared component takes auth prop |
| F6 | Two contentinfo landmarks if a page forgets to remove old footer | Delete inline footers during integration; unit test asserts single footer |
| F7 | Logo asset weight | Reuse `mynaani-logo.webp` already in bundle; small size |
| F8 | axe contrast on `COLORS.surface` bg | border-top + surface bg already AA-compliant on both pages |
| F9 | E2E specs assert old footer content | Update caregiver.spec/community.spec footer assertions |
| F10 | Future pages (/help, /privacy) adopting footer | Component is portable; adoption is a follow-on decision (gap #4) |

## Gaps

Same as intake gaps: nav link set sign-off, /terms decision,
contact-target decision, rollout scope.
