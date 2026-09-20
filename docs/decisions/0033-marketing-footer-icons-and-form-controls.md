# ADR 0033 — Social icons and radio controls on marketing surfaces

**Status:** Proposed (staging review — requires human approval before production)
**Date:** 2026-09-16
**Process:** v9.51
**Owner:** Product
**Related:** ADR-0030 (marketing-surfaces annex), ADR-0019 (contract adoption),
`.ai/intake/2026-09-16-p2-footer-social-icons.md`,
`.ai/intake/2026-09-16-p2-partner-form-redesign.md`,
`.ai/research/2026-09-16-footer-form-follow-ups.md`.

## Context

Two owner-requested elements on the public marketing surfaces fall
outside the V1 component inventory (`docs/library/CONTRACT.md`):

1. **Social media icons** (Instagram, TikTok, YouTube) in the shared fat
   footer. The V1 contract is text-first and prohibits icons without an
   ADR. Owner explicitly requested the real platform icons.
2. **Radio buttons** in the `/partners` inquiry form ("What best
   describes your organization?"). V1 `Field` covers input/textarea only.
   B2B form research (Trajectory, IvyForms/CXL, OrbitForms) shows radios
   are the correct control for 2–5 visible choices — all options visible
   at once, no dropdown disclosure, lower error rate — and the audience
   here is professionals, not learners.

ADR-0030 already established that buyer-facing marketing surfaces carry a
bounded exemption from learner-protection rules.

## Decision

On **marketing surfaces only** (`/`, `/caregiver`, `/for-communities`,
`/partners`, `/about`, `/help`, `/privacy`, `/terms`):

- Social brand icons are permitted in the footer social row when:
  - rendered as inline SVG (Simple Icons, CC0), `aria-hidden`,
  - accompanied by the visible platform label,
  - inside a ≥44px touch target with a visible focus ring,
  - colored `currentColor` on the token palette (surface on green).
- Radio-button groups are permitted in forms when:
  - wrapped in `<fieldset>` + `<legend>`,
  - each row is a ≥44px touch target,
  - the control is a native `<input type="radio">` (no custom widgets).

Neither control may appear on learner-facing curriculum, paywall, gift,
or account surfaces without a further ADR.

## Consequences

- Footer gains icon+label social links; screen readers announce
  "mynaani on Instagram" style names via `aria-label`.
- The partner form gains a visible-choice organization-type question.
- The closed component inventory is extended for marketing surfaces only;
  `RenderGuard` proposals on learner surfaces still reject these controls.
