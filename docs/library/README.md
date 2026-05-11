# Reference Library (Closed World)

**Status:** Authoritative. Adopted by ADR 0019, Sprint 21.

This directory is the **complete and closed** set of sources from which the AI assistant and all ADRs may reason about UI design, geragogy, cognitive load, and React rendering decisions for this system.

**The list is exhaustive.** Citations to any source not listed below are prohibited under the design contract (`CONTRACT.md`, Section V). Adding a source requires a new ADR in `docs/decisions/` per Section VI of the contract.

If you cannot ground a design decision in a source from this list, the decision cannot be made.

---

## Primary Sources (this repository)

| Ref | Document | Role |
|---|---|---|
| P1 | [`CONTRACT.md`](./CONTRACT.md) | Authoritative design, rendering, and governance contract. |
| P2 | [`IDD-2026-cognitively-protective-iscs.md`](./IDD-2026-cognitively-protective-iscs.md) | Invention disclosure document — provenance for ISCS, UX Mediation Layer, trajectory-based acceptance framework. Inventor: Kim Miles. |

---

## A. React & Frontend Architecture

| Ref | Source |
|---|---|
| A1 | React Official Documentation — react.dev |
| A2 | React Server Components & Rendering Model — Meta |
| A3 | "UI as a Pure Function of State" — React Core Principles |
| A4 | Flux / Redux Unidirectional Data Flow Concepts |
| A5 | Kent C. Dodds — Deterministic UI from External State |

## B. Predictability & Error-Resilient Interfaces

| Ref | Source |
|---|---|
| B1 | Nielsen Norman Group — Consistency, Predictability, Error Prevention |
| B2 | Norman, D. A. (2013). *The Design of Everyday Things*. Basic Books. |
| B3 | Cockburn, A., et al. (2014). Visuospatial Stability in Interface Design. |

## C. Geragogy & Cognitive Aging

| Ref | Source |
|---|---|
| C1 | Fisk, A. D., Rogers, W. A., Charness, N., Czaja, S. J., & Sharit, J. (2009). *Designing for Older Adults: Principles and Creative Human Factors Approaches*. CRC Press. |
| C2 | Czaja, S. J., & Lee, C. C. (2019). The impact of aging on access to technology. *Universal Access in the Information Society*, 18, 559–571. |
| C3 | Knowles, B., Hanson, V. L., Rogers, Y., Piper, A. M., Waycott, J., & Davies, N. (2019). HCI and aging: Beyond accessibility. *CHI 2019*. |
| C4 | Lazar, A., Brewer, R., & Knowles, B. (2025). HCI and older adults: The critical turn and what comes next. *Foundations and Trends in HCI*, 19(2), 112–212. |
| C5 | AARP & Older Adults Technology Services (2021). *Age-Inclusive Technology Design: A Practical Guide*. AARP. |

## D. Cognitive Load & Learning Stability

| Ref | Source |
|---|---|
| D1 | Sweller, J., Ayres, P., & Kalyuga, S. (2011). *Cognitive Load Theory*. Springer. |
| D2 | Paas, F., et al. (2003). Cognitive Load Measurement. |
| D3 | Mayer, R. E. (2009). *Multimedia Learning* (2nd ed.). Cambridge University Press. |

## E. Empirical UX Research for Older Adults

| Ref | Source |
|---|---|
| E1 | Amouzadeh, E., Dianat, I., Faradmal, J., & Babamiri, M. (2025). Optimizing mobile app design for older adults: A systematic review of age-friendly design. *Aging Clinical and Experimental Research*, 37, Article 248. |
| E2 | Gómez-Hernández, M., Ferré, X., Moral, C., & Villalba-Mora, E. (2023). Design guidelines of mobile apps for older adults: Systematic review and thematic analysis. *JMIR mHealth and uHealth*, 11, e43186. |
| E3 | Zhou, C., Yuan, F., Huang, T., Zhang, Y., & Kaner, J. (2022). The impact of interface design element features on task performance in older adults: Evidence from eye-tracking and EEG signals. *IJERPH*, 19(15), 9251. |
| E4 | Zhou, M., Cheng, Z., Sabran, K., & Zahari, Z. A. (2024). User interfaces for older adults to support social interaction through digital technology: A systematic review update. *Disability and Rehabilitation: Assistive Technology*, 19(7), 2430–2441. |

---

## Explicitly Excluded

The following categories of source are **prohibited as justification** for any decision in this system:

- UX trend blogs
- Gamification literature
- Marketing design systems
- Aesthetic-first or novelty-driven frameworks
- Sources not listed above, regardless of merit elsewhere

---

## Process for Adding a Source

1. Write a new ADR in `docs/decisions/NNNN-add-source-<short-name>.md`.
2. Justify the addition using only sources already on this list.
3. Update this README in the same commit as the ADR.
4. Reference the new source by ref ID (e.g., `C6`) in any code or doc that uses it.

No retroactive interpretation. No silent additions.
