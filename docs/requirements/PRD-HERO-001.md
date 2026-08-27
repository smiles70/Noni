# Product Requirements Document — HERO-001

**Process:** v9.51
**ID:** PRD-HERO-001
**Date:** 2026-08-27
**Owner:** Product / Engineering
**Source:** `FRD-HERO-001`

## Non-functional requirements

### NFR-001 — Performance

The hero landing page MUST achieve Largest Contentful Paint (LCP) < 2.5s
on a 3G-equivalent connection and the hero image MUST be lazy-loaded or
served with modern image formats at reasonable dimensions.

### NFR-002 — Accessibility

The landing page MUST meet WCAG 2.2 AA:
- Color contrast ≥ 4.5:1 for body text.
- Focus indicators visible on all interactive elements.
- Alt text for the hero image.
- Keyboard-navigable CTAs in visual order.

### NFR-003 — Geragogy

- No motion except permitted opacity fades (120–180ms).
- No urgency language, countdowns, or scarcity framing.
- No pure black/white or neon colors.
- Maximum 3 visible text levels.

### NFR-004 — Mobile

The hero layout MUST adapt to a single column at viewport widths ≤ 768px
without horizontal scrolling and without reducing body text below 16px.

### NFR-005 — Bundle

The production bundle MUST contain no localhost references and no
third-party brand strings. Bundle verification (`npm run postbuild`) MUST pass.

## Technical requirements

### TR-001 — No new envelopes

The redesign MUST use the existing `landing.page` UI state envelope. No new
backend envelopes or API endpoints are required.

### TR-002 — Component inventory

Only V1 components from `CONTRACT.md` may be used:
`Heading`, `Body`, `Button`, `Card`, `Divider`, `List`, `PendingBanner`, `BlockedNotice`.

### TR-003 — Styling

All spacing, color, and typography MUST use the tokens in
`frontend/src/design/tokens.ts` and respect the closed contract.

## Traceability

| Requirement | Implements | Evidence |
|---|---|---|
| NFR-001 | `LandingPage.tsx` | Lighthouse report |
| NFR-002 | `LandingPage.tsx` | axe / WAVE check |
| NFR-003 | `RenderGuard` + tokens | `npm run type-check`, `npm run build` |
| NFR-004 | CSS media queries | Manual mobile check |
| NFR-005 | `verify-bundle.mjs` | `npm run postbuild` |
| TR-001 | `landing.page` envelope | `backend/models/ui_state_envelope.py` |
| TR-002 | `LandingPage.tsx` proposal | `RenderGuard` self-check |
| TR-003 | Tokens | `frontend/src/design/tokens.ts` |
