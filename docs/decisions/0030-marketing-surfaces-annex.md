# ADR 0030 — Marketing Surfaces Annex to the Interface Contract

**Status:** Proposed (staging review — requires human approval before production)
**Date:** 2026-09-05
**Process:** v9.51
**Owner:** Product
**Related:** ADR-0019 (contract adoption), ADR-0029 (landing-hero exemption),
`.ai/intake/2026-09-05-b2b-landing-research-001.md` (B2B-LANDING-001,
B2B-DESIGN-001).

## Context

Mynaani serves two audiences with different needs:

- **Learners (B2C):** adults 55+ learning AI. The geragogy contract
  (`docs/library/CONTRACT.md`) exists to protect *them* — low arousal,
  bounded density, closed palette, minimal components.
- **Buyers (B2B):** senior living communities, health plans, and similar
  institutions. Research (NN/g B2B-vs-B2C; enterprise-trust studies;
  Candoo Tech, GetSetUp, Papa) shows these are professionals evaluating
  vendor maturity on marketing surfaces. Applying learner-protection rules
  verbatim to buyer-facing pages produces a threadbare page that fails the
  legitimacy check before a conversation starts.

`CONTRACT.md` claims authority over all UI "within this system," but
ADR-0029 already established that marketing surfaces may receive scoped
exemptions via ADR.

## Decision

Split UI governance into two explicit layers:

| Layer | Scope | Ruleset |
|---|---|---|
| **Product surfaces** | Curriculum, learner UI, account, lessons, billing flows | Full `CONTRACT.md` — unchanged |
| **Marketing surfaces** | Landing page, `/for-communities`, future public pages | This annex |

### Marketing surfaces MAY use (beyond the base contract)

- A wider heading scale (display sizes up to ~40px, still humanist sans).
- Photography and brand imagery.
- Stat/outcome blocks and partner/logo strips **only with real data** —
  no invented numbers, no fake logos.
- Simple icons **only when adjacent to a text label** (never
  icon-only meaning; no emoji substitutes).
- A standard marketing header/footer with text navigation links.
- Audience-selector cards and multi-column footer layouts.
- Brand-colored buttons; both primary (desat green) and secondary
  (muted blue) actions.

### Marketing surfaces MUST still obey

- Calm, dignified tone — no urgency, no exclamation-mark CTAs, no
  imperative commands, no dark patterns.
- WCAG 2.2 AA contrast and keyboard/screen-reader access.
- `prefers-reduced-motion` respected; no autoplay motion.
- Design tokens (`COLORS`, `SPACING`, `RADIUS`, `TYPOGRAPHY`) remain the
  vocabulary — richer usage, not a different palette.
- Truthfulness: claims must be verifiable; "founding partners" framing is
  used instead of fabricated proof.
- Exempt elements carry `data-contract-exemption="marketing.<surface>"`
  for audit.

### Explicitly out of scope

- No change to any product/learner surface.
- No change to `landing.page` or other UI State Envelopes — marketing
  pages serve static content and are not behind RenderGuard envelopes;
  they are governed by this annex + audit markers + review.

## Consequences

### Positive

- B2B surfaces can meet professional buyer expectations without weakening
  learner protection.
- The exemption boundary is explicit, auditable, and reversible.
- Matches the industry norm (competitors run richer marketing sites than
  product UIs).

### Negative

- Two rulesets to maintain; reviewers must know which applies.
- Marketing surfaces lose RenderGuard's fail-closed enforcement — they
  rely on code review + tests instead.

## Conditions

1. Applies only to routes/pages explicitly designated marketing surfaces.
2. Each marketing page carries the `data-contract-exemption` marker.
3. Accessibility checks (axe/Lighthouse AA) must still pass.
4. Any future relaxation requires its own ADR.
