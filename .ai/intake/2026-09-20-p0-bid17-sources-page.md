# PS-BID17-004 — Inline sources on marketing pages → dedicated /sources page

**Status:** in-progress | **Severity:** P0 design-fidelity defect on staging
**Reported:** owner, staging screenshots 2026-09-20
**Parent:** `.ai/intake/2026-09-19-p1-bid17-production-implementation.md`

## Problem statement

Both bid-17 pages render a long inline "Sources" reference list at the
bottom — not in the approved mock. Owner directive: create a dedicated
`/sources` page holding the references, and add a "Sources" link in the
footer that loads it.

## Fix

- New `SourcesPage.tsx` at `/sources`: light paper document page,
  persona-partitioned lists ("For caregivers" 7-source set,
  "For communities" 7-source set) with the same name + why annotations.
  Capped measure (document page — deliberately NOT full-bleed), shared
  `Footer` (default variant — it is a persona-neutral shared surface).
- Remove the inline Sources sections and data arrays from
  `CaregiverPage`/`ForCommunitiesPage`.
- Add `{"label": "Sources", "href": "/sources"}` to
  `backend/content/site_chrome.py` nav_links (backend-served per
  MKT-FOOTER-001) and the frontend FALLBACK so the link is present even
  if the endpoint is down.
- Route added in `App.tsx` as a lazy route.

## Edge cases checked

- Footer nav grows to 7 links — within the ≤6-ish doormat budget noted
  in the footer intake; verify it doesn't wrap awkwardly on mobile.
- `test_site_chrome.py` asserts `len(nav_links) >= 4` — safe.
- Persona isolation: both sets visible on one shared page, clearly
  grouped — the *lists* stay partitioned (no cross-referencing claims);
  acceptable since /sources is a shared evidence surface, not a
  journey surface.
- Page must not require auth; must carry the footer + legal links.

## Acceptance

- `/sources` renders both grouped lists, all links valid URLs.
- Footer (both variants) shows a "Sources" link to `/sources`.
- Marketing pages no longer render inline sources; pages keep
  `data-contract-exemption` + all other pins.
- axe clean; unit + e2e pins updated same commit.
