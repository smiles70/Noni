# Sprint Plan — CTA Hero Reading

**Date opened:** 2026-05-27  
**Status:** Implemented. Pending verification.  
**Authority:** `docs/library/CONTRACT.md` (P1), ADR 0019.  
**Predecessor:** `docs/design/frontend-auth-geragogy-sprint-2026-05-18.md`

---

## 1. Why this sprint exists

The landing page presented three primary actions to new visitors:
1. "See how Noni works" (overlay on hero image)
2. "Set up my account — free" (primary CTA)
3. "Log in" (secondary CTA)

Per Hick's Law and geragogy research (Toptal, Digital Scientists, NN/G), three choices
increase decision time and cognitive load for older adult learners. The overlay button
also competed for visual attention against the primary CTA.

The bigger problem: "Set up my account — free" immediately hit the Clerk auth wall.
Per Gleap's SaaS onboarding research (Mistake #1), asking users to authenticate
before they understand the product is the #1 onboarding mistake.

**Goal:** Reduce landing page to 2 buttons and make the "How Noni works" explanation
the mandatory first step before the auth wall.

---

## 2. Architecture changes

### Before (3 buttons on landing)

```
LandingPage.tsx
├── Hero overlay
│   ├── Headline
│   └── "See how Noni works" button ──► HowItWorksDialog (optional)
├── Auth row
│   ├── "Set up my account — free" ──► goCurriculum() ──► Clerk sign-in
│   └── "Log in" ──► goSignIn() ──► Clerk sign-in
└── NavBar

Proposal: primaryActionCount = 5
```

### After (2 buttons on landing)

```
LandingPage.tsx
├── Hero overlay
│   └── Headline (no overlay button)
├── Auth row
│   ├── "Set up my account — free" ──► HowItWorksDialog (mandatory)
│   │                                      └── "Continue to my account"
│   │                                              └── onBegin() ──► Clerk
│   └── "Log in" ──► goSignIn() ──► Clerk sign-in
└── NavBar

Proposal: primaryActionCount = 4
```

---

## 3. Sprint inventory

| # | Item | Contract anchor | Files touched | Lines | Status |
|---|------|----------------|---------------|-------|--------|
| H1 | Remove overlay "See how Noni works" button | Hick's Law; CONTRACT §I.F ≤5 primary actions | `LandingPage.tsx` | 222-228 | Done |
| H2 | Wire signed-out primary CTA to open dialog | Gleap FTUX #1; NN/G trust up-front | `LandingPage.tsx` | 250-251 | Done |
| H3 | Add `onBegin` prop to `HowItWorksDialog` | CONTRACT §I.D component inventory | `HowItWorksDialog.tsx` | 23-28 | Done |
| H4 | Change dialog footer to "Continue to my account" | CONTRACT §III reversibility | `HowItWorksDialog.tsx` | 220-237 | Done |
| H5 | Preserve direct flow for signed-in users | Geragogy respect for existing users | `LandingPage.tsx` | 242-249 | Verified untouched |
| H6 | Update proposal `primaryActionCount` | CONTRACT §IV.B RenderGuard | `LandingPage.tsx` | 168 | Done |
| H7 | Update stale comments | Code hygiene | `LandingPage.tsx` | 129-133, 159-164, 286-288 | Done |

---

## 4. Research backing

### Expert sources consulted (10+)

1. **Toptal** — "Interface Design for Older Adults"
   > "Gradually introducing product characteristics—progressive disclosure and minimalist design—can help prevent cognitive overload from slower mental processing speeds in older adults."

2. **Digital Scientists** — "Onboarding Elderly Users: 5 Quick Tips"
   > "Keep your copy large, concise and easy to scan... Older adults like interacting with a product directly... manipulating a product helps them recall functions more easily."

3. **UserPilot** — "First Time User Experience (FTUE) For SaaS"
   > "Break the onboarding process into easy steps... Keep your microcopy conversational and inviting."

4. **UXPin** — "Progressive Disclosure in UX"
   > "Progressive disclosure is ideal for onboarding flows, where in-app tutorials introduce features incrementally rather than overwhelming new users."

5. **ProductLed** — "SaaS Onboarding Best Practices"
   > "The ultimate motivation is to show users how the product can help improve their lives. Every word in the onboarding experience is an opportunity to speak to users' needs and desires."

6. **Gleap** — "SaaS User Onboarding: The Complete Guide"
   > "Mistake #1: Asking users to set up before they see value. Solution: remove friction... Cognitive load is the enemy of activation."

7. **Laws of UX** — "Hick's Law"
   > "Minimize choices when response times are critical to decrease decision time... Avoid overwhelming users by highlighting recommended options."

8. **Nielsen Norman Group** — "4 Principles to Reduce Cognitive Load"
   > "Progressive disclosure solves this problem by presenting only what's needed at each step of the process."

9. **Nielsen Norman Group** — "Trust or Bust: Communicating Trustworthiness"
   > "Up-front disclosure of all aspects of the customer relationship... Reveal [costs] immediately rather than waiting until after the user has placed an order."

10. **Nielsen Norman Group** — "Few Guesses, More Success"
    > "Start with less sensitive information before requesting more personal details."

---

## 5. Verification checklist

- [x] `npm run type-check` passes (zero errors) — 2026-05-27
- [x] `npm run build` succeeds — 2026-05-27
- [x] Deployed to Cloudflare Pages — `https://5bbbf43f.noni-web.pages.dev` — 2026-05-27
- [ ] Manual: Signed-out user sees exactly 2 buttons on landing page
- [ ] Manual: Clicking "Set up my account — free" opens HowItWorksDialog
- [ ] Manual: Dialog shows "Continue to my account — free" footer button
- [ ] Manual: Clicking "Continue" proceeds to Clerk sign-in → curriculum
- [ ] Manual: Clicking "Close" / backdrop / Escape returns to landing without auth
- [ ] Manual: Signed-in user clicking "Continue learning →" bypasses dialog entirely
- [ ] No RenderGuard violations on landing page
- [ ] No console errors or warnings

---

## 6. Commit

```
feat: move How Noni works explanation to primary CTA

- Remove overlay "See how Noni works" button from hero
- Wire signed-out primary CTA to open HowItWorksDialog
- Add onBegin prop to HowItWorksDialog
- Change dialog footer from "Got it" to "Continue to my account — free"
- Update RenderGuard proposal primaryActionCount 5 → 4
- Preserve signed-in direct flow to curriculum
- Update stale comments
```

---

## 7. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Dialog `onClose` called after `onBegin` on unmount | Low | None | React 18 ignores state updates on unmount |
| CSS `.noni-hero__overlay-btn` unused | Certain | None | Dead CSS, no runtime impact |
| Proposal count conservative | Certain | None | Actual max = 3, proposal = 4 |
| Future caller omits `onBegin` | Low | Low | Optional prop falls back to "Got it" |

---

## 8. Out of scope

- Changing dialog content (copy, sections, images)
- Backend API changes (`/api/landing/page`, envelopes)
- `App.tsx` routing logic
- `AuthProvider` behavior
- `NavBar` changes
- CSS cleanup of unused `.noni-hero__overlay-btn` class

---

*Generated 2026-05-27. Cross-references: CONTRACT.md §I.F, §I.D, §III, §IV.B; ADR 0019; docs/design/frontend-auth-geragogy-sprint-2026-05-18.md.*
