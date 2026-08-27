# 0022 - Reduce free tier to Modules 1-2; Module 3 moves behind one-time purchase

## Status

Accepted (amends ADR 0021).

## Context

ADR 0021 originally placed the paywall at the Module 3 → Module 4 boundary, leaving Modules 1-3 free (16 units total) and Modules 4-5 paid (11 units). That design was chosen because the first three modules resolve on a complete AI-literacy arc, giving every learner a dignified, complete free education.

Subsequent monetization research (MONETIZATION-001) and product testing indicated that the free tier was large enough that many B2C learners perceived the paid tier as too narrow a value add for $39. The team wants to test a shorter free path while preserving the architecture's anti-dark-pattern, geragogy-aligned constraints.

This ADR amends only the module boundary; it does **not** change the one-time purchase model, the $39/$59 prices (revisable per ADR 0021 (3)), the 30-day refund, or the prohibition on subscriptions, ads, urgency, or dark patterns.

## Decision

1. **Free tier: Modules 1 and 2 only.** Modules 1-2 are a complete orientation to Claude, safe use, and real-world practice; they are the trust-building sample.

2. **Paid tier: Modules 3, 4, and 5.** All three modules are unlocked by the same one-time purchase (product code `modules_4_5` is renamed in code references to `modules_3_5` where appropriate; the existing `Product.code` may be renamed or a new product created, but the learner-facing price remains one-time).

3. **No paywall mid-unit.** The paywall is encountered only when the learner attempts to enter Module 3. A learner inside a unit completes that unit.

4. **Hard prohibitions from ADR 0021 (7) remain in force.** No countdowns, no scarcity, no ads, no auto-renew, no engagement-triggered upsells, no dark-pattern cancellation.

5. **Free tier remains a real education, not a teaser.** Modules 1-2 teach safe, confident Claude use; the paid modules deepen judgment and add the build-Skills/Agents capability.

## Consequences

- The paywall now appears at the Module 2 → Module 3 boundary.
- Module 3 curriculum endpoints (`/api/curriculum/module-3/...`) must be gated by the entitlement dependency, the same as Module 4/5.
- Frontend loaders, the curriculum menu, and help copy must treat Module 3 as paid.
- Tests that previously asserted Module 3 was free must be updated or deleted.
- The product code `modules_4_5` may be changed to `modules_3_5` in a follow-up; the first pass gates Module 3 behind the existing `modules_4_5` entitlement to minimize data-model churn.
