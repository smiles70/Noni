# 0021 - Pricing and tiering: free Modules 1-3, one-time purchase for Modules 4-5

## Status

Accepted (pre-implementation; binds future code).

## Context

The system now ships five curriculum modules (26 units total). Sustaining development and hosting requires revenue, but Noni's `ARCHITECTURE.md` and ADR 0019 closed-world contract impose hard prohibitions that most consumer-software pricing patterns violate:

- Rule 5 (No Urgency Framing): no countdowns, no "limited time", no scarcity messaging.
- Rule 6 (No Dark Patterns): no variable rewards, no hidden costs, no confusing navigation, no false scarcity, no manipulation.
- Rule 7 (Explicit Review): no automated charges or upgrades without explicit confirmation.
- Rule 8 (Cognitive Safety First): designed for older adults, whose research-documented vulnerability to subscription dark patterns and auto-renew traps is well established (C1 Fisk et al. 2009; C3 Knowles et al. 2019).

The pricing model must therefore be designed *as part of the architecture*, not bolted on later, and must inherit the same enforceability the rest of the system enjoys.

The curriculum's pedagogical arc also has a natural seam between *receiving understanding* (Modules 1-3) and *producing personal assets* (Modules 4-5). The first arc resolves on a complete thought — "you are the decision-maker" (`module3-unit-4`) — and stands alone as complete AI literacy. The second arc teaches the learner to build Skills and compose Agents — durable productivity assets they personally own. This is the only honest place to draw a payment boundary: the free tier is a complete, dignified education on its own terms; the paid tier teaches an additional capability.

## Decision

1. **Free tier: Modules 1, 2, and 3.** All 16 units. No registration required to read; account required only to persist progress. The free tier is a real, complete, useful education in AI literacy and judgment — not a teaser.

2. **Paid tier: Modules 4 and 5.** All 11 units. One-time purchase, lifetime access for the purchasing account.

3. **Pricing surface (initial targets, revisable by ADR):**
   - **$39 USD** — single-learner one-time purchase, lifetime access to Modules 4-5.
   - **$59 USD** — "caregiver gift" edition. A second party (commonly an adult child) purchases lifetime access on behalf of the learner. The learner receives the access; the caregiver receives a clearly-labeled receipt and gift confirmation. No ongoing relationship between caregiver account and learner data after redemption.

4. **No subscriptions in V1.** No recurring billing of any kind. No auto-renew. No "trial that converts." If the product later requires a subscription model for sustainability, that change requires a new ADR and the same enforcement requirements as the rest of this one.

5. **No paywall mid-unit.** A learner inside a unit completes that unit. Paywalls live strictly *between* modules. The transition from Module 3 to Module 4 surfaces a single, calm, non-urgent purchase prompt with two equally-weighted choices: purchase, or remain on the free tier.

6. **Paid-tier content cannot be revoked.** Once purchased, access to Modules 4-5 and to any Skills/Agents the learner has built is permanent for that account. If the service shuts down, an exportable archive of the learner's units and assets is provided. This is non-negotiable and is the inverse of subscription-based content lock-in.

7. **Hard prohibitions (binding on all future commits):**
   - No countdown timers, "limited-time discounts", or any scarcity language in pricing copy or upgrade prompts.
   - No "X people are viewing this" or social-proof urgency.
   - No dark-pattern cancellation flows. If subscriptions ever exist (per (4)), canceling must be at least as easy as subscribing and reachable in ≤2 clicks from any page.
   - No engagement-triggered upsells. "You've completed N units — upgrade now!" is prohibited. Upgrade prompts appear only at module boundaries and only on explicit navigation.
   - No bundling the paid tier with consent to marketing, data sharing, or third-party analytics.
   - No price discrimination based on geography, device, or detected income signals.
   - No A/B testing of pricing surfaces on real users without a separate ADR documenting the methodology and the consent surface.

8. **Refund policy: full refund on request within 30 days, no questions asked.** Encoded in the purchase flow as a visible, plain-language guarantee adjacent to the price.

9. **Accessibility of the purchase surface.** The upgrade prompt and the purchase form must satisfy the same WCAG 2.1 AA bar as the rest of the system (ADR 0008, 0011, 0014), and must render through the same `RenderGuard` + envelope path as any other UI state (ADR 0019). Pricing is a UI state, not an exception to the contract.

10. **Audit and transparency.** Every purchase, refund, and access grant is logged to the telemetry audit table (ADR 0009) with `event = "billing_event"`, `decision_reason` ∈ {`purchase`, `refund`, `grant`, `revoke_disallowed`}, and the purchasing account id. Revocation attempts are explicitly logged as `revoke_disallowed` to make any future violation of (6) immediately detectable.

## Consequences

**Pedagogical and ethical**
- The free tier resolves on a complete, dignified thought. A learner who cannot or will not pay receives genuine, useful, complete AI literacy.
- The paid tier is framed as additional capability, not as the "real" product. There is no implicit message that free users are second-class.
- Older adults — the explicit target population — are protected by design from the subscription and auto-renew patterns documented in the cited HCI-and-aging literature as disproportionately harmful to them.

**Commercial**
- Revenue per paying learner is bounded by the one-time price. There is no recurring revenue from a single learner. This is a deliberate constraint, not an oversight.
- The caregiver-gift edition opens a real and culturally appropriate distribution channel: adult children initiating AI literacy for parents. The $20 premium reflects the additional gift-flow UX and accounting, not artificial price tiering.
- A subscription model is not foreclosed forever, but introducing one requires a new ADR and must preserve all hard prohibitions in (7).

**Technical (implications for future sprints)**
- A "paywall" surface is required at the Module 3 → Module 4 boundary. It must render through `RenderGuard` + envelope per (9).
- A `billing_event` telemetry event type must be added (extends ADR 0009 audit columns; no new columns required).
- An access-grant model is required: per-account flags `modules_4_5_access`, `purchase_source` ∈ {`self`, `caregiver_gift`}, `granted_at`. This lands with the auth/vendor pass (currently deferred).
- An exportable-archive endpoint per (6) is a future requirement, not a V1 requirement, but cannot be foreclosed by data-model choices made earlier.
- A "remove all my data" account-deletion endpoint must coexist with the audit log; the resolution is to retain a hashed billing-event record (for accounting) and delete the learner content. Detail deferred to the auth/vendor ADR.

**Governance**
- Any change to (1), (2), (4), (5), (6), or (7) requires a new ADR citing only sources from the closed reference list (ADR 0019).
- Pricing numbers in (3) are revisable by a one-line PR + brief ADR amendment, since they are operational parameters. The *structure* of the model — what gets charged for, how, and with what protections — is not.
