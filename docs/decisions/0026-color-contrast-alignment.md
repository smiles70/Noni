# 0026 — Color Contrast Alignment: Reconciling CONTRACT Palette with WCAG 2.1 AA and Geragogy Research

## Status

Accepted (Sprint 28, 2026-05-26).

## Context

ADR 0007 (Accessibility approach, 2026-05-18) adopted **WCAG 2.1 Level AA** as the minimum bar, with `axe-playwright` gating the E2E suite. The closed-world design contract (CONTRACT.md, ADR 0019) defines the sole permitted color palette.

During Sprint 28's UI/UX & Accessibility audit, three colors in the contract palette were found to fail WCAG 2.1 AA when used as text on the contract's background (`#F4F4F2`):

| Color | Hex | Contrast vs `#F4F4F2` | WCAG AA at 16px? |
|---|---|---|---|
| accentDesatGreen | `#5A7D6C` | 4.0:1 | **FAIL** (needs 4.5:1) |
| errorConfirm | `#B85C5C` | 3.9:1 | **FAIL** (needs 4.5:1) |
| accentMutedAmber | `#C9A24D` | 2.4:1 | **FAIL** (needs 4.5:1) |

This tension is **not** a conflict between WCAG and geragogy. The geragogy research library (Dimension 3, Language & Legibility; sources C1, C5, Formosa & Fragoso) **explicitly demands high contrast** for older adult learners. Perceptual aging reduces contrast sensitivity; low-contrast text increases cognitive load (Sweller et al., D1) and undermines self-efficacy (AARP/OATS, C5).

The question is therefore: **how do we satisfy both geragogy and WCAG without breaking the contract's closed-world discipline?**

## Decision

### 1. Darken two near-miss colors

| Token | Old | New | Contrast vs `#F4F4F2` | Change |
|---|---|---|---|---|
| `accentDesatGreen` | `#5A7D6C` | `#4A6D5C` | ~4.6:1 | Darken 16% |
| `errorConfirm` | `#B85C5C` | `#A84C4C` | ~4.5:1 | Darken 10% |

Both remain within the contract's design intent (muted, non-urgent green; restricted functional red). The shift is small enough that no component re-design is required.

### 2. Restrict `accentMutedAmber` to non-text decorative use

The amber's 2.4:1 ratio is too far from the threshold to darken without changing its semantic identity (it would become brown, not amber). The contract already prohibits color as the sole carrier of meaning (Section I.A, Rule 3) and disallows icons in V1 (Section I.E). Therefore:

- `accentMutedAmber` may only appear as:
  - Border tint on selected/checked states
  - Background tint behind dark text (not as foreground text itself)
  - Non-text indicator shapes (lock icon replacement uses adjacent text per Section I.E)

- It **must never** appear as text on `background` or `surface`.

### 3. Update the authoritative documents in this order

1. `frontend/src/design/tokens.ts` — source of truth for runtime
2. `docs/library/CONTRACT.md` — the binding palette specification
3. `docs/decisions/0026-color-contrast-alignment.md` — this ADR

No component files require changes because all colors are imported from `tokens.ts`.

## Consequences

- axe-playwright E2E contrast checks will now pass for all text rendered with `accentDesatGreen` or `errorConfirm`.
- The palette remains closed-world; no new colors were introduced.
- The geragogy quality rubric (Dimension 3) now scores higher for perceptual legibility.
- Any future color additions must include a contrast audit against `#F4F4F2` at 16px before acceptance.
- `accentMutedAmber` restrictions are enforced by code review, not by automated test (it is not used as text today; any future usage must include an explicit contract justification).

## References

- **ADR 0007** — Accessibility approach: WCAG 2.1 AA via axe + visible focus + larger-text mode
- **ADR 0019** — Closed-world design contract (governs all color, spacing, typography)
- **CONTRACT.md** Section I.A — Color System (updated by this ADR)
- **Geragogy Quality Standards Rubric** Dimension 3 — Language, Legibility & Cognitive Legibility
- **C1** — Fisk et al. (2009): perceptual aging and contrast sensitivity
- **C5** — AARP & OATS (2021): age-inclusive design calls for higher contrast
- **Formosa & Fragoso (2025)** — perceptual changes as a quality variable, not an afterthought
