# PS-INSIGHTS-001 — "Insights" blog for the senior-care surface

**Date:** 2026-09-26 · **Priority:** P2 · **Persona:** Shared surface
(nav label "Insights"), B2B-anchored article content
**Pre-discovery:** `.ai/intake/2026-09-25-p2-blog-discovery-sageage.md`
**Library:** `.ai/research/2026-09-26-insights-blog-library.md`
(24 verified sources, quadruple-checked)
**Skills invoked:** `senior-living-agency` ✓; `journey-loop-guard`
(footer mount check) ✓ — Footer mounts only on `/caregiver`,
`/sources`, `/for-communities`; no purchase/paywall surface.

## Problem statement

The B2B senior-care surface has no content-marketing surface. SageAge's
`/blog` (94 posts, 12/page, category filter, Quick-Take article format)
is the benchmark. We cannot match their corpus, but the page can be
replicated exactly — with our articles evidence-anchored in the
verified library rather than opinion pieces.

## Confirmed root-cause/architecture findings (from pressure test)

1. **SEO requires static HTML.** SPA routes ship one title/OG for the
   whole site; no per-route meta mechanism exists. Precedent:
   `public/terms.html` static page. → build-time generator emits
   `public/insights/<slug>.html` + `sitemap.xml` + `robots.txt`.
2. **Footer is one global backend list** (`backend/content/site_chrome.py`
   → `/api/v1/site/footer`). "Insights" is a neutral shared label —
   persona-safe on learner footers while pointing to B2B-anchored
   content. Owner-approved recommendation.
3. **Content backend pattern exists** — mirror `site_chrome.py`:
   `backend/content/blog_posts.py` + `/api/v1/site/blog` index +
   `/api/v1/site/blog/:slug`, updatable without frontend deploy.

## Design (selected)

- **React:** `BlogIndexPage` (`/insights`) — H1, subtitle, category
  filter, 12 cards/page, Next pagination (SageAge-matched structure).
  `BlogPostPage` (`/insights/:slug`) — Quick-Take box, date|categories
  meta, "← Back to Insights", H2 body sections, footer CTA.
- **Static mirror:** generator script renders each post to
  `public/insights/<slug>.html` at build (title/OG/description/meta per
  article) — cards link to the static URLs. `sitemap.xml`, `robots.txt`.
- **Tokens:** MARKETING dark/paper (ADR-0034); `Footer variant="dark"`;
  `ChatWidget journey="facility"`; `trackScrollDepth("insights")`.
- **Content:** 12 articles drafted from the verified library in the
  whitepaper RESEARCH-BRIEF voice; every claim traced to a library row
  or KG node. Zero fabricated stats.
- **Footer:** add `{label:"Insights", href:"/insights"}` to backend
  `nav_links` + `Footer.tsx` FALLBACK + same-commit test updates.
  (Nav goes 7→8 links — shared-surface rule honored; no persona pricing.)

## Alternatives considered

- React-only SPA blog — rejected: dead SEO, broken share cards.
- Backend-rendered/blog CMS (headless) — rejected: new infra for 12
  static posts; revisit if volume grows past ~30.
- B2B-scoped footer link only — deferred: needs persona-scoped
  siteChrome contract; current label approach is safe.

## Acceptance criteria

- `/insights` renders filter + 12 cards; card → article (same-tab).
- Each article: Quick-Take box, ≥2 verified citations rendered as
  links, facility ChatWidget, scroll telemetry.
- `public/insights/*.html` served with unique title/OG; sitemap lists
  all; axe AA on index + one article; responsive matrix green.
- Footer "Insights" link present on all Footer mounts; learner pages
  unchanged; unit + e2e pins same-commit; `/purchase/*` untouched
  (verified by mount grep, no loop surface involved).

## Edge cases

- Empty category filter → show all; unknown slug → Insights index
  redirect (not blank).
- Generator must fail the build loudly on a post missing citation
  fields (no silent no-ops).
- Article images: stock-style resident/staff/community subjects —
  licensed or generated; never SageAge assets.

## Open items for owner

1. Confirm `Insights` label + `/insights` route (vs `/blog`).
2. Article volume for launch: 12 (one full page) is the minimum to
   mimic; pagination control can ship dormant until post 13.
