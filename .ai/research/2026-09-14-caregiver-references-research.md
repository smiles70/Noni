# Caregiver / for-communities References — Research Protocol & Triple-Check

**Date:** 2026-09-14 (revised)  
**Scope:** All external references and whitepapers linked from `CaregiverPage.tsx`, `ForCommunitiesPage.tsx`, and the related research/ADR/intake artifacts.  
**Method:** URL reachability (`curl -sL --max-time 15`), PDF text extraction (`pdftotext`), cross-check between page claims and PDF bibliographies, and web-search verification for blocked sources.

---

## 1. Research question

Do the research claims on the caregiver marketing page rest on real, reachable, and caregiver/geragogy-specific sources? Are the senior-facility page and the two downloadable whitepapers still grounded in the same geragogy/aging sources as before?

---

## 2. Caregiver page source table — page-cited references (7)

`CaregiverPage.tsx` (`SOURCES` array, lines 174–210) now uses a distinct set focused on family caregiving, technology support, and geragogy.

| # | Source | URL | HTTP | Verdict |
|---|--------|-----|------|---------|
| 1 | Tang X. et al. — "I Never Imagined Grandma Could Do So Well with Technology" (CSCW 2022) | `https://xinrutang.github.io/file/FamilyCSCW22/FamilyCSCW22.pdf` | 200 | Reachable; describes family caregivers' evolving roles in older adults' technology learning |
| 2 | Caregiver Action Network — CIC Caregiver Tech Insights Survey (2026) | `https://www.caregiveraction.org/wp-content/uploads/2026/05/CIC-Survey-2026.pdf` | 200 | Reachable; 272 family caregivers, 90% use digital tools, 38% spend 11+ hours/week on coordination |
| 3 | AARP / Age in Place Tech — 2025 Technology Trends: Older Adults and Caregiving | `https://www.ageinplacetech.com/files/aip/2025-technology-trends-older-adults-caregiving.doi_.10.26419-2fres.00891.007.pdf` | 200 | Reachable; caregivers 50+ adopt convenience/safety technology more than non-caregivers |
| 4 | JMIR Aging — Application-based interventions for family caregivers of older adults: scoping review (2026) | `https://aging.jmir.org/2026/1/e76115` | 202 | 202 status (likely pre-print/accepted); 49 studies on apps and caregiver outcomes |
| 5 | SSPH+ / Frontiers in Public Health Reviews — Digital Informal Care: The Use of Technology in Family Care (2025) | `https://www.ssph-journal.org/journals/public-health-reviews/articles/10.3389/phrs.2025.1608872/full` | 200 | Reachable; 110-study scoping review on digital tools for family care |
| 6 | Heliyon — The impact of family members on aging persons' technology use intentions (2025) | `https://doi.org/10.1016/j.heliyon.2025.e42252` | 200 | Reachable via DOI; family caregiver belief alignment predicts older adult technology use |
| 7 | Laganà L. et al. — Enhancing computer self-efficacy in older adults: a randomised controlled study | `https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/` | 200 | Reachable; age-appropriate, self-paced training improves attitudes and self-efficacy |

**Cross-check:** Only Laganà et al. also appears in the existing `Geragogy — the key to learning` whitepaper bibliography. The other six are caregiver-specific and are not currently in the two whitepapers, because the whitepapers are senior-facility / general geragogy deep-dives. The `CaregiverPage` now carries its own inline references rather than duplicating the community-page list.

---

## 3. Senior-facility page and whitepaper source table (unchanged)

`ForCommunitiesPage.tsx` retains the original seven geragogy/aging sources. These are also present in the whitepaper bibliographies.

| # | Source | URL | HTTP | Verdict |
|---|--------|-----|------|---------|
| 1 | Pew Research Center — How Americans' opinions and use of AI differ by age (2026) | `https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-use-of-ai-differ-by-age/` | 200 | Reachable |
| 2 | Nielsen Norman Group — Usability for Senior Citizens | `https://www.nngroup.com/articles/usability-seniors-improvements/` | 200 | Reachable |
| 3 | W3C WAI — Web Accessibility for Older Users: A Literature Review | `https://www.w3.org/WAI/older-users/literature/` | 200 | Reachable |
| 4 | Owsley C. — Vision and Aging, *Annual Review of Vision Science* | `https://www.annualreviews.org/content/journals/10.1146/annurev-vision-111815-114550` | 403 | Paywall / bot-guarded; verified via web search (DOI 10.1146/annurev-vision-111815-114550, Vol. 2, 2016) |
| 5 | Hasher L. & Zacks R.T. — Working memory, comprehension, and aging | `https://hasherlab.psych.utoronto.ca/abstracts/hasher_zacks_88.htm` | 200 | Reachable |
| 6 | JMIR (2025) — Cognitive load and learning performance in digital health education for older patients | `https://www.jmir.org/2025/1/e79430` | 202 | Unusual 202 status; article verified via web search (J Med Internet Res 2025;27:e79430, DOI 10.2196/79430) |
| 7 | Laganà L. et al. — Enhancing computer self-efficacy in older adults | `https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/` | 200 | Reachable |

---

## 4. PDF inventory

| Whitepaper | Local path | Pages | File size | Staging URL | Live URL | HTTP |
|---|---|---|---|---|---|---|
| The AI Gap | `frontend/public/whitepapers/the-ai-gap.pdf` | 10 | 121,787 B | `https://staging.noni-web.pages.dev/whitepapers/the-ai-gap.pdf` | `https://www.mynaani.com/whitepapers/the-ai-gap.pdf` | 200 |
| Geragogy — the key to learning | `frontend/public/whitepapers/geragogy-the-key-to-learning.pdf` | 8 | 106,736 B | `https://staging.noni-web.pages.dev/whitepapers/geragogy-the-key-to-learning.pdf` | `https://www.mynaani.com/whitepapers/geragogy-the-key-to-learning.pdf` | 200 |

### 4.1 Metadata

- **Creator:** Chromium / Skia PDF
- **Creation date:** 2026-09-05
- **Tagged:** No
- **Encrypted:** No
- **PDF version:** 1.4

Note: PDFs are not PDF/UA-tagged. They are marketing downloads, not the product UI, but a future P2 could make them tagged PDFs.

---

## 5. Bibliography cross-check

### 5.1 The AI Gap PDF

The references section (page 8–9 of 10) contains 17 named sources, including the senior-facility page-cited references above plus additional Pew, AARP, npj Digital Medicine, Campbell/Hasher/Thomas, Kalyuga, and NIA/NLM sources.

**Verdict:** The claim of "17 sources" is consistent with the extracted bibliography.

### 5.2 Geragogy PDF

The references section (page 7–8 of 8) contains 16 named sources, including the senior-facility page-cited references above plus additional AARP, Boulton-Lewis, Campbell/Hasher/Thomas, Kalyuga, Knowles/Holton/Swanson, and NIA/NLM sources.

**Verdict:** The claim of "16 sources" is consistent with the extracted bibliography.

### 5.3 URL wrapping issue in PDF text

`pdftotext` wraps some long URLs mid-string. This is only a text-extraction artifact; the actual link targets in the page code and PDFs are correct.

---

## 6. Claim verification

| Claim on caregiver page | Source(s) | Support |
|---|---|---|
| Family members play evolving roles in older adults' technology learning | Tang et al. 2022 | Directly supported |
| Caregivers already use digital tools but face coordination burden | Caregiver Action Network 2026 | Supported |
| Caregivers 50+ adopt convenience and safety technology more than non-caregivers | AARP / Age in Place Tech 2025 | Supported |
| Apps can support caregiver well-being and burden if well-designed | JMIR Aging 2026; SSPH+ 2025 | Supported |
| Family caregiver capability beliefs influence older adult technology use | Heliyon 2025 | Supported |
| Age-appropriate, self-paced training improves older-adult self-efficacy | Laganà et al. | Supported |

---

## 7. Decision / confidence

**Decision:** The `CaregiverPage` now has its own set of caregiver-specific, reachable, and verifiable references. The geragogy/learning foundation is preserved through Laganà et al., and the caregiving context is supported by six new sources. The senior-facility page and whitepapers remain unchanged and evidence-grounded.

**Confidence:** High for the 200 URLs; Medium for the two `202` responses (`aging.jmir.org` and `jmir.org`), which are unusual but resolve to the expected articles. Medium for source counts in PDFs because they rely on manual enumeration from `pdftotext` output.

---

## 8. Edge cases and remaining gaps

1. **JMIR Aging 202** — the 202 status may indicate an accepted-but-not-yet-final article. The DOI and title match the expected article.
2. **PDF/UA tagging** — marketing PDFs are not tagged. Not a functional blocker, but a future accessibility P2.
3. **Caregiver-specific whitepaper** — if the marketing team wants a caregiver-specific downloadable PDF, a new whitepaper should be generated that includes the seven caregiver page sources plus the existing geragogy literature.
4. **McKinsey / Demand Gen B2B references** — from a separate B2B intake; not on the public caregiver/facility surfaces.

---

## 9. Code / artifact references

- `frontend/src/components/CaregiverPage.tsx` — `SOURCES` array (lines 174–210)
- `frontend/src/components/ForCommunitiesPage.tsx` — `SOURCES` array
- `frontend/public/whitepapers/the-ai-gap.pdf`
- `frontend/public/whitepapers/geragogy-the-key-to-learning.pdf`
- `docs/decisions/0030-marketing-surfaces-annex.md` — marketing-surface exemption
