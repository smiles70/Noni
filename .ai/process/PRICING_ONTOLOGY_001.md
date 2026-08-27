# PRICING-001 Ontology

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-pricing-research-001.md`  
**Purpose:** Normalize the entities and relationships discovered during PRICING-001 so they can be traced in the canonical knowledge graph.

---

## Entities

| Entity | ID pattern | Definition | Examples |
|--------|------------|------------|----------|
| `SourceArtifact` | `SRC-<name>` | Authoritative, published source used as evidence. | `SRC-AARP-2025`, `SRC-JAMR-2017`, `SRC-ADR-0021` |
| `Requirement` | `REQ-PRICING-###` | A pricing-related condition the system must satisfy. | `REQ-PRICING-001` |
| `Persona` | `PERSONA-<name>` | A user type whose willingness-to-pay or behavior matters. | `PERSONA-Learner-55Plus`, `PERSONA-Caregiver` |
| `Journey` | `JOURNEY-<name>` | A user path that intersects with pricing. | `JOURNEY-FreeToPaid`, `JOURNEY-GiftPurchase` |
| `Capability` | `CAP-PRICING-###` | A system ability that satisfies one or more requirements. | `CAP-Paywall`, `CAP-GiftRedeem` |
| `UserStory` | `US-PRICING-###` | A concrete user-facing pricing story. | `US-PRICING-001` |
| `AcceptanceCriterion` | `AC-PRICING-###` | Observable condition for a capability. | `AC-PRICING-001` |
| `Decision` | `DEC-PRICING-###` | A chosen strategy or policy. | `DEC-PRICING-001` |
| `Evidence` | `EVI-PRICING-###` | A finding that supports or refutes a requirement or decision. | `EVI-PRICING-001` |
| `Owner` | `OWNER-<name>` | Role accountable for the decision. | `OWNER-Product` |
| `Dependency` | `DEP-PRICING-###` | A relationship where one capability requires another. | `DEP-PRICING-001` |
| `Assumption` | `ASM-PRICING-###` | A stated assumption underlying a requirement or decision. | `ASM-PRICING-001` |
| `Gap` | `GAP-PRICING-###` | A missing capability or unvalidated assumption. | `GAP-PRICING-001` |
| `BudgetProfile` | `BUDGET-<name>` | A cost/revenue envelope. | `BUDGET-PaidModules` |

## Relationships

| Relationship | Meaning |
|--------------|---------|
| `defines` | SourceArtifact introduces a Requirement. |
| `serves` | Requirement serves a Persona. |
| `part_of` | Journey or UserStory is part of a larger Journey. |
| `evidenced_by` | Requirement or Decision is supported by Evidence. |
| `implements` | Capability implements a Requirement. |
| `depends_on` | Capability depends on another Capability. |
| `enables` | Journey enables another Journey. |
| `decides` | Decision resolves one or more Requirements. |
| `owned_by` | Decision or Requirement has an Owner. |
| `assumes` | Requirement or Decision assumes an Assumption. |
| `has_gap` | Requirement or Capability has an unmet Gap. |

---

## Canonical nodes for PRICING-001

### SourceArtifacts

- `SRC-AARP-2025` — AARP *2025 Tech Trends and Adults 50-Plus*.
- `SRC-JAMR-2017` — Yamauchi et al., *Willingness to Pay for Elderly Telecare Service*, i-JMR 2017.
- `SRC-RMHP-2024` — Yuan et al., *Determinants of WTP for Digital Health Technologies*, RMHP 2024.
- `SRC-GERONTOL-2016` — Wang et al., *Caregivers' WTP for Technologies*, The Gerontologist 2016.
- `SRC-JMIR-2024` — Tang et al., *Older US Adults WTP for Telehealth*, JMIR 2024.
- `SRC-CHI-2024` — CHI 2024 *Deceptive Patterns and Older Adults*.
- `SRC-GERAGOGY-2022` — Gates & Wilson-Menzfeld, *Geragogy in Digital Skills Programs*.
- `SRC-ADR-0021` — Existing pricing and tiering decision.
- `SRC-PROFITWELL` — Patrick Campbell / ProfitWell pricing frameworks.
- `SRC-KYLE-POYAR` — Kyle Poyar PLG pricing guidance.
- `SRC-TOOLRADAR-2026` — B2B SaaS pricing benchmarks.
- `SRC-DUOLINGO` — Duolingo public pricing.
- `SRC-LUMOSITY` — Lumosity public pricing.

### Requirements

- `REQ-PRICING-001` — Pricing must respect older-adult willingness and ability to pay.
- `REQ-PRICING-002` — Pricing must avoid subscription dark patterns (auto-renew, hard-to-cancel, hidden costs).
- `REQ-PRICING-003` — Pricing must support a caregiver/proxy payer.
- `REQ-PRICING-004` — Pricing must align with geragogy: autonomy, low pressure, transparent value.
- `REQ-PRICING-005` — Pricing must fit the landing → auth → free modules → paywall flow.
- `REQ-PRICING-006` — Paid tier must be framed as additional capability, not as gating the "real" product.
- `REQ-PRICING-007` — Pricing must include a visible, no-questions refund policy.

### Personas

- `PERSONA-Learner-55Plus` — Older adult learning AI at own pace; low-to-moderate WTP.
- `PERSONA-Caregiver` — Adult child or caregiver purchasing on behalf of learner; higher WTP, emotionally motivated.

### Journeys

- `JOURNEY-FreeToPaid` — Learner completes Modules 1-3, encounters paywall, chooses to purchase Modules 4-5.
- `JOURNEY-GiftPurchase` — Caregiver buys access on behalf of learner; learner redeems.
- `JOURNEY-ReverseTrial` — Learner previews Module 4 for 7 days, then decides to buy or stay free.

### Capabilities

- `CAP-Paywall` — Render a calm, accessible paywall at Module 3→4 boundary.
- `CAP-GiftRedeem` — Allow caregiver purchase and learner redemption of Modules 4-5.
- `CAP-Refund` — Self-serve 30-day refund request and audit logging.
- `CAP-ReverseTrial` — Optional 7-day preview of Module 4 without auto-charge.
- `CAP-PricingPage` — Dedicated, plain-language pricing page.

### UserStories

- `US-PRICING-001` — As a learner, I want to start for free so I can judge value before paying.
- `US-PRICING-002` — As a learner, I want a one-time purchase so I am not locked into recurring charges.
- `US-PRICING-003` — As a caregiver, I want to buy access for a loved one and receive a clear receipt.
- `US-PRICING-004` — As a learner, I want to preview paid content before I commit.
- `US-PRICING-005` — As any user, I want to cancel or refund easily if I change my mind.

### AcceptanceCriteria

- `AC-PRICING-001` — Paywall must display price, refund policy, and a "continue free" option before payment.
- `AC-PRICING-002` — Gift purchase must not link caregiver and learner accounts after redemption.
- `AC-PRICING-003` — Reverse trial must not collect payment method at start and must not auto-charge.
- `AC-PRICING-004` — Refund request must be reachable in ≤2 clicks and logged to `billing_event`.

### Decisions

- `DEC-PRICING-001` — Retain one-time lifetime purchase for Modules 4-5 at $39 single / $59 gift.
- `DEC-PRICING-002` — Add optional 7-day reverse trial of Module 4 as a future ADR, not V1.
- `DEC-PRICING-003` — No subscription / auto-renew in V1.

### Evidence

- `EVI-PRICING-001` — AARP 60% unwilling to pay for free services.
- `EVI-PRICING-002` — Telecare WTP median $3.70/month.
- `EVI-PRICING-003` — Caregiver WTP $50–$70/month.
- `EVI-PRICING-004` — Hidden costs / hard-to-cancel top concerns for older adults.
- `EVI-PRICING-005` — B2C conversion 20%, 50% in first 7 days.
- `EVI-PRICING-006` — Comparable edtech annual prices $60–$168.
- `EVI-PRICING-007` — Geragogy emphasizes autonomy and self-directed learning.

### Assumptions

- `ASM-PRICING-001` — Learners value the free tier as a complete education and the paid tier as skill-building.
- `ASM-PRICING-002` — Caregivers are willing to spend $59 as a one-time gift.

### Gaps

- `GAP-PRICING-001` — No primary Van Westendorp survey of Mynaani learners/caregivers yet.
- `GAP-PRICING-002` — Marginal cost of serving paid module users (Claude API, storage) is not modeled.
- `GAP-PRICING-003` — Payment processor and tax handling not selected.

### Owners

- `OWNER-Product` — Accountable for pricing decision.
- `OWNER-Engineering` — Accountable for paywall/gift/reverse-trial implementation.
- `OWNER-Research` — Accountable for evidence and WTP validation.

---

## Provenance rules

1. Every Requirement must be `evidenced_by` at least one Evidence or SourceArtifact.
2. Every Decision must be `decides` at least one Requirement.
3. Every Capability must `implement` at least one Requirement.
4. Every Assumption must be attached to a Requirement or Decision.
5. Every Gap must be `has_gap` on a Requirement or Capability.
