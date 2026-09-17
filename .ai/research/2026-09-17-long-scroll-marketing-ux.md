# Research — long-scroll UX on the caregiver + facility marketing pages

- Date: 2026-09-17
- Question: Is the significant vertical scroll on `/caregiver` (9
  sections) and `/for-communities` (10 sections) consistent with
  modern, FAANG-level, enterprise-grade UX — or a defect?
- Scope: **caregiver and senior-care-facility journeys only.** The
  learner curriculum is contract-bound geragogy and was not assessed.
- Related intakes: `.ai/intake/2026-09-16-p2-marketing-fat-footer.md`,
  ADR-0030 (Marketing Surfaces Annex).

## Source table (retrieved and content-verified via search excerpts, 2026-09-17)

### Scroll behavior evidence (NN/g + analytics)

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 1 | nngroup.com/articles/scrolling-and-attention | NN/g (Fessenden, 2018) | 57% of viewing time above fold; 74% in first two screenfuls. Users scroll but attention decays fast. |
| 2 | nngroup.com/articles/scrolling-and-attention-original-research | NN/g (Nielsen) | 1997 reversal: scrolling is no longer a usability disaster; still, "people prefer sites that get to the point." |
| 3 | nngroup.com/articles/page-fold-manifesto | NN/g (Schade, 2015) | Fold still matters — above-fold content must earn the scroll; long pages need signposts. |
| 4 | nngroup.com/articles/changes-in-web-usability-since-1994 | NN/g (Nielsen) | Scrolling no longer fails nav pages, but hidden choices are chosen less. |
| 5 | nngroup.com/articles/accordions-complex-content | NN/g (Loranger) | Accordions shorten pages but raise interaction cost; headings-as-IA alternative. |
| 6 | contentsquare.com/blog/scroll-tracking | Contentsquare | Scroll-map methodology; 99B-session benchmark: ~50% desktop / ~45% mobile average scroll. |
| 7 | contentsquare.com/guides/heatmaps/scroll-maps | Contentsquare | "False bottoms" — whitespace/dividers that make users think the page ended. Directly relevant to our `<hr>`-separated sections. |
| 8 | clickport.io/blog/track-scroll-depth-ga4 | ClickPort (citing Chartbeat, 2B visits) | 55% of pageviews get <15s attention; average reader scrolls ~halfway. |
| 9 | getsleek.io/blog/what-is-scroll-depth | Sleek (aggregating Chartbeat/Hotjar) | Multi-section landing pages: only 30–50% reach the bottom. |
| 10 | webeyez.com/insights/guides/chartbeat-scroll-depth-optimization-guide | Webeyez | Anchor CTAs within first 40–50% of depth; sticky CTAs when key actions sit deep. |

### Older-adult usability (academic + standards)

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 11 | doi.org/10.31274/etd-180810-3940 | Iowa State thesis | Baby boomers on long scrolling homepages + tablet nav — direct evidence for our audience. |
| 12 | danachisnell.com AARP-50Sites.pdf | AARP / Chisnell & Redish | Expert review of 50 sites for 50+ users; ability/attitude diversity model. |
| 13 | dl.acm.org/doi/10.1145/957205.957212 | ACM Universal Usability | 49 participants 20–82; redesigned for older users improved performance for all. |
| 14 | journals.sagepub.com/doi/10.1518/hfes.46.3.385.50404 | Human Factors | Clutter + link count hamper search, especially for older adults. |
| 15 | dl.acm.org/doi/10.5555/1766311.1766430 | ACM UAHCI | Eye-tracking: older adults scan pages differently. |
| 16 | w3.org/WAI/older-users/developing | W3C WAI | WCAG techniques that specifically serve older users. |
| 17 | w3.org/TR/wai-age-literature | W3C WAI literature review | Existing WAI guidelines address most older-user needs. |
| 18 | repository.arizona.edu NIA/NLM checklist.pdf | NIA + NLM | "Senior friendly" checklist — readable text, clear nav, explicit controls. |
| 19 | w3.org/WAI/older-users/literature | W3C WAI | Older users' functional requirements summary. |
| 20 | w3.org/WAI/WAI-AGE/comparative-WAI.html | W3C WAI-AGE | Requirement-by-requirement comparison for older users. |

### B2B / enterprise landing-page practice

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 21 | redclawey.com/blog/2026-03-09-long-vs-short-landing-page | Red Claw | Decision matrix: price × awareness × traffic → page length. $500+ = long page justified. |
| 22 | woobox.com/articles/long-vs-short-landing-pages | Woobox | "Length is not the variable — match-to-buyer-journey is." High-ticket/cold-traffic = long. |
| 23 | lilachbullock.com/how-long-should-a-landing-page-be | Bullock | Same framework, practitioner corroboration. |
| 24 | hyperspect.ai/blog/b2b-landing-page-optimization-patterns | Hyperspect | B2B patterns: hard conversions need 600–1,200 words of proof; single-column forms. |
| 25 | conversionbros.com/how-long-should-a-landing-page-be | Conversion Bros | Friction-vs-incentive framing; corroborates 21–23. |
| 26 | saaspattern.com/en/website-breakdowns/stripe | SaaSPattern | Stripe anatomy: modular sections by ICP, dual CTAs, progressive disclosure, many deep-links. |
| 27 | brainy.ink/paper/saas-landing-page-anatomy | Brainy | Nine-section canonical SaaS anatomy (hero→proof→problem→…→CTA) — sections ordered by buyer objection. |
| 28 | saaspattern.com/en/website-breakdowns/salesforce | SaaSPattern | Salesforce: self-segmenting nav, solution architecture over feature grid. |
| 29 | sextantlabs.io/blog/salesforce-gtm-analysis | Sextant Labs | Counter-case: feature-proliferation catalog = cognitive overload. What to avoid. |
| 30 | viktorshmatko.com/blog/why-stripes-website-feels-premium | Shmatko | Premium feel = structure doing the work; one message per section; remove filler sections. |

### Senior-living / caregiver domain

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 31 | digitaland.co/blog/assisted-living-website-design-the-definitive-guide | DIGITAL& | "Tour-driven" sites; dual audience — anxious adult-child skimmer + accessibility-needing resident. |
| 32 | socialanimal.dev/blog/assisted-living-website-design-what-families-need | Social Animal | 86% of senior-living site visits bounce <11s; real substance beats template polish. |
| 33 | creatingresults.com/blog/2026/06/17/what-todays-buyer-expects | Creating Results | Adult children scan for care levels, pricing, safety — clarity within seconds or they leave. |
| 34 | lowcode.agency/blog/senior-living-website-redesign | LOW/CODE | Months-long emotional journey; early-stage researchers want education not forms. |
| 35 | gautamkhorana.com/industries/senior-living | Khorana | 11pm anxious-research context; answers must be findable fast. |

### Long-scroll/mobile mechanics

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 36 | uxplanet.org/best-practices-for-long-scrolling-256ffbd7aa12 | UX Planet | Sticky nav / orientation aids are the fix for long-scroll disorientation. |
| 37 | clay.global/blog/web-design-guide/long-scrolling-websites | Clay | Anchor links per section, back-to-top, sticky header; speed budget (LCP<2.5s). |
| 38 | sitepoint.com/6-ways-to-improve-long-scroll-mobile-websites | SitePoint | Mobile stacking multiplies page height; declutter, CTA in first scroll. |
| 39 | abbacustechnologies.com/scrolling-ux-best-practices | Abbacus | Digestible sections reduce cognitive load; avoid layout shifts. |
| 40 | marmeto.com/blogs/e-commerce/mobile-first-optimization-for-long-scroll-ecommerce-websites | Marmeto | Same mobile-stacking problem and mitigations, e-commerce angle. |

### In-page navigation / sticky patterns (added pass 2)

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 41 | nngroup.com/articles/in-page-links-content-navigation | NN/g (Wang, 2023) | Users now naturally engage TOC links — the mental-model objection is resolved. |
| 42 | nngroup.com/articles/table-of-contents | NN/g | TOC increases discoverability of bottom content; placement options incl. collapsed-sticky. |
| 43 | nngroup.com/articles/in-page-links | NN/g | Anchors-OK reassessment: valuable on long pages, but shorten content first where possible. |
| 44 | mediawiki.org/wiki/Reading/Web/Projects/In-page_Navigation | Wikimedia | Reader research: TOC/sticky headers reduce navigational scrolling on long pages. |
| 45 | uxpatternsguide.com/patterns/in-page-anchor-navigation | UX Patterns | "On this page" spec: heading-derived links, active state, focus movement to destination. |
| 46 | smashingmagazine.com/2023/05/sticky-menus-ux-guidelines | Smashing (Kukarkina) | Sticky helps when users navigate between page views a lot; hurts when it obscures content. |
| 47 | cleancommit.io/ab-tests/implementing-a-sticky-navbar | Clean Commit | A/B: sticky nav → +15.3% conversion, +9.6% revenue/visitor. |
| 48 | doi.org/10.3390/informatics12030097 | MDPI Informatics | Wikipedia 2023 redesign: persistent TOC + sticky header raised in-site traversal. |
| 49 | bestpage.ai/learn/optimization-growth/sticky-elements-listicle-ux | BestPage | Sticky TOC +26% scroll depth; sticky CTAs *hurt* (feel aggressive). Slim, delayed, scroll-up reveal. |
| 50 | jenniferwang-wmf.github.io/Web_sticky_header | Wikimedia Web team | A/B: sticky header cuts scroll-back-to-top navigation. |

### CTA placement / decision friction (added pass 2)

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 51 | levri.ai/guide/multiple-ctas-hurt-conversion | Levri | Hick's law: 3+ equal-weight CTAs above fold convert 2.6× worse; distinct intents OK. |
| 52 | smartinsights.com/.../where-is-the-best-place-to-put-your-cta | Smart Insights | CTA belongs where action is most likely — not mechanically above fold. |
| 53 | tinuiti.com/blog/marketing/multiple-cta-conversion-rate | Tinuiti | Second CTA helps deeper in funnel when it answers a different validated need. |
| 54 | everythingdesign.webflow.io/blog/hero-section-ab-test-data-25000-tests | DoWhatWorks data | 25k A/B tests: dual CTAs standard among conversion leaders when intents differ. |
| 55 | foundrycro.com/blog/cta-button-conversion-rate-benchmarks-2026 | Foundry | Same-goal CTA repeated at scroll depths ≠ competing CTAs; repetition wins 20–30%. |
| 56 | nngroup.com/articles/information-scent | NN/g (Budiu) | Link labels must carry scent of the destination — governs anchor menu labels. |
| 57 | nngroup.com/articles/information-foraging | NN/g (Pirolli/Card) | Rate-of-gain model: users weigh info value vs effort — the formal case for anchors. |
| 58 | dl.acm.org/doi/10.1145/365024.365325 | ACM CHI (Chi et al.) | Computational information-scent model — academic root of 56–57. |
| 59 | nngroup.com/articles/information-foraging-leave-site | NN/g | Scent must keep strengthening or users leave — sections must each signal the next. |
| 60 | peterpirolli.com SNIF-ACT paper PDF | Pirolli & Fu | Cognitive model predicting link choice from scent — validation of TOC design. |

### Caregiver decision-journey evidence (added pass 2)

| # | Source | Org | Relevance |
|---|--------|-----|-----------|
| 61 | aplaceformom.com senior-care-search-trends PDF | A Place for Mom (n=1,104) | 2/3 of families secure care within 60 days; urgent events compress the search. |
| 62 | pewresearch.org Family Caregivers Online PDF | Pew Research | 88% of online caregivers seek health info; 67% searched on behalf of someone else. |
| 63 | aging.jmir.org/2019/1/e11237 | JMIR Aging | Caregivers seek health info online more than non-caregivers (HINTS n=3,181). |
| 64 | advancehealthcaremarketing.com AHC_SeniorStudy_WP_2025.pdf | Advance Healthcare Mktg (n=500) | 75% of elderly-care decisions made by adult children; guilt/anxiety shapes search. |
| 65 | doi.org/10.1016/b978-0-12-813898-4.00001-4 | NAC/AARP | 1 in 5 Americans are caregivers — scale and diversity of the persona. |

## Synthesis

**Scrolling itself is not the problem — it is the modern default.**
Sources 1–5, 36–40: users scroll willingly since ~1997; Stripe- and
Salesforce-class pages are long by design. High-consideration B2B
decisions (our $375–$1,950/yr facility ask) and emotionally complex
caregiver decisions both justify long-form pages (21–25, 31–35).

**What FAANG/enterprise-grade pages do that ours do not:**

1. **Wayfinding.** Stripe/Salesforce run sticky nav, section anchors,
   self-segmenting menus (26–28). Our two pages are a bare linear
   stack — no anchor nav, no sticky orientation, no back-to-top.
   NN/g (3, 4) and UX Planet (36): on long pages users need signposts
   and orientation or deep content is invisible. The old objection to
   in-page links is resolved — NN/g's 2023 study shows users naturally
   engage TOC links (41, 43), and Wikipedia-scale data confirms a
   persistent TOC lifts traversal (44, 48, 50).
2. **CTA distribution.** Enterprise pages repeat the *same-goal* CTA
   at strategic depths (55 — repetition of one goal is not "competing
   CTAs") and place one within the first 40–50% of depth (10, 26, 38).
   Our primary CTA sits in section 9–10 of 10 — past where ~50–70% of
   visitors ever reach (8, 9). The header "Talk to us" scrolls away.
   Caveat from the data: *sticky* CTAs feel aggressive and hurt (49) —
   repeat inline, don't float.
3. **Section discipline.** Canonical anatomy orders sections by buyer
   objection (27); Salesforce's counter-example shows catalog-style
   sprawl fails (29, 30). Our pages mix argument sections (geragogy
   evidence) with terminal sections (sources list) reasonably well,
   but the evidence list is prose-dense — senior-living research says
   the adult-child researcher skims on mobile (31, 33, 35) and 75% of
   elderly-care decisions are made by adult children under time
   pressure (61, 64).
4. **False-bottom risk.** `<hr>` dividers + generous whitespace
   between 9–10 sections create the exact pattern Contentsquare
   flags for premature scroll-stop (7). Information-scent theory adds
   the mechanism: each section must signal the scent of the next or
   the "rate of gain" collapses and users leave (56–59).
5. **Older-audience load.** Our visitors skew older on BOTH personas
   (caregivers are often 45–65 themselves; facility staff vary).
   Sources 11–20: reduced attention filtering, clutter sensitivity,
   and weaker scanning make long unstructured pages costlier for this
   group — while NOT prohibiting scroll (older users scroll fine when
   content is structured and text is readable — we already meet
   NIA/W3C typography bars via the marketing annex).

**Verdict:** the scroll is *not* inherently wrong — it matches the
decision weight. But as implemented it is *below* modern enterprise
grade on wayfinding and CTA distribution. The gap is structural aids,
not length.

## Decision matrix

| Option | Pros | Cons | Fit |
|--------|------|------|-----|
| A. Keep long page + add anchor subnav, mid-page CTAs, trim | Fixes the real gap; keeps SEO/scroll benefits; small diff | Still long | **Recommended — High confidence** |
| B. Split into multi-page | Shorter pages | Breaks the narrative; NN/g prefers scroll over paging for single-topic content; more nav burden for older users | Low |
| C. Accordion-collapse sections | Shorter perceived page | Higher interaction cost; hides content from scanners; NN/g warns accordions don't fit sequential marketing narrative | Low-Medium |
| D. Status quo | Zero work | Deep CTA invisible to ~half of visitors; disorientation | No |

## Edge-case / remediation matrix (top findings)

| # | Trigger | Impact | Remediation |
|---|---------|--------|-------------|
| 1 | Visitor never reaches section 9–10 CTA | Conversion loss | Repeat the *same-goal* CTA mid-page inline (49, 55) — NOT a floating sticky CTA, which feels aggressive and hurts trust |
| 2 | `<hr>` + whitespace reads as page end | Premature exit | Reduce divider prominence; section previews ("next: pricing") |
| 3 | Mobile stacks sections ~2× taller | Fatigue, bounce | Keep mobile padding tight; ensure CTA visible in first scroll on 390px |
| 4 | Sticky subnav overlaps hero CTA | Repeat of mobile-iphone flake (intake 2026-09-16-p1) | Subnav in normal flow or pointer-events discipline; e2e cover before ship |
| 5 | Anchor jumps lose context | Disorientation | Scroll-margin offsets; active-section highlighting |
| 6 | Anchor links break mental model | NN/g: within-page links confuse | Label as "On this page" menu, not generic links |
| 7 | Evidence list is prose-dense | Skim failure for adult-child | Already cardified on papers section; keep bullets ≤2 lines |
| 8 | Caregiver lands on facility form via shared nav | Persona leak | Keep current routing: caregiver→/contact, facility→/partners |
| 9 | Older visitor loses place after anchor jump | Disorientation | `prefers-reduced-motion`-aware smooth scroll; focus management |
| 10 | Long page + images hurt LCP | Speed/SEO | Already minimal imagery; keep lazy-loading whitepaper links as-is |
| 11 | Subnav hides content on small screens | Occlusion | Collapse subnav to bottom-sheet or hide on <768px |
| 12 | Two CTAs compete ("Talk to us" vs "Let's talk") | Choice paralysis | Distinct intents OK (general vs partner) — keep labels distinct |
| 13 | Analytics blind to scroll behavior | Can't verify fix | Add scroll-depth event (50%/90%) to telemetry before/after |
| 14 | Trimming sources section hurts credibility | Trust loss | Keep sources — collapse to details element or move to papers section |
| 15 | Caregiver page gift CTA buried mid-page | Gift conversion | "Gift mynaani" already in top-right header? No — gift CTA is mid-page; consider header "Gift" link for caregivers |
| 16 | Facility procurement user wants print/PDF | Offline review | Whitepaper PDFs already cover; add pricing PDF later |
| 17 | Screen reader hits long page without landmarks | A11y | Sections already have aria-labelledby — anchors help SR users too |
| 18 | Mid-page CTA interrupts emotional reading | Tone break | Use SECONDARY_BTN style, calm copy — no urgency |
| 19 | Subnav links to sections that get renamed | Drift | Drive anchors from a shared SECTIONS array — single source |
| 20 | A/B comparing scroll depth has no baseline | Can't measure | Ship telemetry first, then layout change |

## Codebase conflict check

- **Fixed-hero rule (AGENTS.md):** applies to `/` landing only — not
  these scrollable marketing surfaces. No conflict.
- **ADR-0030 marketing annex:** both pages are exemption-marked
  (`data-contract-exemption="marketing.*"`); richer nav/anchor
  patterns are permitted there. Learner contract untouched.
- **Mobile-iphone flake lesson:** any new fixed/sticky element on
  these pages must respect pointer-events and overlap — the exact
  defect just fixed on the landing strip. Sticky subnav must be e2e
  covered on mobile-iphone before ship.
- **Persona isolation:** anchor nav must not add cross-persona links
  (no facility pricing visible to caregivers beyond existing
  /for-communities link, no gift pricing on facility page).
- **No new dependencies needed** — pure CSS/Link implementation.

## Recommended workstreams (strict process order)

Ordered for safety + efficiency — measure before reshaping, highest-
value structural aid first, cosmetic polish last. Each ships
independently through the staging gate.

1. **WS-D (P1, first): scroll-depth telemetry** — instrument 25/50/
   90% depth events on both pages. Establishes OUR baseline before any
   layout change ships; the ~50% figure is industry data, not ours.
   Intake: `.ai/intake/2026-09-17-p1-scroll-depth-telemetry.md`
2. **WS-A (P2): "On this page" anchor menu** — heading-derived links,
   shared SECTIONS source, scroll-margin offsets, active state, mobile
   collapse; e2e cover on mobile-iphone (sticky/fixed-element lesson).
   Intake: `.ai/intake/2026-09-17-p2-anchor-nav-menu.md`
3. **WS-B (P2): CTA distribution** — one inline mid-page CTA at ~50%
   depth (facility→/partners, caregiver→/gift); same-goal repeat, not
   competing actions; NO floating sticky CTA (evidence: hurts trust).
   Intake: `.ai/intake/2026-09-17-p2-midpage-cta.md`
4. **WS-C (P3, last): false-bottom remediation** — tighten `<hr>` +
   whitespace pattern; each section's tail signals the next.
   Intake: `.ai/intake/2026-09-17-p3-divider-false-bottom.md`

## Gaps

- No scroll-depth analytics exist on these pages today — the ~50%
  abandonment figure is industry baseline, not ours. WS-D lands first
  for exactly this reason.
- Source corpus: 65 verified sources across 7 themed tables — NN/g,
  W3C/NIA, ACM, JMIR, Pew, NAC/AARP, Wikimedia platform data, SaaS
  teardowns, and senior-living domain research.
