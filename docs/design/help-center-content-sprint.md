# Sprint Plan — Help Center Content

**Date opened:** 2026-05-28
**Status:** In progress
**Authority:** `docs/library/CONTRACT.md` (P1)
**Scope:** Four geragogy-compliant help articles + in-app help page + navigation wiring

---

## 1. Why This Sprint Exists

Noni currently surfaces a single `mailto:hello@mynaani.com` link as its entire support surface. Competitor analysis of Duolingo, Coursera, Khan Academy, Codecademy, Skillshare, MasterClass, Mimo, and Elements of AI shows an average of 6 major help categories and ~80 self-service articles. Noni has zero.

This sprint adds the minimum viable help surface: four articles covering authentication, curriculum, payments, and account management — the four areas where users are most likely to need guidance.

---

## 2. Articles to Write

| # | Article | User Flow Coverage | Backend Routes Referenced |
|---|---------|-------------------|---------------------------|
| 1 | **Getting Started with Mynaani** | Landing → HowItWorksDialog → Auth → First Session | `/auth/config`, `/auth/session`, `/auth/session/init` |
| 2 | **How Mynaani Works** | Curriculum navigation, page types, progress, resuming | Curriculum routes, `readProgress`/`writeProgress` |
| 3 | **Payments and Gifts** | Paywall, self-purchase, gift purchase, redemption, refunds | `/api/billing/*`, `/api/gifts/*` |
| 4 | **Your Account and Support** | Sign out, deletion, security, browser requirements, contact | `/me/delete`, `/me/delete/cancel` |

---

## 3. Geragogy Contract Compliance Checklist (Per Article)

- [ ] Zero exclamation marks
- [ ] No urgency language ("act now," "don't miss out")
- [ ] No condescension ("simply," "just," "don't worry")
- [ ] No inference about user readiness, mastery, or confidence
- [ ] Technical terms explained in plain language on first use
- [ ] Short paragraphs (2–3 sentences max)
- [ ] Reversible actions clearly marked
- [ ] Dignity-preserving tone throughout

---

## 4. Blueprint — Where Articles Land in the App

### 4.1 New Route/View

**`"help"`** added to `View` union type in `App.tsx`

- Renders `<HelpPage>` component
- Public view (does not require auth)
- Accessible from landing page and from inside the curriculum

### 4.2 Navigation Entry Points

| Location | Link Text | Destination | Rationale |
|----------|-----------|-------------|-----------|
| `LandingPage.tsx` (below contact email) | "Help and common questions" | `setView("help")` | Unsigned users need help before auth |
| `NavBar.tsx` (signed-out state) | "Help" | `setView("help")` | Persistent access from any public view |
| `NavBar.tsx` (signed-in state) | "Help" | `setView("help")` | Persistent access from any gated view |
| `AuthBlockedNotice.tsx` | "See help for common sign-in issues" | `setView("help")` | Redirect blocked users to self-service |
| `PaywallPage.tsx` (footer) | "Questions about buying or gifting?" | `setView("help")` | Pre-purchase reassurance |
| `GiftRedeemPage.tsx` (footer) | "Questions about gift tokens?" | `setView("help")` | Redemption guidance |
| `AccountSettingsPage.tsx` (footer) | "Account help" | `setView("help")` | Post-action support |

### 4.3 Section Navigation Inside HelpPage

The `HelpPage` component renders four `<section>` elements, each with an `id` attribute:

- `#getting-started`
- `#how-it-works`
- `#payments-gifts`
- `#your-account`

A sticky table of contents at the top of the page links to each section via anchor navigation. No routing changes needed — all four articles live in one component.

---

## 5. Component Structure

```
frontend/src/components/HelpPage.tsx
  ├── HelpPage (root)
  ├── SectionNav (table of contents)
  ├── GettingStartedSection (article 1)
  ├── HowItWorksSection (article 2)
  ├── PaymentsGiftsSection (article 3)
  └── YourAccountSection (article 4)
```

All sections use `AccountStyles.ts` primitives (`PAGE`, `H1`, `H2`, `BODY`, `STACK`, `DIVIDER`) for visual consistency with existing account/billing pages.

---

## 6. Files to Modify

| File | Change |
|------|--------|
| `frontend/src/App.tsx` | Add `"help"` to `View` union; add `case "help":` to switch; add `goHelp` callback |
| `frontend/src/components/NavBar.tsx` | Add `onHelp` prop; render "Help" button in both signed-in and signed-out states |
| `frontend/src/components/LandingPage.tsx` | Add help link below contact email paragraph |
| `frontend/src/components/AuthBlockedNotice.tsx` | Add help link to sign-in error copy |
| `frontend/src/components/PaywallPage.tsx` | Add help link in footer area |
| `frontend/src/components/GiftRedeemPage.tsx` | Add help link in footer area |
| `frontend/src/components/AccountSettingsPage.tsx` | Add help link in footer area |

---

## 7. Acceptance Criteria

- [ ] All four articles committed to `HelpPage.tsx`
- [ ] Zero exclamation marks across all articles (verified by grep)
- [ ] All user-facing references use "mynaani" (verified by grep)
- [ ] Help page reachable from landing, NavBar, AuthBlockedNotice, Paywall, GiftRedeem, AccountSettings
- [ ] Help page is public (no auth required)
- [ ] Table of contents navigates to each section
- [ ] Visual style matches existing account/billing pages (tokens only, no hardcoded values)
- [ ] RenderGuard proposal documents `primaryActionCount = 1` (the back/close button)

---

## 8. Out of Scope

- Searchable knowledge base (future sprint)
- Multi-page routing for individual articles (future sprint)
- Community forum or chat support (future sprint)
- Analytics on which articles are read most (future sprint)
