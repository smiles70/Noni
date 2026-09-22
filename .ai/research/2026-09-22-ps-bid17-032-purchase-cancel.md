# Verification memo — PS-BID17-032 (/purchase/cancel restyle + fix)
Codebase checks: PurchaseCancelPage (46 lines); two CTAs — /curriculum
(L32) + /paywall (L39), both unconditional, no entitlement check anywhere
in file. Guard rule: entitled learner must not route back to paywall.
Fix = entitlement probe (billing status endpoint precedent exists in
billing.ts) → suppress paywall CTA when entitled; fail-safe = current
behavior on probe error. Jev hedged 0.56 — implement as CTA-suppression,
not silent redirect. Protocol deviation documented.
