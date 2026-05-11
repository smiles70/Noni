# Cognitively Protective Interface Design, Rendering, and Governance Contract

**Status:** Authoritative v1 (adopted by ADR 0019, Sprint 21).
**Scope:** All UI design, React rendering behavior, and AI-assisted UI reasoning within this system.
**Closed world:** Any interface, recommendation, or justification that cannot be fully expressed within this contract MUST be rejected.

This document is the authoritative source. Any conflict between this document and another document (including prior ADRs) is resolved in favor of this document. Modifications require a new ADR per Section VI.

---

## I. Design Vocabulary (Closed and Fully Specified)

### A. Color System (Low-Arousal, High-Predictability)

Permitted colors ONLY:

**Neutrals**
- Background: `#F4F4F2`
- Surface: `#FAFAF8`
- Primary text: `#222222`

**Accents (non-urgent)**
- Muted blue: `#4A6FA5`
- Desaturated green: `#5A7D6C`
- Muted amber: `#C9A24D`

**Restricted (functional use only)**
- Error / confirmation-required: `#B85C5C`
- Disabled: `#B0B0B0`

**Rules**
- No pure white or pure black.
- No saturated or neon colors.
- Color may never be the sole carrier of meaning.
- Maximum two accent colors visible at any time.

### B. Shapes, Geometry, and Grid

**Allowed shapes**
- Rectangles with rounded corners (8–12px radius).
- Circles ONLY for indicators (never containers).
- Straight horizontal or vertical dividers.

**Layout grid**
- Fixed spatial grid based on an 8px base unit.
- Permitted spacing values: `4 / 8 / 16 / 24 / 32 / 48` px.
- No arbitrary spacing values permitted.

**Rules**
- All elements must align to the grid.
- Element positions must remain stable across states and sessions.
- No reflow-driven rearrangement.
- No diagonal, organic, floating, overlapping, or parallax layouts.

### C. Typography (Cognitive Legibility)

**Permitted fonts only**
- Humanist sans-serif (e.g., Inter, Source Sans 3).
- System UI sans-serif fallback.

**Rules**
- Minimum base size: 16px.
- Line height: 1.5–1.7.
- No condensed, decorative, novelty, or script fonts.
- No all-caps except labels ≤2 words.

**Hierarchy**
- Maximum 3 text levels visible simultaneously.
- Headings ≤1.4× body text size.

### D. Standard Component Inventory (V1)

Only the following UI components may be rendered:

1. Heading
2. Body text
3. Button
4. Card
5. Field (input)
6. List
7. Divider
8. Indicator (non-interactive status)
9. ConfirmDialog
10. PendingBanner
11. BlockedNotice

**Rules**
- No additional components may be introduced without a formal ADR.
- Components may not be composed to simulate new component types.
- Each component must respect interaction-density and layout constraints.

### E. Iconography

**Default rule**
- Text-first interfaces only.
- Icons are disallowed in V1.

**Exception process**
- Icons may only be added via ADR.
- Icons may never carry meaning without adjacent text.
- Icons may not increase interaction density or visual salience.

### F. Interaction Density Limits

At any moment:
- ≤5 primary actionable elements.
- ≤1 irreversible action.
- ≤1 highlighted recommendation.

**Rules**
- Progressive disclosure required for all complexity.
- Advanced options hidden by default.
- Any irreversible action requires confirmation.

### G. Motion & Animation (Volatility Suppression)

**Permitted**
- Opacity fades (120–180ms).
- Position transitions ≤8px.
- Linear or ease-out timing only.

**Prohibited**
- Bounce, spring, elastic, or attention-drawing motion.
- Concurrent region animations.
- Motion that causes layout reflow.

---

## II. Accessibility & Focus Handling

**Focus indicator**
- Required for all interactive elements.
- 2px outline using muted blue (`#4A6FA5`).
- 2px offset to avoid layout shift.

**Rules**
- Focus indication may not rely on color alone.
- Focus handling must not introduce spatial movement.

---

## III. State Transparency & Failure Handling

The interface MUST:
- Explicitly label pending, gated, or blocked states.
- Preserve full visual context during errors.
- Require confirmation for state-changing actions.

**Language rules**
- No alarmist, urgent, or blame-oriented phrasing.
- Errors are presented as system states, not user failures.

**Standard confirmation phrasing pattern**

> "This will change [X]. You can continue or go back."

---

## IV. React Frontend Governance

**React's role**
- Deterministic renderer of backend-approved UI State Envelopes.
- Enforcement layer for all constraints in this contract.
- Telemetry emitter only (no interpretation).

**React MUST NOT**
- Infer readiness, mastery, confidence, or emotional state.
- Decide interface or curriculum progression.
- Modify layout, density, or pacing autonomously.

### A. UI State Envelopes

React may render ONLY backend-approved UI State Envelopes defining:
- Explicit state identifier.
- Authorized components (from V1 inventory).
- Interaction limits.
- Layout constraints.
- Transition permissions.

Undefined states MUST NOT render.

### B. React Render Guards (Mandatory, Fail-Closed)

All rendering MUST pass through Render Guards that:
- Enforce color, font, spacing, shape, and motion rules.
- Enforce interaction-density ceilings.
- Enforce spatial immutability.
- Block unauthorized components or transitions.
- Disable optimistic UI.
- Fail closed (non-render) on any violation.

Render Guards are authoritative and non-overrideable.

---

## V. AI UI Violation Self-Check (Required)

Before producing any UI output, the AI assistant MUST verify:

1. Only approved colors are used.
2. Only permitted shapes and spacing values are used.
3. Layout is grid-aligned and spatially stable.
4. Typography complies with all rules.
5. Only authorized components are used.
6. Interaction density limits are respected.
7. All irreversible actions are confirmation-gated.
8. No optimistic UI for progression is present.
9. Motion is minimal and non-urgent.
10. Cognitive load is preserved or reduced.

Failure of any check invalidates the output.

---

## VI. Decision Governance

Any expansion, exception, or modification to this contract requires:
- A discrete Architectural Decision Record (ADR) in `docs/decisions/`.
- Explicit justification from the approved reference library (see `README.md` in this directory).
- No retroactive interpretation.

---

## VII. Non-Negotiable Objective

Every interface state must prioritize **predictability, confidence preservation, spatial stability, cognitive load containment, dignity, and reversibility** over efficiency, expressiveness, speed, or novelty.

If an interface or recommendation cannot be fully expressed using ONLY this contract, it MUST NOT be produced.
