# Pre-intake discovery — B2B blog modeled on sageage.com/blog

**Date:** 2026-09-25 · **Priority:** P2 · **Status:** discovery — pre-regression
**Persona:** Facility / B2B (senior care) — corporate-care register.
**Skill check:** `senior-living-agency` invoked — blog = agency-surace
content, evidence-anchored, "indistinguishable from top 3" bar.
Placement per request: senior-care footer (B2B side, `/for-communities`
family).

## Reference structure (crawled live 2026-09-25)

**Index page** (`/blog/`):
- H1 "The SageAge Blog: Expert Insight into Senior Living Marketing"
  + one-line subtitle
- Category filter bar: "All" + 16 categories
- 12 article cards per page: image, title, date, ~2-line excerpt,
  "Read More"
- "Next Page" pagination; **8 pages, 94 total articles**

**Article page** (`/blog/:slug`):
- Title, "← Previous" nav link, `date | categories` meta
- "In This Blog: Quick Take" box: What You'll Learn / The Big Shift /
  Reading Time / Key Takeaways bullets
- Long-form body: H2 sections, inline iStock photos (resident/staff/
  community lifestyle subjects), pull quotes, footer CTA form

**Click action:** card → same-tab navigation to article URL (slug).

## Answers to the scoping questions

| Question | Answer |
|----------|--------|
| Articles on reference | **94** (12/page × 7 + 10) |
| Needed to mimic page 1 | **12 minimum** |
| Needed for real pagination (>12) | **18–24 recommended** |
| New routes | **2**: `/blog` (index + filter + pagination) + `/blog/:slug` (article template, data-driven — NOT 94 hand-built pages) |
| Photos | Stock-style imagery, resident/staff/community subjects — same subject matter, never SageAge assets |

## Content sourcing (evidence rule)

SageAge's corpus is marketing-agency content. Ours must be
evidence-anchored per the agency skill: geragogy research, NIC/ASHA/
Argentum framing, resident-engagement→LOS→NOI thread. Category set for
mynaani (proposed): AI Learning, Resident Engagement, Family Confidence,
Senior Living Industry, Product Notes, Case Studies — 6, not 17.

## Pressure test vs current codebase (2026-09-25, multi-scan)

**BREAK-1 — SEO parity (critical).** SageAge's blog exists FOR search/
lead-gen. Our stack: SPA on Cloudflare Pages, one static `index.html`
title/OG block, **no per-route meta mechanism, no `document.title`
helper, no sitemap.xml, no robots.txt, no prerendering**. A React-route
blog ships invisible to crawlers and renders broken share cards.
Precedent that saves us: `public/terms.html` is already a hand-served
static HTML page. Same move: **build-time generator emits
`public/blog/*.html` static articles** — Cloudflare Pages serves them
natively, real SEO parity with WordPress, zero new infra. React
`/blog/:slug` alone is decoration, not marketing.

**BREAK-2 — Persona isolation vs shared footer.** Fat footer is a
shared surface (AGENTS rule: "copy must serve both audiences") but
`nav_links` is ONE global backend list (`backend/content/site_chrome.py`)
— no per-persona scoping exists. A "Blog" link pointing to B2B
senior-care content on learner-facing footers leaks persona. Options:
(a) blog declared shared-persona with mixed-audience copy (weakens
register), (b) extend siteChrome contract with persona-scoped link
groups, (c) link only inside `/for-communities` body, not the footer.

**BREAK-3 — Footer isn't global chrome.** `Footer` mounts on only 4
pages (Caregiver dark, Sources, ForCommunities dark; landing uses the
separate `LandingFooter`; Contact uses `loadFooterContent` mini-links
only). "Senior care footer" = ForCommunitiesPage's dark footer +
probably `/partners` (no footer today at all — adding one there is a
choice, not a given).

**SURVIVES — content backend.** `backend/content/site_chrome.py` dict
→ `/api/v1/site/footer` is exactly the pattern a blog should copy:
`blog_posts.py` + `/api/v1/site/blog` + `/api/v1/site/blog/:slug`,
updatable without frontend deploy. Fits modular monolith, no new DB.

**SURVIVES — routing/bundle.** Lazy routes + manualChunks; `/blog` +
`/blog/:slug` are 2 lazy chunks, trivially under the 100kB budget.
Deep links already work in prod.

**SURVIVES — tokens/tests.** MARKETING dark/paper (ADR-0034) fits;
axe + contrast + responsive e2e conventions exist; `Footer.test.tsx`
pins nav labels (27 asserts) — same-commit updates required.
`ChatWidget journey="facility"` + `trackScrollDepth` are the B2B
integration pattern to preserve on blog surfaces.

## Revised architecture (post-pressure-test)

1. `backend/content/blog_posts.py` — post objects (slug, title, date,
   categories, excerpt, quick-take, body blocks, image refs).
2. `/api/v1/site/blog` + `/api/v1/site/blog/:slug` — mirrors site chrome.
3. `BlogIndexPage` + `BlogPostPage` — lazy, MARKETING tokens, Footer
   dark, facility ChatWidget, trackScrollDepth.
4. **Build-time static-HTML generator** for articles (terms.html
   precedent) + `sitemap.xml` + `robots.txt` — without this the feature
   fails its purpose.
5. Footer link decision pending persona ruling (BREAK-2).

## Open questions for owner

1. Route: `/blog` (site-wide) or `/for-communities/insights`
   (B2B-scoped)? Footer link placement decides.
2. Content: who writes the first 12–24 articles — this session's agency
   skill can draft, but volume is a real commitment.
3. Backend: static data file vs API-served posts (siteChrome pattern
   exists for footer content).
4. Photos: stock license source (unsplash/iStock budget) vs generated.
