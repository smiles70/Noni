# PS-BID17-028 — Caregiver-path design drift inventory

**Date:** 2026-09-22 · **Priority:** P2 · **Status:** inventoried — Jev says act
**Skill check:** `geragogy` + `journey-loop-guard` invoked. Same methodology
as PS-BID17-020 (community-path inventory).

## Problem statement

The caregiver journey has the same split-grammar seam the community path
had: `/caregiver` was redesigned in bid-17, but every surface the
caregiver touches next still runs the pre-bid-17 AccountStyles grammar.

## Inventory (verified in code)

| Route | Component | Grammar | Integrations | Notes |
|-------|-----------|---------|--------------|-------|
| `/caregiver` | CaregiverPage | MARKETING (41 refs) | ChatWidget `gift` | redesigned bid-17 |
| `/gift` | GiftCheckoutPage | OLD AccountStyles | `startGuestCheckout` → Stripe `checkout_url`, gift widget | **double-mounts ChatWidget** (L120 inside card + L122 outside) |
| `/gift-redeem` | GiftRedeemPage | OLD | redemption → `goPaidCurriculum` (guard-correct) | auth-gated |
| `/purchase/success` | PurchaseSuccessPage | OLD | entitlement/session confirm; gift widget conditional on `isGift` | shared gift+self |
| `/purchase/cancel` | PurchaseCancelPage | OLD | none | **"Return to paywall" CTA fires unconditionally — no entitlement check (journey-guard exposure)** |

## Persona isolation

Clean — zero facility/organization/partner strings on any caregiver
surface. Gift widget journeys all `journey="gift"`. Learner track never
receives facility content.

## Jev gate (jev-1.13.0)

- Surfaces inconsistent with redesigned grammar: **0.90**
- Drift user-visible mid-journey (marketing → checkout → success): **0.87**
- Transaction surfaces riskier to change than informational: 0.83
- Journey-loop audit mandatory on restyle: 0.77
- Scope pick: **full-path**
- Severity: **act (1.93)**

## Findings beyond drift

1. `GiftCheckoutPage` mounts `<ChatWidget journey="gift">` twice —
   script dedupes by id so it's functionally harmless, but two React
   instances both run the effect. Cleanup-worthy.
2. `PurchaseCancelPage` "Return to paywall" has no entitlement check —
   pre-existing journey-guard exposure, independent of restyle.

## Sub-tickets

- PS-BID17-029 `/gift` checkout restyle (Stripe + widget preserved)
- PS-BID17-030 `/gift-redeem` restyle (auth + guard routing preserved)
- PS-BID17-031 `/purchase/success` restyle (gift/self split preserved)
- PS-BID17-032 `/purchase/cancel` restyle + entitlement-check fix
