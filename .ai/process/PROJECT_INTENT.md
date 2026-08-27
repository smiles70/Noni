# Project Intent, Audience, and Differentiation Assessment — Mynaani

**Process:** v9.51 deep-scan protocol (repository-level artifact and IDD review)
**Date:** 2026-08-26
**Assessor:** Devin, via repository-traceable evidence

## 1. Executive Finding

No standalone `CHARTER.md` file exists in the repository. The project's purpose, value, and differentiation are distributed across a primary Invention Disclosure Document (IDD), the README, an immutable `ARCHITECTURE.md`, and a closed-world reference library. Collectively these artifacts form a coherent, defensible project charter.

---

## 2. Foundational Documents (Provenance)

| Artifact | Location | Role |
|---|---|---|
| **Invention Disclosure Document (IDD)** | `docs/library/IDD-2026-cognitively-protective-iscs.md` | Verbatim patent-style disclosure; provenance for ISCS, UX Mediation Layer, and trajectory-based acceptance framework. Inventor: Kim Miles. |
| **Design Contract** | `docs/library/CONTRACT.md` | Authoritative closed-world UI, rendering, and AI-reasoning contract adopted by ADR 0019. |
| **Reference Library** | `docs/library/README.md` | Closed set of 22 permitted sources (2 primary + 20 secondary) and explicit exclusions. |
| **README** | `README.md` | Project purpose, tech stack, non-goals, API surface. |
| **Architecture Rules** | `ARCHITECTURE.md` | Immutable non-negotiable constraints. |
| **Decision Records** | `docs/decisions/` | 27 ADRs, including 0019 (closed-world contract) and 0021 (pricing/tiering). |
| **Competitor Analysis** | `docs/library/teaching-methodology-competitor-landscape.md` | Five real competitors and explicit strategic gap. |
| **Quality Rubric** | `docs/library/geragogy-quality-standards-rubric.md` | Geragogy-grounded quality dimensions and scoring. |

---

## 3. Purpose and Objective

### 3.1 High-level Purpose

Mynaani is a **geragogy-grounded AI learning system for older adults**. It teaches AI literacy and practical Claude/AI-assistant skills through a structured, dignity-centered curriculum.

> "Mynaani provides structured, respectful learning experiences designed specifically for older adults. The system prioritizes cognitive safety, dignity, and autonomy over speed or engagement metrics." — `README.md` §1

### 3.2 Core Objective

Deliver a complete, calm, user-controlled learning path that moves an older adult from first visit to useful AI literacy, then to personal productivity assets (Claude Skills and Agents), while preventing the cognitive overload, interface volatility, and manipulative patterns common in consumer learning platforms.

---

## 4. Target Audience

| Segment | Who | Needs / Concerns | How Mynaani Serves |
|---|---|---|---|
| **Primary learners** | Adults 55+ new or anxious about AI | Low confidence, fear of mistakes, privacy concerns, cognitive load, prior negative tech experiences | Calm onboarding, zero pressure, no accounts required for free content, predictability, reversibility, dignity-preserving language |
| **Caregivers / adult children** | Family members gifting access | Want to help parents without creating dependency or surprise charges | One-time caregiver gift edition, clear receipts, no ongoing relationship, no dark patterns |
| **Product / geragogy lead** | Designer and architect | Enforce geragogy standards and patentable architecture | Closed-world contract, reference library, ADR-governed change control |

The audience is explicitly framed as older adults whose needs are **not solved by simplification alone** but by systems that respect cognitive dynamics, preserve dignity, and support lifelong capacity for growth (`IDD-2026-cognitively-protective-iscs.md`, Section III).

---

## 5. Approach

### 5.1 Technical Approach: Backend Authority + ISCS

- **Interface State Control System (ISCS):** Models learner interaction as a latent state with an uncertainty matrix. The backend computes a stability metric and selects only states that satisfy a stability threshold. This is the core invention of the IDD.
- **Backend Authority:** All progression, state, and UI envelope decisions are made in auditable backend code. The frontend is a passive renderer (`ARCHITECTURE.md` Rules 1–2, `CONTRACT.md` §IV).
- **UI State Envelope:** Every renderable screen is returned as a typed envelope declaring `state_id`, `authorized_components`, `interaction_limits`, `layout_constraints`, and `transition_permissions` (ADR 0019).
- **Render Guards:** The React layer validates the envelope against the contract's 10 self-checks and fails closed if violated.

### 5.2 Pedagogical Approach: 4-Page Instructional Episode

Each curriculum unit follows a task-centered instructional sequence:

1. **Recap** — activate prior knowledge
2. **Principle** — state the concept simply
3. **Example** — worked example (grounded in Kalyuga 2012 and Sweller 2019)
4. **Retrieval** — low-stakes application, no time pressure, mistakes framed as useful data

This maps directly to Merrill's First Principles of Instruction (A3) and the 4C/ID model (A4) (`teaching-methodology-competitor-landscape.md`).

### 5.3 Design Approach: Closed-World Contract

| Contract Theme | Rule |
|---|---|
| Color | Low-arousal neutrals and muted accents; no neon or pure white/black |
| Typography | 16px minimum, 1.5–1.7 line height, ≤3 text levels, headings ≤1.4× body |
| Layout | 8px grid, fixed spatial positions, no reflow-driven rearrangement |
| Motion | Opacity fades only (120–180ms), linear/ease-out, no bounce or attention drawing |
| Density | ≤5 primary actions, ≤1 irreversible action, ≤1 highlighted recommendation |
| Components | V1 inventory of 11 approved components; no icons, no novelty components |
| AI | 10-item pre-flight self-check for any UI proposal (`CONTRACT.md` §V) |

### 5.4 Commercial Approach: Dignified, No-Dark-Pattern Pricing

- **Free tier:** Modules 1–3 (16 units) — complete AI literacy, no registration required
- **Paid tier:** Modules 4–5 (11 units) — one-time purchase, lifetime access, builds Claude Skills and Agents
- **No subscriptions, no auto-renew, no paywall mid-unit, no urgency/scarcity messaging**
- 30-day no-questions-asked refund (ADR 0021)

---

## 6. Value Proposition

For the **primary learner**, value is:

1. **Cognitive safety** — no sudden changes, no overwhelm, no evaluative pressure
2. **Dignified autonomy** — the learner is positioned as the decision-maker at every step
3. **Real, transferable skill** — Claude/AI literacy that is immediately useful
4. **Confidence preservation** — errors are reframed as useful data, no "wrong" framing

For the **caregiver**, value is a trustworthy way to introduce an older adult to AI without exposing them to predatory pricing, surprise charges, or confusing interfaces.

For the **project**, value is a defensible, patent-aligned intellectual-property position in a market segment where no competitor currently combines structured AI curriculum, geragogy-first design, and backend-governed cognitive protection.

---

## 7. Why This Application Exists

The repository itself states the existence rationale in the IDD and competitor analysis:

> "Conventional adaptive learning systems and graphical user interfaces rely on rule-based or heuristic-driven progression logic, leading to interface volatility, cognitive overload, and unpredictable interaction costs—issues that disproportionately affect older adult learners." — `IDD-2026-cognitively-protective-iscs.md`

The 2026-08-09 `login-loop-investigation-report` and the IDD both identify that older adults fail in digital learning **before observable performance errors** — at the interaction level, due to overload, loss of confidence, and emotional volatility. Existing adaptive systems treat correction after the fact. Mynaani exists to **regulate interaction before failure occurs**, making cognitive volatility a measurable system variable.

---

## 8. Differentiation from Competitors

The competitor analysis (`docs/library/teaching-methodology-competitor-landscape.md`) evaluates five real offerings:

| Competitor | Segment | Mynaani's Differentiation |
|---|---|---|
| Senior Planet / AARP OATS | Community learning (in-person + online) | Depth over breadth; cognitively protective UI; telemetry-gated progression |
| GCFLearnFree | Free reference tutorials | Structured instructional design; geragogy contract; AI-specific curriculum |
| AT&T Connected Learning / NCOA | Digital inclusion (basic skills) | AI literacy beyond the threshold; dignity-centered design |
| DigitalLearn (PLA / Cox) | Public library basic skills | AI-specific depth; complexity ramp; confidence-preserving assessment |
| GetSetUp | Live interactive classes | Asynchronous flexibility; structured progression; cognitively protective interface |

### Defensible Position — Four Gaps No Competitor Fills

1. **Structured, progressive Claude/AI curriculum** — not one-off sessions.
2. **Cognitively protective, geragogy-first UI** — not standard web or video interfaces.
3. **Telemetry-gated, complexity-managed progression** — not learner self-selection.
4. **Confidence-preserving assessment** — no scoring, no pass/fail, no evaluative framing.

---

## 9. Distinguishing Technical Novelty

The IDD frames the system's novelty as:

> "A novel class of regulated learning interfaces wherein pedagogical safety constraints are enforced through uncertainty-aware control logic, rather than heuristic adaptation." — `IDD-2026-cognitively-protective-iscs.md`

Specific claims in the IDD include:

- Recursive state estimation of a latent learner-interface state
- Uncertainty representation (covariance matrix)
- Bounded stability metric derived from that uncertainty
- Constrained optimization for selecting the next permissible UI state
- Information-theoretic divergence threshold for state transitions
- Reduced interface oscillation and predictable rendering as technical effects

This is not a generic LMS or content delivery platform; it is a **control-theoretic approach to interface and curriculum governance** in service of geragogy.

---

## 10. Artifact Gaps

| Gap | Observation |
|---|---|
| No `CHARTER.md` | Purpose, audience, and value are distributed across README, ARCHITECTURE, IDD, ADRs, and library documents. A single canonical `CHARTER.md` or `docs/CHARTER.md` would improve v9.51 compliance and onboarding. |
| No explicit persona document | Audience is inferred from README, IDD, golden landing flow, and ADR 0021. A `docs/PERSONAS.md` could be created. |
| IDD is patent-style, not market charter | The IDD is the strongest primary source but requires the surrounding contract to translate into product strategy. |

**Recommendation:** Create a canonical `docs/CHARTER.md` (or `.ai/process/CHARTER.md`) that consolidates purpose, audience, approach, value, and differentiation, with traceability to the IDD, CONTRACT, ADR 0019, and competitor analysis. This would close the artifact gap and improve Nelson/PRA scoring.

---

*Generated from repository evidence under Process v9.51.*
