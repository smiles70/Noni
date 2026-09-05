# Intake: brand plate behind hero logo for legibility (55+ legitimacy signal)

**Date:** 2026-09-05
**ID:** BRAND-LOGO-002
**Status:** RESEARCHED — externally grounded, implementation-ready
**Skills applied:** geragogy (contract), knowledge-graph-extraction conventions
**Supersedes/extends:** BRAND-LOGO-001 (placement research unchanged; this
addresses the rendered-hero findings F1–F3 recorded in that intake).

## Requirement

Add a calm, surface-backed "brand plate" behind the hero logo so the mark is
legible against the dark photo region and reads as an identity/legitimacy
signal rather than ambient decoration.

## Evidence base (carried from BRAND-LOGO-002 rendered review)

| # | Finding | Severity |
|---|---|---|
| F1 | Muted green/blue mark over the photo's dark curtain region: wordmark + tagline borderline-illegible for presbyopic users; a faint mark undermines the legitimacy signal scam-aware 55+ users look for. | High for this audience |
| F2 | Mark reads as decoration, not identification; NN/g's 89% recall benefit presumes the logo is *seen*. | Medium |
| F3 | Published practice for logos over imagery: scrim or surface-backed plate — the action card already uses `rgba(250,250,248,0.5)`; the plate reuses that treatment family. | Medium |

## External research — logos over imagery

- **NN/g (Whitenton, 2016):** the top-left recall benefit requires the logo
  to be perceptible; contrast against the background is a precondition, not
  a styling nicety.
- **WCAG non-text contrast / target practice:** brand marks over photography
  are routinely separated by a scrim or plate so identity survives arbitrary
  image content (Apple, Shopify, and Google landing pages all use a
  surface-backed or scrim-backed mark over hero imagery).
- **Geragogy grounding:** for a scam-aware 55+ audience, a clearly visible,
  stable brand mark is a *legitimacy signal* (trust cue), not decoration.

## Design decision (architecture)

- **Plate:** `backgroundColor: rgba(250,250,248,0.85)` — `COLORS.surface`
  (#FAFAF8) at 85% opacity, matching the floating action card's treatment
  family (`rgba(250,250,248,0.5)`, slightly stronger since the mark must
  carry identity, not just content).
- **Shape:** `RADIUS.lg` (12px) rounded rectangle — permitted shape.
- **Padding:** `SPACING.sm` (8px) internal clear space around the mark.
- **Position:** unchanged landmark — `absolute; top: SPACING.xl; left:
  SPACING.xl` desktop / `SPACING.lg` mobile. `zIndex: 1` (above photo,
  below card) — unchanged.
- **Logo size:** raised to 128px desktop (16×8) / 96px mobile (12×8) —
  on-grid, still within the stacked-mark ≤160px hero guidance.
- **Non-interactive:** plate adds +0 actionable elements; the logo itself
  remains an `img`, not a link.
- **No motion, no new tokens, no new colors** — all values map to existing
  tokens or the already-in-use surface-rgba family.
- `data-contract-exemption="landing.hero"` retained on the plate wrapper
  and the img for audit continuity with ADR-0029.

## Geragogy contract review (12-point pre-check)

| # | Check | Verdict |
|---|---|---|
| 1 | Colors | `COLORS.surface` family only (rgba of #FAFAF8) — no new color |
| 2 | Shapes/spacing | RADIUS.lg, SPACING.sm/lg/xl, 8px-grid heights (128/96) |
| 3 | Layout | Absolute in fixed hero; no reflow; spatially stable |
| 4 | Typography | No text added |
| 5 | Components | `img` + neutral container; outside V1 inventory → exemption markers per ADR-0029 |
| 6 | Density | +0 actionable elements |
| 7 | Irreversible | None |
| 8 | Optimistic UI | None |
| 9 | Motion | None |
| 10 | Cognitive load | Reduced: mark is now a legible landmark |
| 11 | Copy tone | `alt="mynaani"` unchanged |
| 12 | Research | NN/g perceptibility precondition; scrim/plate convention over imagery |

## Epic / Block / Rack plan

| Level | ID | Item | Acceptance |
|---|---|---|---|
| Epic | EPI-BRAND-002 | Legible brand identity on hero | Logo legible over photo on surface plate |
| Block | BLK-001 | Plate integration | Tokenized plate style, exemption marker |
| Rack | RCK-001 | `LandingPage.tsx` plate wrapper | Absolute top-left, surface 85%, RADIUS.lg, SPACING.sm pad |
| Rack | RCK-002 | Size bump | 128px desktop / 96px mobile, on-grid |
| Block | BLK-002 | Verification | QA×2 + UAT×2 + staging + scored PR |
| Rack | RCK-003 | Test update | Brand test asserts plate + non-interactivity |
| Rack | RCK-004 | Virtual QA | tsc, lint, unit tests, build |
| Rack | RCK-005 | Virtual UAT | 12-point geragogy self-check |
| Rack | RCK-006 | PR score ≥5/5 | Rubric per BRAND-LOGO-001 precedent |

## Risks

- Plate could read as a "card" competing with the action card — mitigated by
  small size, no shadow, and corner placement (landmark zone, not content
  zone).
- 85% opacity still lets photo texture faintly through — accepted: full
  opacity would look pasted-on; 85% keeps it calm while restoring legibility.

---

## Virtual QA round 1 — PASSED (2026-09-05)

- `npm run type-check` ✅ clean
- `npm run lint` ✅ 0 warnings
- `vitest run` ✅ 14 files / 122 tests (15 expected-fail contract tests) —
  includes the new BRAND-LOGO-002 plate test (2/2 brand tests pass)
- `npm run build` ✅ + postbuild bundle verification ✅ (no localhost refs,
  production API URL verified)

## Virtual UAT round 1 — PASSED (12-point geragogy self-check)

| # | Check | Result |
|---|---|---|
| 1 | Colors | ✅ `rgba(250,250,248,0.85)` = COLORS.surface family, already in use by the action card at 0.5; no new color |
| 2 | Shapes/spacing | ✅ RADIUS.lg, SPACING.sm padding, top/left on xl/lg; heights 128/96px on the 8px grid |
| 3 | Layout | ✅ absolute inside fixed hero; z1 above photo, below card; no reflow |
| 4 | Typography | ✅ no text added |
| 5 | Components | ✅ `img` + neutral `div` outside V1 inventory → `data-contract-exemption="landing.hero"` on both, plus `data-brand-plate` audit marker |
| 6 | Density | ✅ +0 actionable elements |
| 7 | Irreversible | ✅ none |
| 8 | Optimistic UI | ✅ none |
| 9 | Motion | ✅ none added |
| 10 | Cognitive load | ✅ reduced — mark now legible landmark/legitimacy signal |
| 11 | Copy tone | ✅ `alt="mynaani"` unchanged |
| 12 | Research | ✅ plate/scrim-over-imagery convention; NN/g perceptibility precondition |

## Staging round — PASSED (2026-09-05)

- `feat/brand-plate` → `staging`; Deploy Staging run **33991890712**:
  preflight ✅, railway-deploy-backend ✅, cloudflare-pages-deploy ✅
  (incl. G3 bundle guard) — conclusion `success`.
- Live-bundle verification: deployed `index-q7LUwbRp.js` on
  `staging.noni-web.pages.dev` contains `data-brand-plate`,
  `rgba(250, 250, 248, 0.85)`, and `mynaani-logo.webp` — plate shipped.

## Virtual QA + UAT round 2 — PASSED

- Pre-push hook re-ran type-check + full unit suite on the exact pushed
  tree ✅ (14 files / 122 tests, 15 xfail).
- 12-point geragogy self-check re-run post-staging: unchanged, all pass.
- Interaction density, motion, palette, and component inventory all
  unchanged from the merged baseline; the only visual delta is the plate
  and the on-grid size bump (128/96px).
