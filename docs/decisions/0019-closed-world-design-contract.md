# 0019 - Closed-world design, rendering, and AI-reasoning contract

## Status

Accepted (Sprint 21).

## Context

ADRs 0001–0018 established architectural decisions (backend authority, accessibility, telemetry, container strategy, module gating patterns) but referenced design rationale informally — sometimes by citing sources that, on later verification, were either misattributed (e.g., a recurring "Carr 2009" that has no traceable provenance and was almost certainly a corruption of Fisk et al. 2009) or out of scope for this system's chosen evidence base.

Two parallel inputs converged in Sprint 21:

1. **The inventor's IDD** — "Cognitively-Protective Interface-Controlled Learning System" (Kim Miles, 2026) — formalizes the ISCS as uncertainty-constrained state estimation and introduces the UX Mediation Layer and trajectory-based acceptance framework as primary architectural concepts.
2. **The clarified Cognitively Protective Interface Design, Rendering, and Governance Contract** — a fully specified, closed ruleset for color, geometry, grid, typography, components, iconography, interaction density, motion, accessibility, state transparency, React rendering behavior, AI self-check, and decision governance, with a closed list of permitted reference sources.

The contract is not a stylistic preference. It is the operational implementation of the IDD's stability constraints at the UI layer. Without it, "stability" remains backend-only and the frontend can silently violate the very properties the ISCS exists to enforce.

The contract is closed-world by design: open-ended citation pools have already produced one provably fabricated reference and several mis-summarized ones in this repo. A closed list eliminates that class of error.

## Decision

1. **Adopt `docs/library/CONTRACT.md` as the authoritative design, rendering, and AI-reasoning contract** for this system. The contract supersedes any conflicting design language in prior ADRs. Decisions in prior ADRs remain in force; only their citations are subject to re-grounding under this ADR.

2. **Adopt `docs/library/README.md` as the closed reference list.** Two primary sources (CONTRACT, IDD) plus 20 external sources across five categories (A–E). Any citation outside this list is prohibited.

3. **Adopt `docs/library/IDD-2026-cognitively-protective-iscs.md` as a primary architectural source.** ADRs and code comments may cite it directly as the provenance for ISCS, the UX Mediation Layer, and the trajectory-based acceptance framework.

4. **Three genuinely new technical commitments** (these are *additions*, not restatements of prior ADRs):

   - **UI State Envelope requirement.** All backend endpoints that drive a renderable screen must return a typed envelope declaring `state_id`, `authorized_components` (drawn from the 11-item V1 inventory), `interaction_limits`, `layout_constraints`, and `transition_permissions`. Undefined states cannot render. Existing endpoints adopt this via an additive wrapper so payloads remain backward compatible.

   - **React Render Guards (fail-closed).** All rendering passes through a `RenderGuard` boundary that validates the envelope against the contract's ten self-check items. On violation, the guard renders an explicit `BlockedNotice` naming the failed check; it never silently degrades or falls back. Guards are non-overrideable.

   - **AI UI Self-Check pre-flight.** The ten-item self-check in Section V of the contract is a mandatory pre-flight for any UI proposal produced by the AI assistant working in this repo. Compliance is asserted in the commit message for any UI-affecting change.

5. **Design governance.** Any expansion of the color set, component inventory, motion vocabulary, spacing scale, or reference library requires a new ADR that justifies the change using only sources already on the closed list.

## Consequences

- The system gains an enforceable boundary between "what backend approved" and "what frontend rendered." Drift between the two becomes a runtime-visible event (`BlockedNotice`), not a silent UX regression.
- Citation hygiene becomes verifiable. The closed list is small enough to audit fully; no future "Carr 2009" can propagate through ADRs unnoticed.
- Future UI work must pick from 11 components. Anything else is an ADR. This is a deliberate brake on component-inventory growth, which is one of the largest sources of cognitive load drift in long-lived design systems.
- Existing frontend code (`LandingPage.tsx`, `CurriculumRenderer.tsx`) will not satisfy the contract on day one. A subsequent sprint (Sprint 22, "closed-world migration") brings them into compliance. Until then, the existing screens continue to render as they do today; the contract is enforced only on new code wrapped in `RenderGuard`.
- Some prior ADRs cite sources now off the closed list (e.g., Hawthorn 2000, Lövdén 2010, Williams/Wadleigh/Ylänne 2010, Czaja/Boot/Charness/Rogers 2019). Their *decisions* remain accepted. A follow-up pass under this ADR rewrites their citations to on-list sources without altering the decision text; the original ADRs receive a one-line header noting the re-grounding.
- The IDD is now a citable primary source in this repo. Architectural claims that previously needed secondary literature can cite it directly.
- The AI assistant operating in this repo is bound by the same self-check as the rendering layer. Proposals that cannot be expressed within the contract must be rejected, not approximated.

## References

- `docs/library/CONTRACT.md` (P1)
- `docs/library/IDD-2026-cognitively-protective-iscs.md` (P2)
- `docs/library/README.md` (closed reference list, refs A1–E4)
