# Gap Analysis — Mynaani Landing Page vs. Older-Adult Best Practice

**Process:** v9.51
**Date:** 2026-08-27
**Scope:** Compare the live Mynaani landing page against the competitive
research and rubric from `LANDING_HERO_COMPETITIVE_RESEARCH.md` and
`LANDING_HERO_RUBRIC.md`.

## Current state

- Live URL: `https://noni-web.pages.dev/`
- Source: `frontend/src/components/LandingPage.tsx`
- Contract: `docs/library/CONTRACT.md`
- Envelope: `landing.page` in `backend/models/ui_state_envelope.py`

## Summary gap table

| # | Dimension | Current state | Best practice (research) | Gap | Severity |
|---|---|---|---|---|---|
| 1 | Hero headline size | 22 px (`headingScale.level1`) | 24–48 px hero headlines common; AARP heuristic says 18–24 pt | Headline is smaller than nearly every competitor | Medium-High |
| 2 | Hero image quality / relatability | Uses existing `/nonisplash.jpg` | Sites like AARP, Senior Planet, AARP Life Reimagined use warm, real photos of older adults | Image may be generic or not obviously older-adult | Medium |
| 3 | CTA visual dominance | Uses `accentMutedBlue` on `surface`; single primary and secondary | Many sites use full-width or larger high-contrast primary CTA | CTA is present but not visually dominant | Medium |
| 4 | Benefit cards above fold | No benefit cards in hero; supporting sections below the fold | AARP, Arlow, Ask Grace use 2–4 benefit cards near headline | Value proposition requires scrolling to see | Medium |
| 5 | Trust signals | Footer note "Patent-pending curriculum..." removed in HERO-001; no explicit trust badge | Gov/health sites and AARP show trust / membership / safety up front | Trust is conveyed only through copy, not visual signals | Low-Medium |
| 6 | Headline / subheadline contrast | H1 (22 px) vs body (16 px) = 1.375× | AARP heuristic: headings "noticeably larger" than body | Passes but is at the low end of the range | Low |
| 7 | One primary CTA | Yes: "Begin calmly" | Yes: one primary CTA | No gap | None |
| 8 | Plain language | Backend copy is plain and calm | All successful senior sites use plain language | No gap | None |
| 9 | No urgency / fear | No urgency language | No urgency in best practice | No gap | None |
| 10 | Mobile single column | Flex-wrap two-column that stacks; may reflow | AARP / Medicare use deterministic single-column on mobile | Layout may reflow at narrow widths | Low |
| 11 | Contract compliance | Fully token-driven; passes RenderGuard | Mynaani-specific; not applicable to competitors | Strong | None (strength) |

## Root cause of the headline / dominance gap

The Mynaani contract (`CONTRACT.md` Section I.C) sets:

> "Headings ≤1.4× body text size."

With a 16 px body, the largest legal H1 is **22.4 px**. This is at the
bottom of the AARP heuristic range (18–24 pt, where pt ≈ px in web) and
far below the 24–48 px hero headlines used by AARP, Senior Planet, Ask
Grace, Arlow, and the MetLife reference image.

## Root cause of the benefit-card gap

The `landing.page` envelope permits `Card` and `List`, but the current
`RenderProposal` does not include a benefit-card section. The `what_noni_does`
and `how_it_feels` lists are rendered below the fold, not in the hero.

## Root cause of the trust-signal gap

HERO-001 removed the "Patent-pending curriculum..." footer text. No new
trust signal (e.g., "free modules," "no payment info required," "nonprofit
mission") was added to the hero card.

## Recommended resolutions

### Option A — Keep contract, tighten within bounds

- Increase heading to the maximum 22.4 px (already 22 px).
- Add a small benefit list **inside** the CTA card using `List` component.
- Add a trust note to the primary CTA (e.g., "Free. No card required.").
- Select a more relatable hero image.

### Option B — Contract exemption for the landing page

- Draft `ADR 0029` to allow the landing page headings up to 32 px and a
  hero card with a subtle overlap or larger border-radius, while keeping
  the rest of the application under `CONTRACT.md`.
- This requires an explicit justification and a new ADR per `CONTRACT.md`
  Section VI.

### Option C — Hybrid

- Leave the current landing page as the **calm, contract-compliant** version.
- Create a separate `landing.promotional` state for a high-impact campaign
  page that can exceed contract limits under its own ADR.

## Risks of each option

| Option | Risk |
|---|---|
| A | May still look too quiet vs. competitors; small margins of improvement |
| B | Dilutes the closed-world contract; sets a precedent for exemptions |
| C | Requires maintaining two landing surfaces and extra state management |

## Recommendation

Proceed with **Option A** first. It closes the headline, CTA, and trust gaps
without amending the contract. If user testing or analytics shows the page
still underperforms, escalate to **Option B** with `ADR 0029`.
