# Landing Page Rubric — Older-Adult / Geragogy Alignment

**Process:** v9.51
**Date:** 2026-08-27
**Scope:** Evaluate Mynaani’s landing page against the top 15 senior-focused
sites and AARP heuristics.

## Scoring

| Score | Meaning |
|---|---|
| 0 | Missing or does not meet the criterion |
| 1 | Partially meets the criterion |
| 2 | Meets the criterion fully |

## Dimensions

### 1. Immediate value communication

| Criterion | Weight | Evidence source |
|---|---|---|
| Headline states a clear benefit in plain language | 2 | Content, `hero.headline` |
| Subheadline supports the headline with one sentence | 1 | Content, `hero.subheadline` |
| CTA describes the next step accurately | 2 | `call_to_action` labels |

### 2. Visual trust and relatability

| Criterion | Weight | Evidence source |
|---|---|---|
| Hero image shows relatable older adult(s) | 1 | Image asset |
| Image is warm, non-stock, and supports the message | 1 | Image asset |
| No visual clutter or competing claims | 1 | RenderProposal density |

### 3. Readability and accessibility

| Criterion | Weight | Evidence source |
|---|---|---|
| Body text ≥ 16 px | 2 | `TYPOGRAPHY.bodySizePx` |
| Headings noticeably larger than body (≥ 1.2×) | 1 | `TYPOGRAPHY.headingScale` |
| Strong color contrast for text and buttons | 1 | Tokens / WCAG check |
| Keyboard focus visible and logical | 1 | Manual check |

### 4. Action clarity

| Criterion | Weight | Evidence source |
|---|---|---|
| One primary, high-contrast CTA is visible above fold | 2 | Component render |
| Secondary actions are visually subordinate | 1 | Button styling |
| Total visible actions ≤ 5 | 1 | RenderProposal |

### 5. Trust and safety

| Criterion | Weight | Evidence source |
|---|---|---|
| Clear statement of what is free and what is not | 1 | Content, CTA notes |
| No urgency, scarcity, or fear-based language | 2 | Copy review |
| Trusted-source cues (nonprofit, gov-style, or clear privacy) | 1 | Content / footer |

### 6. Mobile and responsive

| Criterion | Weight | Evidence source |
|---|---|---|
| Single-column, readable layout at 320 px | 1 | Manual check |
| Tap targets ≥ 44 × 44 px | 1 | Button padding |
| No horizontal scrolling | 1 | Manual check |

### 7. Contract compliance (Mynaani-specific)

| Criterion | Weight | Evidence source |
|---|---|---|
| Only V1 components used | 1 | RenderGuard |
| Only token colors and spacing | 1 | Tokens audit |
| No disallowed motion or reflow | 1 | Motion / layout check |

## Total possible: 23

## Rating

| Score | Interpretation |
|---|---|
| 0–8 | Critical gaps; page should not ship |
| 9–14 | Acceptable for MVP but needs work |
| 15–19 | Strong landing page for this audience |
| 20–23 | Excellent, reference-class for older adults |

## How to use

Score the live `https://noni-web.pages.dev/` page and the source
`LandingPage.tsx` against each criterion. Document evidence under
`EVI-HERO-RUBRIC` in the knowledge graph.
