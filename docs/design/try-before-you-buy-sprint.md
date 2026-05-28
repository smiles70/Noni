# Sprint Plan — Try Before You Buy (Freemium Preview)

**Date conceived:** 2026-05-27  
**Status:** Researched, planned, not implemented.  
**Authority:** `docs/library/CONTRACT.md` (P1), ADR 0019, ADR 0006.  
**Predecessor:** `docs/design/cta-hero-reading-sprint-2026-05-27.md` (landed and verified).  
**Scope:** Allow prospective users to experience Module 0, Units 1–3 without any authentication, then gate Unit 4+ behind a free account creation.

---

## 1. Why This Sprint Exists

### Current State (Post-CTA Hero Reading Sprint)

The landing page now presents a clean 2-button hero:
- "Set up my account — free" (primary CTA) → opens HowItWorksDialog → Clerk sign-in → curriculum
- "Log in" (secondary CTA) → Clerk sign-in → curriculum

This is a **significant improvement** over the previous 3-button design. However, per the geragogy research and SaaS onboarding best practices documented below, it still violates the #1 onboarding mistake: asking users to authenticate before they have experienced any value.

### The Core Problem

The HowItWorksDialog is **explanatory** (reading about Noni) rather than **experiential** (actually doing a lesson). Digital Scientists' research on older adult learners explicitly found that older adults learn better by *manipulating* a product than by reading about it. The Nintendo Wii onboarding was cited as the gold standard because it lets users interact immediately.

### Research Evidence

| Source | Key Finding | Implication for Noni |
|--------|-------------|----------------------|
| **Gleap** — "SaaS User Onboarding: The Complete Guide" | "Mistake #1: Asking users to set up before they see value. Solution: remove friction... Cognitive load is the enemy of activation." | Users should do a lesson before seeing an auth wall |
| **Digital Scientists** — "Onboarding Elderly Users" | "Older adults learn by manipulating a product, not reading about it. The Nintendo Wii succeeds because users interact immediately." | A preview lesson is more effective than an explanation dialog |
| **ProductLed** — "SaaS Onboarding Best Practices" | "The ultimate motivation is to show users how the product can help improve their lives." | Users must *experience* calm, paced learning firsthand |
| **NN/G Trust** — "Trust or Bust" | "Up-front disclosure of all aspects... Reveal costs immediately." | "First 3 lessons free, no account needed" builds trust |
| **Industry Data** (Mixpanel/Amplitude) | Freemium/trial models convert 25–40% better than "signup first" | Preview → signup outperforms explain → signup |
| **Nintendo Wii (Gold Standard)** | Immediate interaction, no manual reading | Unit 1 loads in <2 seconds, user is doing, not reading |

### What Senior Planet / OATS (AARP) Does

Senior Planet, the gold standard for older adult tech education, uses:
- Free in-person classes with no account required
- Immediate hands-on interaction with devices
- Human instructors who demonstrate first, then let learners try
- Clear "what you'll learn in this session" framing
- No credit card, no commitment language

Noni's current dialog-based approach is closer to a product brochure than a Senior Planet class.

---

## 2. User Flow — Proposed Architecture

### Current Flow (After CTA Hero Reading Sprint)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LANDING PAGE (2 buttons)                         │
│  "Set up my account — free"  →  HowItWorksDialog  →  Clerk  →  🎓  │
│  "Log in"                    →  Clerk  →  🎓                        │
└─────────────────────────────────────────────────────────────────────┘

User experience: READ about Noni → SIGN UP → LEARN
```

### Proposed Flow: "Freemium Preview" Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LANDING PAGE (3 buttons, clear hierarchy)         │
│  "Try a free lesson" (primary)   →  Module 0, Unit 1 (no auth)    │
│  "Set up my account" (secondary) →  HowItWorksDialog → Clerk → 🎓  │
│  "Log in" (tertiary)             →  Clerk → 🎓                    │
└───────────────────────┬───────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              MODULE 0, UNITS 1–3 (NO AUTH REQUIRED)                 │
│                                                                      │
│  • Lesson loads immediately in calm, paced format                  │
│  • No popup, no "create account" interruption                      │
│  • User experiences actual product: pacing, voice, simplicity       │
│  • "Next lesson" navigation flows to Unit 2, then Unit 3          │
│  • Progress saved in localStorage (no backend call)                 │
│                                                                      │
│  Visual cue: "Lesson 1 of 6 — Free preview" (subtle indicator)    │
└───────────────────────┬───────────────────────────────────────────────┘
                        │
              Units 2 → 3 (still free, no auth, seamless)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              ATTEMPT UNIT 4 → AUTH GATE SCREEN                        │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  "Great job finishing Lesson 3!"                            │    │
│  │                                                             │    │
│  │  "You're learning fast. Create your free account to         │    │
│  │   continue with Lesson 4 and unlock the rest of Module 0." │    │
│  │                                                             │    │
│  │  "Free. No card needed. Stop any time."                     │    │
│  │                                                             │    │
│  │  [Continue with free account]  ←  primary action              │    │
│  │  [Back to landing page]        ←  secondary action          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Psychological triggers in play:                                     │
│  • Reciprocity: user received 3 free lessons → more willing to give  │
│  • Loss aversion: "I don't want to lose my progress"               │
│  • Investment: 3 units of time invested → sunk cost effect         │
│  • Aha moment: user now *understands* what Noni feels like         │
└───────────────────────┬───────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CLERK SIGN-IN → CURRICULUM (continues at Unit 4)      │
│                                                                      │
│  • Picks up exactly where user left off (Unit 4, no progress lost) │
│  • All 6 units of Module 0 now accessible                          │
│  • Modules 1–3 also free (existing behavior)                       │
│  • Backend syncs localStorage preview progress to user account       │
└─────────────────────────────────────────────────────────────────────┘
```

### Why "Halfway Through Module 0" (After Unit 3)

- **6 units total** → Unit 4 is the exact midpoint
- **Psychological commitment**: 3 units = "I've invested time, I want to finish"
- **Reciprocity principle**: User received value (3 free lessons) → more willing to give value (create account)
- **Aha moment timing**: By Unit 3, user has experienced the calm pacing, plain language, and lesson format — they *understand* the product
- **Loss aversion**: "I don't want to lose my progress" is a stronger motivator than "I want to start"
- **Industry standard**: Most SaaS freemium tiers gate at the point where users have experienced core value but want more

---

## 3. Sprint Inventory

| # | Item | Contract Anchor | Files Touched | Status |
|---|------|----------------|---------------|--------|
| **F1** | Make `GET /api/curriculum/module/0/units` public (no JWT for read) | CONTRACT §IV.A (backend-approved envelopes) | `backend/api/routes/curriculum.py` | Planned |
| **F2** | Make `GET /api/curriculum/module/0/unit/{id}` public for units 1–3 | CONTRACT §IV.A | `backend/api/routes/curriculum.py` | Planned |
| **F3** | Return structured `403` for units 4+ with "auth required" message | CONTRACT §III (state transparency) | `backend/api/routes/curriculum.py` | Planned |
| **F4** | Add `PREVIEW` UI state envelope (or reuse `landing.page`) | CONTRACT §IV.A (explicit state identifier) | `backend/models/ui_state_envelope.py` | Planned |
| **F5** | Add `goPreview()` view state in `App.tsx` | CONTRACT §IV (React governance) | `frontend/src/App.tsx` | Planned |
| **F6** | Add `"Try a free lesson"` button to landing page | CONTRACT §I.F (≤5 primary actions) | `frontend/src/components/LandingPage.tsx` | Planned |
| **F7** | Create `PreviewLessonRenderer` or extend `LessonRenderer` | CONTRACT §I.D (authorized components) | `frontend/src/components/` | Planned |
| **F8** | LocalStorage preview progress tracking | No contract violation (client-side only) | `frontend/src/` | Planned |
| **F9** | Auth gate screen at Unit 4 with "Continue with free account" CTA | CONTRACT §III (confirmation for state changes) | `frontend/src/components/PaywallPage.tsx` or new | Planned |
| **F10** | Backend sync: migrate localStorage progress to user account on signup | CONTRACT §III (state transparency) | `frontend/src/api/`, backend | Planned |
| **F11** | Update `LandingPage` RenderGuard proposal for 3-button layout | CONTRACT §IV.B (RenderGuard accounting) | `frontend/src/components/LandingPage.tsx` | Planned |
| **F12** | Add "Lesson X of Y — Free preview" indicator to preview mode | CONTRACT §I.D (Indicator component) | `frontend/src/components/` | Planned |
| **F13** | Regression test: verify auth flow still works for direct signup | CONTRACT §III (reversibility) | All auth paths | Planned |
| **F14** | Regression test: verify existing curriculum flow unchanged | CONTRACT §IV (React governance) | `frontend/src/App.tsx` | Planned |

---

## 4. Technical Implementation Options

### Option A: Public Preview Endpoint (Recommended)

**Approach:** Backend allows unauthenticated read access to Module 0, Units 1–3. Backend returns `403` with structured message for Units 4+.

**Backend changes:**
```python
# backend/api/routes/curriculum.py
# Current: @router.get("/module/{module_id}/units") requires JWT
# New: Allow public read for module_id=0

@router.get("/module/{module_id}/units")
async def get_module_units(module_id: int, request: Request):
    if module_id != 0:
        # Existing auth check
        user = await require_auth(request)
    # For module_id == 0, return units without auth
    # But still gate unit content for units 4+
```

**Frontend changes:**
- New `loadPreviewUnit(moduleId, unitId)` API function (no auth headers)
- New `PreviewLessonRenderer` that calls public API
- Auth gate intercepts attempt to load Unit 4, shows paywall

**Pros:**
- No content duplication
- Backend remains single source of truth
- Scales to future "free preview" modules
- LocalStorage progress can be synced to backend after signup

**Cons:**
- Requires backend auth architecture changes
- More files touched
- Requires backend deploy + frontend deploy coordination

### Option B: Static Preview (Faster, Riskier)

**Approach:** Hardcode Module 0, Units 1–3 content into frontend bundle as static JSON.

**Backend changes:** None.

**Frontend changes:**
```typescript
// frontend/src/data/preview_module_0.ts
export const PREVIEW_MODULE_0 = {
  moduleId: 0,
  units: [
    { id: 1, title: "...", content: "..." },
    { id: 2, title: "...", content: "..." },
    { id: 3, title: "...", content: "..." },
  ]
};
```

**Pros:**
- Zero backend changes
- Deploys faster (frontend only)
- Works even if backend is down

**Cons:**
- Content drift risk (backend vs. frontend copy)
- Duplicate source of truth — violates DRY
- Harder to maintain (every content update requires frontend redeploy)
- Violates CONTRACT §IV.A (React should render backend-approved envelopes)
- Static content cannot adapt per-user (though preview is anonymous, so this is minor)

### Decision: Option A

Option B violates the contract's principle that React should render backend-approved envelopes. Option A is the correct architectural choice despite requiring backend changes.

---

## 5. Geragogy Contract Compliance Analysis

### Current Landing Page (Post-CTA Hero Reading) — Grade: A (93%)

See full grading in `docs/design/cta-hero-reading-sprint-2026-05-27.md` Section 5 or the conversation transcript from 2026-05-27. Summary:

| Section | Score | Key Finding |
|---------|-------|-------------|
| I.A Color | A+ | Full compliance |
| I.B Geometry | A+ | Full compliance |
| I.C Typography | A | Verify heading ratio ≤1.4× |
| I.D Components | B+ | Pre-existing NavBar not in V1 inventory |
| I.E Iconography | A+ | Full compliance |
| I.F Density | A+ | Improved from 5→4 |
| I.G Motion | A+ | Full compliance |
| II Accessibility | A+ | Full compliance |
| III Failure Handling | A+ | Full compliance |
| IV React Governance | A+ | Full compliance |
| V AI Self-Check | A | 2 minor verifications |
| VII Objective | A+ | Full compliance |

### Proposed Preview Mode — Estimated Grade: A (92%)

| Section | Projected Score | Risk |
|---------|-----------------|------|
| I.A Color | A+ | No color changes needed |
| I.B Geometry | A+ | Lesson renderer already compliant |
| I.C Typography | A+ | No typography changes needed |
| I.D Components | B+ | NavBar still pre-existing gap; PreviewLessonRenderer must use authorized components only |
| I.E Iconography | A+ | No icons needed |
| I.F Density | A | 3 buttons on landing pushes density to limit (but ≤5 is still compliant) |
| I.G Motion | A+ | No new motion |
| II Accessibility | A+ | Focus handling already in dialog/renderer |
| III Failure Handling | A+ | Auth gate is clear state change, not an error |
| IV React Governance | A | New `PREVIEW` state needs backend envelope |
| V AI Self-Check | A | Need to verify all 10 checks |
| VII Objective | A+ | Improved dignity (users try before committing) |

**Net effect on contract:** Slightly improves cognitive load containment (users learn by doing, not reading), but increases landing page density from 2→3 buttons. Still within ≤5 limit.

---

## 6. Comparison: Noni vs. Senior-Focused Best Practices

### Current State Analysis (from 2026-05-27 conversation)

| Dimension | Senior Planet (OATS/AARP) | Noni Current | Noni Proposed |
|-----------|---------------------------|--------------|---------------|
| **First impression** | Large "Programs" menu with categories | Clean hero, but requires click to understand | "Try a free lesson" lets users experience immediately |
| **Trust building** | Physical locations, instructor photos | Reassurance text is good; lacks human faces | Same, but experiential trust > textual trust |
| **Interaction before commitment** | Free in-person classes, no account | Explanation dialog before auth | Actual hands-on lesson before auth |
| **Pacing** | Class schedules, clear time commitments | "Stop any time" is good | Lesson duration gives concrete time sense |
| **Support visibility** | "Need help?" prominent | Help not visible on landing | Same gap; should add |
| **Try before buy** | Walk in, sit down, start learning | Read about it, then sign up | Do a lesson, then sign up |

---

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Backend auth changes break existing curriculum flow | Medium | High | F13/F14 regression tests mandatory; maintain existing JWT-required paths for all other modules |
| Public endpoint exposes unintended data | Low | High | Strict module_id==0 check; return 403 for all other modules |
| LocalStorage progress lost on signup | Medium | Medium | F10: sync localStorage to backend on account creation |
| Content drift (backend vs. preview) | Low (Option A) / High (Option B) | Medium | Option A eliminates this risk |
| Landing page density at limit (3 buttons) | Certain | Low | ≤5 is compliant; clear visual hierarchy (primary/secondary/tertiary) |
| User confusion: "Why can't I continue Lesson 4?" | Medium | Low | Clear auth gate screen with explanation, not an error |
| Preview users never convert to accounts | Unknown | Medium | A/B test conversion rate; can adjust gate point (Unit 3 vs. Unit 4 vs. Unit 5) |
| Backend deploy + frontend deploy coordination | Medium | Medium | Deploy backend first, then frontend; backend change is backward-compatible |

---

## 8. Open Questions for Future Sprint Kickoff

1. **Gate point**: Is Unit 4 the right place, or should it be Unit 3 or Unit 5? Needs user testing.
2. **Button hierarchy**: How to visually distinguish "Try a free lesson" (primary), "Set up my account" (secondary), and "Log in" (tertiary) without violating color rules?
3. **Progress persistence**: How long does localStorage preview progress persist? Should it expire?
4. **Backend sync strategy**: On signup, should we auto-advance to Unit 4, or let user choose to restart Module 0?
5. **Analytics**: How do we measure preview → signup conversion without violating privacy principles?
6. **Paywall screen copy**: What exact phrasing maximizes conversion while maintaining dignity and non-urgency?
7. **NavBar gap**: Should we resolve the pre-existing NavBar component inventory issue first (requires ADR)?
8. **Heading ratio verification**: What is the actual computed `headingScale.level1` value in pixels?

---

## 9. Acceptance Criteria (When Sprint Is Executed)

- [ ] Signed-out user sees 3 buttons on landing page with clear hierarchy
- [ ] Clicking "Try a free lesson" opens Module 0, Unit 1 without any auth wall
- [ ] Units 2 and 3 are accessible without auth (seamless navigation)
- [ ] Attempting Unit 4 shows a clear, calm auth gate screen (not an error)
- [ ] Auth gate screen says "Create your free account to continue" with reassurance copy
- [ ] Clicking "Continue with free account" goes to Clerk sign-in → curriculum at Unit 4
- [ ] LocalStorage preserves preview progress across sessions
- [ ] After signup, backend syncs preview progress to user account
- [ ] Existing auth flow (direct "Set up my account" → Clerk) still works
- [ ] Existing curriculum flow for signed-in users unchanged
- [ ] No RenderGuard violations on any page
- [ ] No console errors or warnings
- [ ] `npm run type-check` passes
- [ ] `npm run build` succeeds
- [ ] Deployed to Cloudflare Pages with correct `VITE_API_BASE_URL`

---

## 10. Cross-References

- `docs/library/CONTRACT.md` — §I.A–I.G, §III, §IV, §V, §VII
- `docs/design/cta-hero-reading-sprint-2026-05-27.md` — predecessor sprint, current landing page state
- `docs/decisions/0019-closed-world-design-contract.md` — contract authority
- `docs/decisions/0024-auth-provider-selection.md` — Clerk integration model
- `frontend/src/components/LandingPage.tsx` — current landing page implementation
- `frontend/src/components/LessonRenderer.tsx` — lesson rendering component
- `frontend/src/App.tsx` — view state machine
- `backend/models/ui_state_envelope.py` — backend envelope definitions
- `backend/api/routes/curriculum.py` — curriculum API routes

---

## 11. Conversation Context

This sprint plan was developed during a coding session on 2026-05-27. The session sequence was:

1. Completed and deployed the **CTA Hero Reading Sprint** (reduce landing page from 3 buttons to 2, move explanation to primary CTA flow).
2. Verified build (`npm run type-check`, `npm run build`) and deployed to Cloudflare Pages.
3. User requested a comparison of the landing page against other senior-focused sites.
4. Analysis identified the remaining gap: users still don't *experience* Noni before auth.
5. User asked: "how can we do that, with module 0 limit at the half way point?"
6. This document captures the research, architecture, and planning for that future sprint.

---

*Generated 2026-05-27. Not yet implemented. Execute only with explicit approval and a fresh 1440-degree regression check.*
