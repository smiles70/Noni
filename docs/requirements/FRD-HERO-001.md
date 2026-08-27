# Functional Requirements Document — HERO-001

**Process:** v9.51
**ID:** FRD-HERO-001
**Date:** 2026-08-27
**Owner:** Engineering
**Source:** `BRD-HERO-001`

## Functional requirements

### FR-001 — Hero layout

The landing page MUST display a two-column hero layout on desktop and a
single stacked column on mobile. The left side MUST contain the Noni logo,
a single H1, and a one-sentence body. The right side MUST contain a card
with the primary CTA and no more than three secondary actions.

**Acceptance criteria:**
- Layout does not exceed `landing.page` `max_visible_text_levels=3`.
- Total primary actions ≤ 5.
- No reflow-driven rearrangement.

### FR-002 — Brand and content

All visible text and imagery on the landing page MUST be Noni-branded.
No MetLife, legal-plan, or third-party references may appear in the
rendered DOM or in the production bundle.

**Acceptance criteria:**
- `grep -i "metlife" dist/assets/*` returns no matches.
- Hero image filename and alt text are Noni-specific.

### FR-003 — Primary call to action

The primary CTA MUST be "Begin learning" and MUST route the user to the
free curriculum path (signed-out users to `account.signin`, signed-in users
to `curriculum.menu`).

**Acceptance criteria:**
- Button is the highest-contrast action in the card.
- Action is a permitted transition in `landing.page`.

### FR-004 — Secondary actions

The landing page MAY include up to two secondary actions such as
"How it works" and "Sign in". These MUST remain within the
`landing.page` `max_primary_actions` limit.

**Acceptance criteria:**
- Secondary actions are styled as non-primary buttons.
- Total actions visible at once ≤ 5.

### FR-005 — Contract compliance

The redesigned `LandingPage.tsx` proposal MUST pass the `RenderGuard`
self-checks for the `landing.page` envelope.

**Acceptance criteria:**
- `npm run type-check` passes.
- `npm run build` passes.
- No contract color, spacing, typography, or motion violations.
