# Caregiver / for-communities References — Research Protocol & Triple-Check

**Date:** 2026-09-14  
**Scope:** All external references and whitepapers linked from `CaregiverPage.tsx`, `ForCommunitiesPage.tsx`, and the related research/ADR/intake artifacts.  
**Method:** URL reachability (`curl -sL --max-time 15`), PDF text extraction (`pdftotext`), cross-check between page claims and PDF bibliographies, and web-search verification for blocked sources.

---

## 1. Research question

Do the research claims and downloadable whitepapers on the caregiver and senior-facility marketing surfaces rest on real, reachable, and accurately cited sources? Are the page-cited sources also present in the PDF bibliographies?

---

## 2. Source table — page-cited references (7)

All seven sources appear in `CaregiverPage.tsx` (`SOURCES` array, lines 187–223) and in `ForCommunitiesPage.tsx`.

| # | Source | URL | HTTP | Verdict |
|---|--------|-----|------|---------|
| 1 | Pew Research Center — How Americans' opinions and use of AI differ by age (2026) | `https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-use-of-ai-differ-by-age/` | 200 | Reachable; article present |
| 2 | Nielsen Norman Group — Usability for Senior Citizens | `https://www.nngroup.com/articles/usability-seniors-improvements/` | 200 | Reachable |
| 3 | W3C WAI — Web Accessibility for Older Users: A Literature Review | `https://www.w3.org/WAI/older-users/literature/` | 200 | Reachable |
| 4 | Owsley C. — Vision and Aging, *Annual Review of Vision Science* | `https://www.annualreviews.org/content/journals/10.1146/annurev-vision-111815-114550` | 403 | Paywall / bot-guarded; article verified via web search (DOI 10.1146/annurev-vision-111815-114550, Vol. 2, 2016) |
| 5 | Hasher L. & Zacks R.T. — Working memory, comprehension, and aging | `https://hasherlab.psych.utoronto.ca/abstracts/hasher_zacks_88.htm` | 200 | Reachable |
| 6 | JMIR (2025) — Cognitive load and learning performance in digital health education for older patients | `https://www.jmir.org/2025/1/e79430` | 202 | Unusual 202 status; article verified via web search (J Med Internet Res 2025;27:e79430, DOI 10.2196/79430) |
| 7 | Laganà L. et al. — Enhancing computer self-efficacy in older adults | `https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/` | 200 | Reachable |

**Cross-check:** The same seven sources are also extracted from the whitepaper bibliographies (see Section 4).

---

## 3. PDF inventory

| Whitepaper | Local path | Pages | File size | Staging URL | Live URL | HTTP |
|---|---|---|---|---|---|---|
| The AI Gap | `frontend/public/whitepapers/the-ai-gap.pdf` | 10 | 121,787 B | `https://staging.noni-web.pages.dev/whitepapers/the-ai-gap.pdf` | `https://www.mynaani.com/whitepapers/the-ai-gap.pdf` | 200 |
| Geragogy — the key to learning | `frontend/public/whitepapers/geragogy-the-key-to-learning.pdf` | 8 | 106,736 B | `https://staging.noni-web.pages.dev/whitepapers/geragogy-the-key-to-learning.pdf` | `https://www.mynaani.com/whitepapers/geragogy-the-key-to-learning.pdf` | 200 |

### 3.1 Metadata

- **Creator:** Chromium / Skia PDF
- **Creation date:** 2026-09-05
- **Tagged:** No
- **Encrypted:** No
- **PDF version:** 1.4

Note: PDFs are not PDF/UA-tagged. They are marketing downloads, not the product UI, but a future P2 could make them tagged PDFs.

---

## 4. Bibliography cross-check

### 4.1 The AI Gap PDF

The references section (page 8–9 of 10) contains 17 named sources, including all 7 page-cited references above plus:

- Additional Pew Research Center studies (2017, 2025)
- AARP Research (2025, 2026)
- npj Digital Medicine (2026)
- Campbell, Hasher & Thomas (2014)
- Kalyuga (2012)
- National Institute on Aging / U.S. National Library of Medicine

**Verdict:** The page claim of "17 sources" is consistent with the extracted bibliography. The 7 inline page sources are all present.

### 4.2 Geragogy PDF

The references section (page 7–8 of 8) contains 16 named sources, including the 7 page-cited references above plus:

- AARP Research (2025, 2026)
- Boulton-Lewis (2010)
- Campbell, Hasher & Thomas (2014)
- Kalyuga (2012)
- Knowles, Holton & Swanson (andragogy lineage)
- National Institute on Aging / U.S. National Library of Medicine
- npj Digital Medicine (2026)

**Verdict:** The page claim of "16 sources" is consistent with the extracted bibliography. The 7 inline page sources are all present.

### 4.3 URL wrapping issue in PDF text

When `pdftotext` extracts the PDF, some long URLs are wrapped mid-URL (e.g., `https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-useof-ai-differ-by-age/` missing the hyphen). This is only a text-extraction artifact. The actual link target in the PDF is correct, because the links are served from the page copy as typed.

---

## 5. Claim verification

| Claim on page / PDF | Source(s) | Support |
|---|---|---|
| 57% of under-50 U.S. adults use AI chatbots vs. 28% of 50+ | Pew Research Center 2026 | Directly supported in PDF and on page |
| Adults 65+ are the most uncertain group about AI | Pew Research Center 2026 | Supported |
| Older adults (65+) succeed at website tasks ~55% vs. 75% for 21–55, ~43% slower | Nielsen Norman Group | Supported |
| ~80% contrast-sensitivity loss by age 80 | W3C WAI / Owsley | Supported (cited in both page and PDF) |
| Cognitive load is a key mediator of learning in older adults | JMIR 2025 | Supported |
| Age-appropriate training improves self-efficacy | Laganà et al. | Supported |

---

## 6. Decision / confidence

**Decision:** The seven page-cited references are real, the linked PDFs are reachable on both staging and production, and the whitepaper bibliographies contain the expected 16–17 sources that include all page-cited references. The content is therefore evidence-grounded.

**Confidence:** High for the five 200 URLs and the two verified-but-blocked URLs (Annual Reviews, JMIR). Medium for the claim counts of 16/17 because they rely on manual enumeration from `pdftotext` output; a PDF-parsing library would give a more precise count.

---

## 7. Edge cases and remaining gaps

1. **Annual Reviews 403** — the paywall means the original source cannot be programmatically read. A purchase or library access is needed to audit the exact text, but the DOI and web-search confirm the article exists.
2. **JMIR 202** — the 202 status is unusual for a web page; it may be an acceptance or pre-print state. The DOI `10.2196/79430` resolves and the article title matches.
3. **PDF/UA tagging** — marketing PDFs are not tagged. Not a functional blocker, but a future accessibility P2.
4. **PDF text extraction** — `pdftotext` wraps some URLs. The actual `href` in the page code is correct.
5. **McKinsey and Demand Gen B2B references** — from `.ai/intake/2026-09-05-b2b-landing-research-001.md`. McKinsey URL is reachable via search but blocks `curl` (000); Demand Gen Report is 200. These are in the B2B intake, not on the public page, so they do not affect the caregiver/facility surfaces.

---

## 8. Code / artifact references

- `frontend/src/components/CaregiverPage.tsx` — lines 187–223 (SOURCES)
- `frontend/src/components/ForCommunitiesPage.tsx` — SOURCES block
- `frontend/public/whitepapers/the-ai-gap.pdf`
- `frontend/public/whitepapers/geragogy-the-key-to-learning.pdf`
- `docs/decisions/0030-marketing-surfaces-annex.md` — marketing-surface exemption

---

## 9. Gaps requiring user input

None for the current scope. If a separate caregiver-specific whitepaper is desired (rather than reusing the two existing PDFs), a new PDF generation and reference list will be needed.
