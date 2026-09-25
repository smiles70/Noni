# Intake — landing hero: match approved full-bleed mock

- Priority: P2 — visual fidelity on the public landing page
- Date: 2026-09-17
- Persona: learner (B2C) — `/` landing; B2B entries stay top-right
- Branch: `landing-page-update`
- Target: user-approved screenshot (Gemini mockup, `mynaani.com` frame)
  + static mock at `/tmp/mynaani-landing-page/`

## Problem statement

The rendered landing page does not match the approved design. In the
approved design the hero photograph runs **edge-to-edge behind the whole
viewport** — the logo plate, the two B2B buttons, the hero copy, and the
legal strip all float **on** the photo. The current static mock instead
renders a **solid white navbar bar** across the top and a **solid white
footer bar** across the bottom, cropping the photo to the middle band.

## Pixel-by-pixel delta (target vs current mock)

| Element | Target | Current mock |
| --- | --- | --- |
| Photo coverage | Full viewport, behind header + footer | Middle band only (`flex: 1` between white bars) |
| Header background | Transparent — elements float on photo | Solid `#ffffff` bar |
| Logo | White rounded plate (~110px) hugging the stacked lockup, top-left on photo | Bare logo + text spans on white bar |
| B2B buttons | Two green pills floating top-right on photo | Same pills but on white bar |
| Hero copy | Left-aligned, vertically centred, on gradient wash | Same — correct already |
| CTA | Green pill ~200px, `How it works` | Same — correct already |
| Footer | Thin translucent strip on photo, small muted text | Solid `#ffffff` bar, taller |
| Hero image | `hero-mynaani.jpg` — mirror reflection is part of the photo | Same asset — correct already |

## Scope

1. Make the hero section a full-viewport fixed layer (`inset: 0`) so the
   photo covers edge-to-edge.
2. Header becomes a transparent overlay (`position: absolute`, no
   background); logo gets its own white rounded plate; B2B pills float
   unchanged.
3. Footer becomes a thin translucent strip (`rgba(255,255,255,~0.85)`)
   pinned to the bottom of the viewport over the photo.
4. Drop the `.logo-text` spans — `mynaani-logo.webp` already contains the
   wordmark + tagline; keeping the spans duplicates the brand name.
5. Keep the left-to-right legibility wash and the near-solid mobile wash.
6. Mirror the same structure in `LandingPage.tsx` (already done on this
   branch — floating card removed, copy left-aligned on a wash, compact
   logo plate, translucent `LandingFooter`).

## Edge cases

- Mobile (<600px): near-solid wash keeps text legible; header/footer
  overlay must not collide with the stacked B2B pills.
- Contrast: footer text needs ≥4.5:1 over the photo — translucent white
  strip preserves this.
- The logo plate must stay opaque enough to read over busy photo areas.
- No new colours — reuse the approved palette (`#3b5d4f` CTA green maps
  to `COLORS.accentDesatGreen` in the React implementation).

## Acceptance

- Static copy at `localhost:8080` matches the approved screenshot:
  photo edge-to-edge, floating header, translucent footer.
- `LandingPage.tsx` renders the same structure (verified once the
  backend can boot — Postgres not installed locally).
- No layout regression on mobile widths.
