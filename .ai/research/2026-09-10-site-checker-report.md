# Site checker report — https://www.mynaani.com

**Date:** 2026-09-10  
**Target:** https://www.mynaani.com  
**API base:** https://noni-api-production.up.railway.app  
**Pages crawled:** 22  
**Browser:** Chromium (Playwright)

## Executive summary

| Severity | Count |
|----------|-------|
| P0 (broken) | 0 |
| P1 (major) | 2 |
| P2 (minor) | 0 |
| P3 (cosmetic / info) | 20 |

**Top findings (P1)**
- **P1** on `/for-communities`: one external research citation (`annualreviews.org`) returned HTTP 403 — likely bot/HEAD protection, not a dead link.
- **P1** on `/c/demo`: partner slug `demo` does not exist, so `GET /api/v1/org/by-slug/demo` returned HTTP 404. This is expected behavior for an unknown slug, not a production regression.

## Methodology

- Crawled `https://www.mynaani.com` with Chromium via Playwright, fresh browser context per route.
- Captured console logs, uncaught page errors, failed network requests, HTTP >= 400 responses, and external link status.
- Used the route table from `frontend/src/App.tsx` to seed the crawl list and to map each page to its component/source file.
- Auth-gated routes were visited without credentials to verify they redirect to `/signin?redirect=<route>`.
- Backend/API smoke checks hit `/health`, `/api/v1/auth/config`, and `/api/ui-envelope/landing.intro`.
- Full-page screenshots are saved to `.ai/research/site-checker-screenshots/` (not committed by default) and raw JSON data is in `.ai/research/2026-09-10-site-checker-data.json`.

## Interpretation / diagnosis

The site is structurally healthy. No P0 (broken) or P2 findings were detected. The two P1s are both likely false positives caused by test data / crawler behavior:

1. **`/for-communities` 403 link**: The `annualreviews.org` URL is a real research article. A 403 response to an automated HEAD/GET request typically means the publisher blocks non-browser traffic. A real user clicking the link in a browser would reach the article. Remediation: confirm in a real browser; consider adding `rel="noopener"` and a link-checker allow-list for academic publishers that rate-limit bots.
2. **`/c/demo` 404**: `/c/:slug` renders `PartnerPage`, which calls `GET /api/v1/org/by-slug/:slug`. `demo` is not a registered partner slug, so the 404 is the correct API contract. Remediation: if running automated partner-page checks, use a known, non-destructive partner slug or mock the API response.

All auth-gated routes redirected to `/signin?redirect=...` as intended by `App.tsx` `requireAuth` logic. Public routes loaded without console errors or uncaught exceptions.

## API / backend checks

| Name | URL | Result |
|------|-----|--------|
| health | https://noni-api-production.up.railway.app/health | HTTP 200 OK (application/json) |
| auth config | https://noni-api-production.up.railway.app/api/v1/auth/config | HTTP 200 OK (application/json) |
| landing intro envelope | https://noni-api-production.up.railway.app/api/ui-envelope/landing.intro | HTTP 200 OK (application/json) |

## Per-page findings

### / — Landing (public)
- **Component:** LandingPage (frontend/src/components/LandingPage.tsx)
- **Final URL:** https://www.mynaani.com/
- **Load time:** 1507 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, BUTTON, A, A)
- **Screenshot:** .ai/research/site-checker-screenshots/00-landing.png

### /signin — Sign in (public)
- **Component:** SignInPage (frontend/src/components/SignInPage.tsx)
- **Final URL:** https://www.mynaani.com/signin
- **Load time:** 1152 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/01-sign-in.png

### /for-communities — For Communities (B2B) (public)
- **Component:** ForCommunitiesPage (frontend/src/components/ForCommunitiesPage.tsx)
- **Final URL:** https://www.mynaani.com/for-communities
- **Load time:** 1165 ms
- **Severity:** P1
- **Status:** loaded
- **Dead external links:** `https://www.annualreviews.org/content/journals/10.1146/annurev-vision-111815-114550` -> 403
  - *Diagnosis:* likely publisher bot/HEAD protection; user-facing link is probably valid. Verify with a real browser click.
- **Interactive elements:** 21 (sample: A, A, A, A, A)
- **Screenshot:** .ai/research/site-checker-screenshots/02-for-communities-b2b-.png

### /privacy — Privacy (public)
- **Component:** PrivacyPage (frontend/src/components/PrivacyPage.tsx)
- **Final URL:** https://www.mynaani.com/privacy
- **Load time:** 1208 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, BUTTON, A, A)
- **Screenshot:** .ai/research/site-checker-screenshots/03-privacy.png

### /help — Help (public)
- **Component:** HelpPage (frontend/src/components/HelpPage.tsx)
- **Final URL:** https://www.mynaani.com/help
- **Load time:** 1119 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 10 (sample: A, BUTTON, A, A, A)
- **Screenshot:** .ai/research/site-checker-screenshots/04-help.png

### /admin — Admin console (public)
- **Component:** AdminConsolePage (frontend/src/components/AdminConsolePage.tsx)
- **Final URL:** https://www.mynaani.com/admin
- **Load time:** 1385 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, INPUT, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/05-admin-console.png

### /gift — Gift checkout (public)
- **Component:** GiftCheckoutPage (frontend/src/components/GiftCheckoutPage.tsx)
- **Final URL:** https://www.mynaani.com/gift
- **Load time:** 1307 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/06-gift-checkout.png

### /c/demo — Partner page (demo slug) (public)
- **Component:** PartnerPage (frontend/src/components/PartnerPage.tsx)
- **Final URL:** https://www.mynaani.com/c/demo
- **Load time:** 1274 ms
- **Severity:** P1
- **Status:** loaded
- **HTTP >= 400 responses:** `GET https://noni-api-production.up.railway.app/api/v1/org/by-slug/demo` -> 404
- **Console errors:** Failed to load resource: the server responded with a status of 404 ()
  - *Diagnosis:* `/c/:slug` is a partner landing page. `demo` is not a registered slug, so the backend correctly returns 404. This is expected; use a real partner slug for automated checks.
- **Interactive elements:** 1 (sample: A)
- **Screenshot:** .ai/research/site-checker-screenshots/07-partner-page-demo-slug-.png

### /purchase/success — Purchase success (public)
- **Component:** PurchaseSuccessPage (frontend/src/components/PurchaseSuccessPage.tsx)
- **Final URL:** https://www.mynaani.com/purchase/success
- **Load time:** 1152 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 3 (sample: A, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/08-purchase-success.png

### /purchase/cancel — Purchase cancel (public)
- **Component:** PurchaseCancelPage (frontend/src/components/PurchaseCancelPage.tsx)
- **Final URL:** https://www.mynaani.com/purchase/cancel
- **Load time:** 1163 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 3 (sample: A, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/09-purchase-cancel.png

### /welcome — Welcome (auth-gated) (auth-gated)
- **Component:** WelcomePage (frontend/src/components/WelcomePage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fwelcome
- **Load time:** 1144 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/10-welcome-auth-gated-.png

### /setup — Account setup (auth-gated) (auth-gated)
- **Component:** AccountSetupPage (frontend/src/components/AccountSetupPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fsetup
- **Load time:** 1272 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/11-account-setup-auth-gated-.png

### /getting-started — Getting started (auth-gated) (auth-gated)
- **Component:** GettingStartedPage (frontend/src/components/GettingStartedPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fgetting-started
- **Load time:** 1166 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/12-getting-started-auth-gated-.png

### /curriculum — Curriculum (auth-gated) (auth-gated)
- **Component:** CurriculumRenderer (frontend/src/components/CurriculumRenderer.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fcurriculum
- **Load time:** 1140 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/13-curriculum-auth-gated-.png

### /paid-curriculum — Paid curriculum (auth-gated) (auth-gated)
- **Component:** PaidLessonRenderer (frontend/src/components/PaidLessonRenderer.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fpaid-curriculum
- **Load time:** 1428 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/14-paid-curriculum-auth-gated-.png

### /menu — Curriculum menu (auth-gated) (auth-gated)
- **Component:** CurriculumMenu (frontend/src/components/CurriculumMenu.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fmenu
- **Load time:** 1226 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/15-curriculum-menu-auth-gated-.png

### /paywall — Paywall (auth-gated) (auth-gated)
- **Component:** PaywallPage (frontend/src/components/PaywallPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fpaywall
- **Load time:** 1181 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/16-paywall-auth-gated-.png

### /gift-redeem — Gift redeem (auth-gated) (auth-gated)
- **Component:** GiftRedeemPage (frontend/src/components/GiftRedeemPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fgift-redeem
- **Load time:** 1140 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/17-gift-redeem-auth-gated-.png

### /mock-checkout — Mock checkout (auth-gated) (auth-gated)
- **Component:** MockCheckoutPage (frontend/src/components/MockCheckoutPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Fmock-checkout
- **Load time:** 1202 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/18-mock-checkout-auth-gated-.png

### /account — Account settings (auth-gated) (auth-gated)
- **Component:** AccountSettingsPage (frontend/src/components/AccountSettingsPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Faccount
- **Load time:** 1133 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/19-account-settings-auth-gated-.png

### /org — Org dashboard (auth-gated) (auth-gated)
- **Component:** OrgDashboardPage (frontend/src/components/OrgDashboardPage.tsx)
- **Final URL:** https://www.mynaani.com/signin?redirect=%2Forg
- **Load time:** 1175 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 4 (sample: A, INPUT, BUTTON, BUTTON)
- **Screenshot:** .ai/research/site-checker-screenshots/20-org-dashboard-auth-gated-.png

### /auth/callback — Auth callback (public)
- **Component:** inline pending banner (frontend/src/App.tsx)
- **Final URL:** https://www.mynaani.com/auth/callback
- **Load time:** 1176 ms
- **Severity:** P3
- **Status:** loaded
- No findings
- **Interactive elements:** 1 (sample: A)
- **Screenshot:** .ai/research/site-checker-screenshots/21-auth-callback.png


## Code mapping table

| Page | Route | Component | Source file | Auth gate |
|------|-------|-----------|-------------|-----------|
| Landing | / | LandingPage | frontend/src/components/LandingPage.tsx | No |
| Sign in | /signin | SignInPage | frontend/src/components/SignInPage.tsx | No |
| For Communities (B2B) | /for-communities | ForCommunitiesPage | frontend/src/components/ForCommunitiesPage.tsx | No |
| Privacy | /privacy | PrivacyPage | frontend/src/components/PrivacyPage.tsx | No |
| Help | /help | HelpPage | frontend/src/components/HelpPage.tsx | No |
| Admin console | /admin | AdminConsolePage | frontend/src/components/AdminConsolePage.tsx | No |
| Gift checkout | /gift | GiftCheckoutPage | frontend/src/components/GiftCheckoutPage.tsx | No |
| Partner page (demo slug) | /c/demo | PartnerPage | frontend/src/components/PartnerPage.tsx | No |
| Purchase success | /purchase/success | PurchaseSuccessPage | frontend/src/components/PurchaseSuccessPage.tsx | No |
| Purchase cancel | /purchase/cancel | PurchaseCancelPage | frontend/src/components/PurchaseCancelPage.tsx | No |
| Welcome (auth-gated) | /welcome | WelcomePage | frontend/src/components/WelcomePage.tsx | RequireAuth |
| Account setup (auth-gated) | /setup | AccountSetupPage | frontend/src/components/AccountSetupPage.tsx | RequireAuth |
| Getting started (auth-gated) | /getting-started | GettingStartedPage | frontend/src/components/GettingStartedPage.tsx | RequireAuth |
| Curriculum (auth-gated) | /curriculum | CurriculumRenderer | frontend/src/components/CurriculumRenderer.tsx | RequireAuth |
| Paid curriculum (auth-gated) | /paid-curriculum | PaidLessonRenderer | frontend/src/components/PaidLessonRenderer.tsx | RequireAuth |
| Curriculum menu (auth-gated) | /menu | CurriculumMenu | frontend/src/components/CurriculumMenu.tsx | RequireAuth |
| Paywall (auth-gated) | /paywall | PaywallPage | frontend/src/components/PaywallPage.tsx | RequireAuth |
| Gift redeem (auth-gated) | /gift-redeem | GiftRedeemPage | frontend/src/components/GiftRedeemPage.tsx | RequireAuth |
| Mock checkout (auth-gated) | /mock-checkout | MockCheckoutPage | frontend/src/components/MockCheckoutPage.tsx | RequireAuth |
| Account settings (auth-gated) | /account | AccountSettingsPage | frontend/src/components/AccountSettingsPage.tsx | RequireAuth |
| Org dashboard (auth-gated) | /org | OrgDashboardPage | frontend/src/components/OrgDashboardPage.tsx | RequireAuth |
| Auth callback | /auth/callback | inline pending banner | frontend/src/App.tsx | No |

## Recommended next steps

1. Review any P0/P1 findings above for real regressions.
2. Confirm auth-gated routes redirect to /signin with a ?redirect= param (per App.tsx logic).
3. Verify external links flagged as dead are truly dead or were rate-limited during crawl.
4. Add the site-checker run to CI against the staging preview URL on a schedule.
