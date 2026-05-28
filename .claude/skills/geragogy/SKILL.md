---
name: geragogy
description: >
  Enforce the Cognitively Protective Interface Design, Rendering, and
  Governance Contract for Noni/mynaani — a SaaS product built for older
  adult learners (ages 55+). This skill prevents generic AI slop,
  high-arousal aesthetics, and cognitive overload. Every UI output
  MUST comply with the closed-world contract defined in
  docs/library/CONTRACT.md.

  Activate automatically for any frontend component, page, layout,
  styling, copy, or interaction design work in this repository.
license: Proprietary — adopted by ADR 0019, Sprint 21.
---

# Geragogy Design Skill — Noni / mynaani

## 0. Non-Negotiable Objective

Every interface state must prioritize **predictability, confidence
preservation, spatial stability, cognitive load containment, dignity,
and reversibility** over efficiency, expressiveness, speed, or novelty.

If an interface or recommendation cannot be fully expressed using ONLY
the rules in this skill, it MUST NOT be produced.

---

## 1. Audience & Context

**Primary users:** Adults aged 55+ learning AI for the first time.  
**Known characteristics:**
- Presbyopia (reduced near-vision acuity)
- High scam-awareness (look for legitimacy signals)
- Prefer self-directed pacing (Knowles andragogy)
- Resist condescension or infantilization
- Value calm, credible, transparent design over trendy or playful

**Tone:** Calm. Dignified. Reassuring. Never urgent, never playful, never
youth-oriented.

---

## 2. Closed Color System

### Permitted Colors ONLY

| Role | Hex | Token | Usage |
|------|-----|-------|-------|
| Background | `#F4F4F2` | `COLORS.background` | Page background |
| Surface | `#FAFAF8` | `COLORS.surface` | Cards, buttons, overlays |
| Primary text | `#222222` | `COLORS.textPrimary` | Headings, body, labels |
| Muted blue | `#4A6FA5` | `COLORS.accentMutedBlue` | Primary actions, focus, links |
| Desaturated green | `#4A6D5C` | `COLORS.accentDesatGreen` | Success, confirmations (Sprint 28) |
| Muted amber | `#C9A24D` | `COLORS.accentMutedAmber` | Decorative indicators ONLY |
| Error / confirm | `#A84C4C` | `COLORS.errorConfirm` | Errors, irreversible actions |
| Disabled | `#B0B0B0` | `COLORS.disabled` | Disabled states, muted text |

### Prohibited
- Pure white (`#FFFFFF`) or pure black (`#000000`)
- Saturated red, neon, high-chroma colors
- Gradients (unless explicitly ADR-approved)
- More than TWO accent colors visible simultaneously
- Color as the sole carrier of meaning

### Enforcement Rule
Before producing ANY UI element, verify its color is in the table above.
If it is not, propose a token change via ADR — do not use the color.

---

## 3. Typography

### Rules
- **Minimum base size:** 16px (`TYPOGRAPHY.bodySizePx`)
- **Line height:** 1.5–1.7 (`TYPOGRAPHY.bodyLineHeight = 1.6`)
- **Permitted fonts:** Inter, Source Sans 3, system-ui (humanist sans-serif)
- **NO condensed, decorative, novelty, or script fonts**
- **NO all-caps** except labels ≤2 words (and prefer sentence case even then)
- **Maximum 3 text levels visible simultaneously**
- **Headings ≤1.4× body text size** (ceiling, not target)

### Token Reference
```
TYPOGRAPHY.headingScale.level1 = 22px   (~1.375× body)
TYPOGRAPHY.headingScale.level2 = 19px   (~1.1875× body)
TYPOGRAPHY.headingScale.level3 = 17px   (~1.0625× body)
TYPOGRAPHY.bodySizePx = 16px
TYPOGRAPHY.bodyLineHeight = 1.6
TYPOGRAPHY.fontFamily = Inter, "Source Sans 3", system-ui, sans-serif
```

### Heading Ratio Guidance
The 1.4× ceiling was written for **dense pages** (curriculum lessons
with multiple competing text levels). On sparse pages like the landing
page, a larger heading is acceptable IF it is the sole dominant text
element and does not compete with other headings. An ADR is required for
any heading >1.4× body.

### Copy Tone Rules
- **NO exclamation marks** in headings or CTAs (signals urgency/arousal)
- **NO imperative commands** to the user ("Learn!" "Start!") — use
  descriptive or outcome-oriented phrasing
- **NO social pressure** ("Join a vibrant community," "Don't miss out")
- **NO condescension** ("So easy even grandma can do it")
- **NO blame-oriented error messages** — errors are system states, not
  user failures
- Standard confirmation: "This will change [X]. You can continue or go back."

---

## 4. Layout & Spacing

### Grid
- **8px base unit**
- Permitted values: 4, 8, 16, 24, 32, 48 px
- No arbitrary spacing values

### Token Reference
```
SPACING.xs  = 4
SPACING.sm  = 8
SPACING.md  = 16
SPACING.lg  = 24
SPACING.xl  = 32
SPACING.xxl = 48
GRID_BASE_PX = 8
```

### Shapes
- **Rectangles with rounded corners only:** 8–12px radius
- **Circles ONLY for indicators** (never containers)
- **Straight horizontal or vertical dividers only**
- No diagonal, organic, floating, overlapping, or parallax layouts

### Token Reference
```
RADIUS.sm = 8
RADIUS.md = 10
RADIUS.lg = 12
```

### Spatial Stability Rules
- Element positions must remain stable across states and sessions
- No reflow-driven rearrangement on auth state change
- No layout shift from loading → loaded states

---

## 5. Component Inventory (Closed World)

Only these UI components may be rendered. No others without ADR.

| # | Component | Notes |
|---|-----------|-------|
| 1 | Heading | h1–h3 only. Max 3 visible levels. |
| 2 | Body text | p, span, label. Min 16px. |
| 3 | Button | Primary or secondary. Max 5 per view. |
| 4 | Card | Container with surface color, radius ≤12px. |
| 5 | Field | Input, textarea. Min 16px text. |
| 6 | List | ul, ol. No custom bullet styling outside tokens. |
| 7 | Divider | Straight horizontal line only. |
| 8 | Indicator | Non-interactive status (loading dot, progress). |
| 9 | ConfirmDialog | Must use standard confirmation phrasing. |
| 10 | PendingBanner | Loading state. No motion except opacity fade. |
| 11 | BlockedNotice | Error state. Calm, non-alarmist language. |

### Prohibited (Require ADR)
- Icons (text-first interfaces)
- Dropdown menus
- Accordions
- Tabs
- Tooltips
- Carousels
- Modals beyond ConfirmDialog
- Toast notifications
- Skeleton screens (use PendingBanner)
- Progress bars with motion

---

## 6. Interaction Density Limits

At ANY moment, the visible UI must satisfy:
- **≤5 primary actionable elements**
- **≤1 irreversible action**
- **≤1 highlighted recommendation**

### Rules
- Progressive disclosure required for all complexity
- Advanced options hidden by default
- Any irreversible action requires confirmation dialog
- No multi-step wizards without explicit step indicators

---

## 7. Motion & Animation

### Permitted
- **Opacity fades only:** 120–180ms (`MOTION.fadeMinMs` to `MOTION.fadeMaxMs`)
- **Position transitions ≤8px**
- **Linear or ease-out timing only**

### Prohibited
- Bounce, spring, elastic
- Concurrent region animations
- Motion that causes layout reflow
- Color transitions (background-color, color)
- Scale transforms
- Rotation
- Blur or filter transitions

### Token Reference
```
MOTION.fadeMinMs = 120
MOTION.fadeMaxMs = 180
MOTION.defaultFadeMs = 150
MOTION.maxPositionShiftPx = 8
MOTION.allowedEasings = ["linear", "ease-out"]
```

### Reduced Motion
Respect `prefers-reduced-motion: reduce`. All motion must be disableable.

---

## 8. Iconography

**Default rule: TEXT-FIRST interfaces only. Icons are disallowed in V1.**

Exception process (requires ADR):
- Icon may only be added if accompanied by adjacent text label
- Icon may not increase interaction density or visual salience
- No emoji as icon substitutes

---

## 9. Accessibility & Focus

- **Focus indicator:** 2px outline using muted blue (`#4A6FA5`), 2px offset
- Focus indication may not rely on color alone
- Focus handling must not introduce spatial movement
- All interactive elements must have visible focus states
- Skip-to-content link required on all pages

---

## 10. State Transparency & Failure Handling

- Explicitly label pending, gated, or blocked states
- Preserve full visual context during errors
- Require confirmation for state-changing actions
- Errors presented as system states, not user failures

---

## 11. React Governance

### React's Role
- Deterministic renderer of backend-approved UI State Envelopes
- Enforcement layer for all constraints in this skill
- Telemetry emitter only (no interpretation)

### React MUST NOT
- Infer readiness, mastery, confidence, or emotional state
- Decide interface or curriculum progression
- Modify layout, density, or pacing autonomously
- Use optimistic UI for progression
- Track mouse movements, hover time, or scroll depth for "engagement scoring"

### Render Guards (Mandatory, Fail-Closed)
All rendering MUST pass through Render Guards that:
- Enforce color, font, spacing, shape, and motion rules
- Enforce interaction-density ceilings
- Enforce spatial immutability
- Block unauthorized components or transitions
- Disable optimistic UI
- **Fail closed (non-render) on any violation**

---

## 12. AI Self-Check (Required Before Every UI Output)

Before producing ANY UI output, verify:

1. **Colors:** Only approved colors used.
2. **Shapes/Spacing:** Only permitted shapes and spacing values used.
3. **Layout:** Grid-aligned and spatially stable.
4. **Typography:** Complies with all rules (size, line height, weight, hierarchy).
5. **Components:** Only authorized components from V1 inventory.
6. **Density:** Interaction density limits respected.
7. **Irreversible actions:** All confirmed.
8. **Optimistic UI:** None present.
9. **Motion:** Minimal and non-urgent.
10. **Cognitive load:** Preserved or reduced.
11. **Copy tone:** Calm, dignified, no exclamation marks, no imperative commands.

**Failure of ANY check invalidates the output. Do not proceed. Propose an
ADR or request clarification.**

---

## 13. Code Patterns (Project-Specific)

### Import Tokens
All UI code MUST import from the token file:
```typescript
import { COLORS, SPACING, TYPOGRAPHY, RADIUS, MOTION, FOCUS } from "../design/tokens";
```

### No Raw Hex Literals
Never write `#4A6FA5` inline. Always use `COLORS.accentMutedBlue`.

### No Arbitrary Spacing
Never write `margin: 20px` or `padding: 12px`. Use `SPACING.md` (16)
or `SPACING.lg` (24).

### RenderGuard Usage
All page-level components must wrap their render tree:
```tsx
<RenderGuard envelope={envelope} proposal={proposal}>
  {/* UI tree */}
</RenderGuard>
```

The `proposal` must accurately declare:
- `components` (from V1 inventory)
- `primaryActionCount` (≤5)
- `irreversibleActionCount` (≤1)
- `highlightedRecommendationCount` (≤1)
- `visibleTextLevels` (≤3)
- `colorsUsed` (subset of permitted colors)
- `motionDurationsMs` (within 120–180ms)

### Fire-and-Forget Patterns
Backend analytics, telemetry, and logging MUST NOT block the user request:
```python
asyncio.create_task(log_event(...))  # never await
try/except around all analytics calls
```

---

## 14. What "Generic AI Slop" Looks Like (Recognize and Reject)

| AI Slop Pattern | Why It Violates Geragogy | Correct Alternative |
|-----------------|-------------------------|---------------------|
| Purple gradient on white background | Saturated, high-arousal, not in palette | Solid muted blue on surface |
| Inter font everywhere + emojis | Generic, icons disallowed | Inter or Source Sans 3, text-only |
| Bouncy loading animation | Spring motion prohibited | Opacity fade 150ms |
| "Join 10,000 happy learners!" | Social pressure, exclamation | "Free. No card needed. Stop any time." |
| Skeleton screen shimmer | Concurrent animation, non-inventory component | PendingBanner with opacity fade |
| Dark mode default | Older adults prefer light mode | Light mode (`#F4F4F2` background) |
| Sticky bottom CTA bar | Increases density, spatial instability | Static, predictable layout |
| Carousel testimonials | Motion + density + non-inventory component | Single, calm credibility line |
| Tooltip on hover | Non-inventory component, motion | Adjacent body text explanation |
| "Easy" / "Simple" / "Just" in copy | Condescending, diminishes capability | Descriptive, respectful phrasing |

---

## 15. Decision Governance

Any expansion, exception, or modification to this skill requires:
- A discrete ADR in `docs/decisions/`
- Explicit justification from the approved reference library
- No retroactive interpretation

**The contract is a closed world. If you cannot express it within these
rules, it MUST NOT be produced.**

---

*Skill version: 1.0.0  
Authority: docs/library/CONTRACT.md (ADR 0019, Sprint 21)  
Scope: All UI design, React rendering, and AI-assisted UI reasoning in
the Noni / mynaani system.*
