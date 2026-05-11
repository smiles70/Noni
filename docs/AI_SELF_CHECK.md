# AI UI Self-Check (Mandatory Pre-Flight)

**Authority:** `docs/library/CONTRACT.md` Section V, adopted by ADR 0019.
**Applies to:** Any AI assistant operating inside this repository on UI-affecting work.

Before producing any UI description, recommendation, render proposal, or
code change that touches a user-facing surface, the assistant MUST run
this ten-item check and assert compliance in the commit message.

If ANY check fails, the output is invalid and must be rejected — not
softened, not approximated, not partially shipped.

---

## The ten checks

1. **Colors.** Only values from `frontend/src/design/tokens.ts` `COLORS` are used. No raw hex literals elsewhere. No pure white, no pure black, no saturated/neon. Color is never the sole carrier of meaning. ≤2 accent colors visible at once.

2. **Shapes and spacing.** Only rectangles with 8–12px radius (`RADIUS` tokens). Circles only for indicators. Spacing values are drawn exclusively from `{4, 8, 16, 24, 32, 48}`.

3. **Grid alignment and spatial stability.** All elements align to the 8px grid. Element positions persist across states and sessions. No reflow-driven rearrangement, no diagonal/organic/floating/overlapping/parallax layouts.

4. **Typography.** Humanist sans-serif only (Inter, Source Sans 3, system fallback). Body ≥16px. Line height 1.5–1.7. No condensed, decorative, novelty, or script fonts. No all-caps except labels ≤2 words. ≤3 visible text levels. Headings ≤1.4× body.

5. **Authorized components.** Only the V1 inventory: `Heading`, `Body`, `Button`, `Card`, `Field`, `List`, `Divider`, `Indicator`, `ConfirmDialog`, `PendingBanner`, `BlockedNotice`. No new components without an ADR. No composition that simulates a new component type.

6. **Interaction density.** ≤5 primary actions, ≤1 irreversible action, ≤1 highlighted recommendation, at any moment. Progressive disclosure for all complexity. Advanced options hidden by default.

7. **Irreversible-action confirmation.** Every irreversible or state-changing action is confirmation-gated using the standard pattern: *"This will change [X]. You can continue or go back."*

8. **No optimistic UI for progression.** Curriculum or interface progression never advances on optimistic client state. Pending and gated states are explicitly labeled. State changes are observed, not predicted.

9. **Motion.** Opacity fades 120–180ms only. Position transitions ≤8px. Linear or ease-out timing only. No bounce, spring, elastic, or attention-drawing motion. No concurrent region animations. No reflow.

10. **Cognitive load.** The proposed change preserves or reduces cognitive load relative to the prior state. Any increase in interface novelty is justified by a corresponding increase in learner stability, cited from `docs/library/README.md`.

---

## Reference scope (closed)

Justifications must cite only sources listed in `docs/library/README.md`
(refs P1–P2, A1–A5, B1–B3, C1–C5, D1–D3, E1–E4). Citations to any other
source are prohibited and invalidate the output.

---

## Commit-message assertion

Any commit that touches frontend rendering, design tokens, envelope
schema, or copy must include the line:

```
Self-check: 10/10 (CONTRACT Section V)
```

If any check is N/A for a non-UI commit, state that explicitly:

```
Self-check: N/A (no UI surface affected)
```

A failed check is never "X/10" — it is a rejected proposal that must be
redesigned before commit.
