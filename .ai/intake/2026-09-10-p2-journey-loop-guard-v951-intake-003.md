# Intake: journey loop and paywall guard

**Process:** v9.51
**Date:** 2026-09-10
**ID:** P2-JOURNEY-LOOP-003
**Status:** INTAKE — research, architecture, and design complete; build NOT authorized.
**Owner:** Product + Platform
**Source:** `AGENTS.md` journey-loop-guard rule and post-gift-checkout UAT observation.

---

## 1. Problem statement

After completing a `modules_4_5` self-purchase or gift redemption, the learner can
still be routed to `/paywall` or the free `/curriculum` track. This causes one
of three failure modes:

1. A paywall loop: an already-entitled learner completes free track, clicks
   "Continue to paid modules," and is shown the paywall again.
2. A reset to zero: a learner whose `localStorage` progress is on the free track
   is sent back to the first free unit even though they own the paid bundle.
3. A purchase-cancel loop: an entitled learner on `/purchase/cancel` clicks
   "Return to paywall" and is re-offered a product they already own.

The 5 items below are all instances of the same root cause: the frontend routes
by progress or hardcoded paywall CTAs instead of by active entitlement.

---

## 2. ICP / persona

| Persona | Goal | Frustration |
|---|---|---|
| **Senior learner who bought access** | Continue into the paid modules after the free track | Keeps being asked to buy again |
| **Gift recipient** | Redeem a code and start learning | Ends up at the start of the free track |
| **Returning learner on a new device** | Resume where they left off | Progress is gone because it was only in `localStorage` |

---

## 3. Current-state evidence

1. **Free-track completion CTA is not entitlement-aware**
   - `frontend/src/components/CurriculumRenderer.tsx:60` passes
     `onContinueGated={goPaywall}` as the end-of-sequence handler.
   - `frontend/src/components/curriculum/LessonRenderer.tsx:370-372` calls
     `onSequenceComplete()` without checking entitlement.
   - `LessonRenderer` `getContinueLabel` always says "Continue to paid modules"
     on the last page of the free track.

2. **Paywall surface is not entitlement-aware**
   - `frontend/src/components/PaywallPage.tsx:155` renders "Buy" / "Buy as a
     gift" CTAs unconditionally.
   - No call to an entitlement endpoint to decide whether to show a
     "Continue to paid modules" CTA.

3. **Resume helper is progress-based, not entitlement-based**
   - `frontend/src/App.tsx:122-129` `goCurriculum()` reads `readProgress()` and
     only picks `/paid-curriculum` when `saved.module === 4 || saved.module === 5`.
   - A new gift recipient with `module: 0-2` or `null` progress is sent to
     `/curriculum`.

4. **Purchase cancel surface can re-loop to paywall**
   - `frontend/src/components/PurchaseCancelPage.tsx:39-40` "Return to paywall"
     button calls `navigate("/paywall")` unconditionally.

5. **Progress is not cross-device**
   - `frontend/src/lib/progress.ts:13-31` stores `mynaani_progress_v1` in
     `localStorage` only.

---

## 4. Options evaluated

| Option | Description | Verdict |
|---|---|---|
| A — leave as-is | Entitlement checks deferred to a future sprint | Current P2 loop remains in staging; customer-visible |
| B — frontend-only heuristics | Use `module >= 3` or `localStorage` flags to decide routing | Fragile; breaks when `localStorage` is empty or migrated |
| C — backend entitlement endpoint + frontend checks | `/api/me/entitlements` returns `modules_4_5` boolean; pages and resume helpers use it | Recommended |
| D — server-side progress sync | Store progress in DB; replace `localStorage` | Correct for cross-device but larger scope; separate P2 |

**Selected:** Option C for items 1-4. Option D for item 5 is a separate track and
out of scope for this P2 unless explicitly resourced.

---

## 5. Architecture

### Backend

1. New `GET /api/me/entitlements` (or `/api/v1/me/entitlements`) returns the
   active products for the current account, e.g. `{ "modules_4_5": true }`.
2. Reuse existing `entitlements` service and `Account` relationship.

### Frontend

1. New `useEntitlements()` hook or `AuthProvider` augmentation that fetches
   `/api/me/entitlements` on READY.
2. `CurriculumRenderer` / `LessonRenderer`:
   - `onSequenceComplete` for the last free unit checks `entitlements.modules_4_5`.
   - If entitled, route to `/paid-curriculum`.
   - If not, route to `/paywall`.
3. `PaywallPage`:
   - If `entitlements.modules_4_5` is true, show "Continue to paid modules" CTA
     to `/paid-curriculum` instead of "Buy".
4. `goCurriculum` remains a resume helper, but `PurchaseSuccessPage`,
   `GiftRedeemPage`, and any other post-grant surface continue to bypass it and
   route straight to `/paid-curriculum`.
5. `PurchaseCancelPage`:
   - If `entitlements.modules_4_5` is true, "Return to paywall" becomes
     "Continue to paid modules" and routes to `/paid-curriculum`.
   - If not, keep `/paywall`.

### Item 5 (cross-device progress)

- Intake-only for this P2.
- Future ADR required: server-side `Progress` table, sync on unit/page change,
  `localStorage` as optimistic fallback.

---

## 6. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Entitlement source | Backend `/api/me/entitlements` | Single source of truth; works across devices and sessions. |
| Hook placement | `AuthProvider` or `useEntitlements()` | One request per authenticated session. |
| Cancel page guard | Check entitlement, then route to paid or paywall | Prevents loops for already-entitled learners. |
| Progress sync | Defer to separate P2 | Larger data-migration and offline-fallback design needed. |

---

## 7. MLDC alignment

- Use existing `PRIMARY_BTN`, `SECONDARY_BTN`, and tokenized styles.
- No new animation.
- Copy is plain-language, no urgency.
- Contrast must pass MARTY contrast check (existing P2).

---

## 8. Nelson repo-hygiene / knowledge-graph

- Intake references `AGENTS.md` journey-loop-guard rule and
  `.devin/skills/journey-loop-guard/SKILL.md`.
- Adds `entitlement-check` and `paid-track-resume` nodes to
  `.ai/ontology/user-journey-ontology.json`.
- Updates `.ai/journeys/default/journey.yml` with entitlement-aware edges.
- Maps to existing `entitlements` service and `Purchase` model.

---

## 9. Epic / Block / Rack plan

### Epic — JOURNEY-LOOP-003: entitlement-aware routing

| Block | Rack | Deliverable | Owner |
|---|---|---|---|
| **Entitlement API** | Endpoint | `GET /api/me/entitlements` | Backend |
| | Tests | `test_me_entitlements.py` | Backend |
| **Curriculum end CTA** | Route check | `LessonRenderer` uses entitlement for `onSequenceComplete` | Frontend |
| | Unit test | `LessonRenderer` test for entitled vs. unentitled | Frontend |
| **Paywall guard** | CTA change | `PaywallPage` shows "Continue" when entitled | Frontend |
| | E2E test | Playwright paywall entitlement state | Frontend |
| **Cancel guard** | CTA change | `PurchaseCancelPage` routes to paid track when entitled | Frontend |
| | Unit test | `PurchaseCancelPage` test | Frontend |
| **Auth wiring** | Hook | `useEntitlements()` in `AuthProvider` | Frontend |
| | Contract | E2E for post-purchase and post-redemption | Frontend |

---

## 10. Test plan

### Unit / integration

- `backend/tests/test_me.py`: entitlements endpoint returns correct flags.
- `frontend/src/components/__tests__/LessonRenderer.test.tsx`: end-of-free
  track CTA route changes with `entitlements.modules_4_5`.
- `frontend/src/components/__tests__/PaywallPage.test.tsx`: buy CTA hidden and
  continue CTA shown when entitled.
- `frontend/src/components/__tests__/PurchaseCancelPage.test.tsx`: route
  respects entitlement.

### E2E

- `frontend/e2e/entitlement-routing.spec.ts`:
  - Free track end with entitlement → `/paid-curriculum`.
  - Free track end without entitlement → `/paywall`.
  - `/paywall` with entitlement → shows continue CTA.
  - `/purchase/cancel` with entitlement → routes to `/paid-curriculum`.
