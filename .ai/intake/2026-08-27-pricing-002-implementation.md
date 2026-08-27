# Intake — PRICING-002: Implement the recommended Mynaani pricing model

**Date:** 2026-08-27  
**Requester:** Product  
**Process:** v9.51  
**Scope:** Implement the pricing model selected in PRICING-001: one-time $39 single-learner / $59 caregiver-gift purchase for Modules 4-5; no subscription; optional reverse-trial readiness; and paywall at the Module 3→4 boundary.

---

## Motivation

PRICING-001 research validated ADR 0021's one-time purchase structure and identified the caregiver-gift channel as the highest-WTP path. The system now needs concrete paywall, billing, and gift-redemption capabilities.

## Inputs

- `.ai/process/PRICING_RESEARCH_001.md`
- `.ai/process/PRICING_ONTOLOGY_001.md`
- `docs/decisions/0021-pricing-and-tiering.md`
- `docs/design/pricing.md`

## Scope

### In scope

1. Pricing page (`/pricing`) with clear, plain-language copy.
2. Paywall page at the Module 3→4 boundary (`/paywall` or modal).
3. One-time purchase flow for the learner (Stripe checkout or mock in dev).
4. Caregiver gift purchase flow (`/gift` or `/purchase/gift`).
5. Access-grant persistence: `modules_4_5_access`, `purchase_source`, `granted_at`.
6. 30-day refund capability and audit logging.

### Out of scope (future ADR)

1. Optional 7-day reverse trial of Module 4.
2. Exportable archive of Skills/Agents on service shutdown.
3. B2B / institutional licensing.
4. A/B testing of pricing surfaces.

## Constraints

- No subscription or auto-renew.
- No countdown timers, scarcity, or social-proof urgency.
- No paywall inside a unit; paywall appears only between modules.
- No dark-pattern cancellation; refund must be self-serve.
- Payment surface must be WCAG 2.1 AA and `RenderGuard`/ISCS compliant.
- All billing events logged to `billing_event` telemetry table.

## Acceptance criteria

1. An unauthenticated or free user can view the pricing page without creating an account.
2. A learner completing Module 3 sees a calm paywall with two equally weighted options: continue free or one-time purchase.
3. A learner can purchase Modules 4-5 for $39; access is immediately granted and permanent.
4. A caregiver can purchase a $59 gift; the learner receives a redemption link via Magic.link.
5. A user can request and receive a refund within 30 days in ≤2 clicks.
6. Telemetry logs `purchase`, `refund`, `grant`, `revoke_disallowed` events.
7. Type-check, build, and bundle verification pass.

## Risks

1. Payment processor selection (Stripe vs. mock) is a deferred decision.
2. Tax handling (VAT/sales tax) is not modeled.
3. Access-grant model must coexist with account deletion and audit retention.
