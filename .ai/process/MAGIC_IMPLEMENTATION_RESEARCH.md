# Magic.link Implementation Research — Issues, Edge Cases, Best-in-Class Execution

**Process:** v9.51 (provenance-aware research artifact)
**Date:** 2026-08-27
**Scope:** Magic.link SDK integration for Vite React + FastAPI
**Source intake:** `.ai/intake/2026-08-27-magic-link-auth.md`
**ADR:** `docs/decisions/0027-magic-link-auth.md`

---

## 1. External sources

1. **Magic Docs — FAQ / Session management** — `https://docs.magic.link/home/faq`  
2. **Magic Docs — Server-side Node DID validation** — `https://docs.magic.link/embedded-wallets/sdk/server-side/node`  
3. **Magic Docs — Server-side Python SDK** — `https://docs.magic.link/embedded-wallets/sdk/server-side/python`  
4. **Magic Docs — Magic links login** — `https://docs.magic.link/embedded-wallets/authentication/login/magic-links`  
5. **Magic Docs — Rate limits** — `https://docs.magic.link/embedded-wallets/sdk/resources/rate-limit`  
6. **Magic Pricing** — `https://magic.link/pricing`  
7. **Stack Overflow — Magic link auth issue in React** — `https://stackoverflow.com/questions/73255425`  
8. **Stack Overflow — Magic Connect vs Magic Auth** — `https://stackoverflow.com/questions/75885046`  
9. **GitHub — magic-js issue #165 (random logout)** — `https://github.com/magiclabs/magic-js/issues/165`  
10. **Magic secure auth guide** — `https://magic.link/posts/secure-auth-on-client-and-server-guide`  

---

## 2. Core facts from source

- **DID token lifetime:** The token returned from `loginWithMagicLink` defaults to **15 minutes**. It is an authentication proof, not a session token.
- **Magic session lifetime:** By default the Magic SDK keeps the user logged in for **up to 7 days** (browser/cookie state). Auto-refresh can extend to **90 days** from the dashboard.
- **DID token is not invalidated on logout:** A previously generated DID token is only invalidated by expiry. The 15-minute lifetime is the mitigation, not server-side revocation.
- **Rate limit:** Default **500 requests/minute** per app. Excess returns HTTP `429`.
- **Pricing:** Free/Developer tier covers up to **1,000 Monthly Active Wallets (MAW)**; overage ~$0.045/MAW; Startup tier $99/mo for 2,500 MAW.
- **Error taxonomy (Python `magic-admin`):** `DIDTokenExpired`, `DIDTokenInvalid`, `DIDTokenMalformed`, `ExpectedBearerStringError`, `RateLimitingError`, `APIConnectionError`.
- **Wrong app type:** Creating a "Magic Connect" app instead of "Magic Auth" causes `Magic RPC Error: -32603 Unsupported Magic Connect method`.

---

## 3. Implementation issues

### 3.1 Session vs DID token confusion
**Issue:** Frontend and backend may treat the 15-minute DID as a long session token.  
**Impact:** Users appear "logged in" for 7 days in Magic, but the DID token used for API calls expires after 15 minutes.  
**Mitigation:** On the backend, validate the DID for each request. On the frontend, refresh the DID with `magic.user.getIdToken({ lifespan: 15 * 60 })` before a request if it is close to expiry, but only after explicit user action or a background ping. For Mynaani, prefer a short expiry and a calm re-auth prompt rather than silent auto-refresh.

### 3.2 DID token not invalidated by logout
**Issue:** Even after sign-out, a stolen DID token remains valid until expiry.  
**Impact:** Short window (15 min) but non-zero replay risk.  
**Mitigation:** Keep 15-minute lifetime; use short-lived tokens; do not accept tokens older than issued-at (`iat`) with a small leeway; clear client storage on sign-out; backend should not cache the DID as a session token.

### 3.3 Magic Connect vs Magic Auth key mismatch
**Issue:** Using a Magic Connect publishable key with `magic-sdk` auth methods throws `RPC Error: -32603`.  
**Impact:** Complete sign-in failure; hard-to-interpret error.  
**Mitigation:** Create an explicit "Magic Auth" app in the dashboard, not a Magic Connect / wallet app. Document this in `docs/ops/integrations-setup.md`.

### 3.4 Email deliverability
**Issue:** Magic sends the link; spam/junk folders, slow providers, or user mistakes can delay or block it.  
**Impact:** Older adults may not find the email or trust the sender.  
**Mitigation:** Add a "Didn't get it?" resend with rate limiting; keep a support fallback; consider whitelabel / custom domain in a future ADR.

### 3.5 Rate limits on login
**Issue:** 500 requests/minute per app. Repeated testing or a small spike can trigger `429`.  
**Impact:** E2E and load tests may fail; production users may be locked out during a traffic spike.  
**Mitigation:** Mock the provider in E2E tests; add backend `429` -> `auth.transient_verifier_unavailable` classification; alert on rate-limit telemetry.

### 3.6 Test mode caveats
**Issue:** Magic Test Mode (via `testMode: true`) allows `test+success@magic.link` etc., but test users are **not secure** and should not be treated as production data.  
**Impact:** Contaminated production telemetry or accidental test data.  
**Mitigation:** Use `testMode` only with `AUTH_PROVIDER=mock` or in a dedicated CI environment; never enable Test Mode in the production build.

### 3.7 IndexedDB / storage in Electron or private browsing
**Issue:** Magic stores session state in browser storage (IndexedDB). Private browsing, strict anti-tracking, or non-standard runtimes can break persistence and cause random logouts.  
**Impact:** Users may be kicked out unexpectedly.  
**Mitigation:** For Mynaani (web only), this is acceptable. If an Electron/desktop wrapper is added later, this needs revisiting.

---

## 4. Edge cases

| # | Edge case | Expected behavior | Test to add |
|---|---|---|---|
| E-001 | User enters invalid email | Magic SDK rejects before sending; UI shows calm error | `frontend/src/api/__tests__/auth.test.ts` |
| E-002 | DID token expired | Backend returns `auth.expired`; `AuthProvider` transitions to `SIGNED_OUT` | `test_magic_verifier.py` |
| E-003 | DID token malformed | Backend returns `auth.malformed` | `test_magic_verifier.py` |
| E-004 | Magic API rate limit (429) | Backend returns `auth.transient_verifier_unavailable`; frontend shows retry banner | `test_a3_auth.py` with mocked rate limit |
| E-005 | Magic API down or network error | Backend returns `auth.transient_verifier_unavailable`; no permanent sign-out | `test_a3_auth.py` with mocked connection error |
| E-006 | User clicks magic link on a different device | If `redirectURI` set, the original tab may not be logged in; Mynaani should test the simpler no-redirect flow | Manual / E2E |
| E-007 | Two accounts with same email (email change) | Magic `sub` (issuer) is the unique user ID, not email; `auth_user_id` should derive from `sub`, not just email | `test_magic_verifier.py` |
| E-008 | `MAGIC_API_SECRET_KEY` missing or wrong | Backend fails closed (no auth); logs a safe warning | `test_a3_auth.py` misconfiguration path |
| E-009 | `VITE_MAGIC_PUBLISHABLE_KEY` missing | Build-time guard stops the production build | `npm run build` / verify-build-env.mjs |

### Note on E-007 (critical)
The DID token `sub` is the Magic user subject. The `email` may change or not be stable across users. Mynaani's `accounts.auth_user_id` should derive from `sub` (or a uuid5 of `sub`), **not** from email alone, to avoid collision and relink issues. This is a correction to the integration plan and must be reflected in `magic_verifier.py`.

---

## 5. Best-in-class execution recommendations

1. **Fail-closed validation:** Every backend `verify_token` path for `magic` should return `None`/`AuthError` on any exception; never trust the token without admin SDK validation.
2. **No client-side secret:** Only the publishable key is in the frontend; the secret key never reaches the browser.
3. **Short DID tokens:** Keep the default 15-minute `loginWithMagicLink` token. If a refresh strategy is needed, use `magic.user.getIdToken({ lifespan: 15 * 60 })` on explicit user action.
4. **Bearer-only auth header:** Use `Authorization: Bearer <did_token>`; parse with the existing `parse_bearer()` helper.
5. **Defensive error classification:** Map Magic errors to the existing `auth.*` discriminated codes:
   - `DIDTokenExpired` -> `auth.expired`
   - `DIDTokenInvalid` / `IncorrectSignerAddress` -> `auth.signature_invalid`
   - `DIDTokenMalformed` / `ExpectedBearerStringError` -> `auth.malformed`
   - `RateLimitingError` / `APIConnectionError` -> `auth.transient_verifier_unavailable`
6. **Test strategy:** Mock `magic-admin.Magic` in backend tests; mock `magic-sdk` in frontend tests; reserve a dedicated Magic Test Mode app for CI.
7. **Session refresh as an explicit, later ADR:** Do not build auto-refresh in the first cut. The 15-minute token + calm re-auth prompt is more geragogy-aligned.
8. **Security logging:** Log `magic_did_validation_result` with `provider`, `email` (redacted), `token_age`, and `error_code`. Never log the token.
9. **Vendor app hygiene:** Document that only a **Magic Auth** (not Magic Connect) app is to be created.
10. **Cost guardrails:** Add a monthly MAW dashboard review; set up an alert at 80% of the free tier.

---

## 6. Open gaps this research creates

1. **GAP-MAGIC-SUBJECT-ID:** Need to confirm whether `accounts.auth_user_id` is `uuid5(NAMESPACE, sub)` or `uuid5(NAMESPACE, email)`. Recommendation: use `sub`.
2. **GAP-MAGIC-REDIRECT:** Decision needed on whether to use `redirectURI` and a `/callback` page.
3. **GAP-MAGIC-REFRESH:** Session-refresh strategy for the 15-minute DID is explicitly deferred to a follow-up ADR.
4. **GAP-MAGIC-TEST-DATA:** Need a test-mode tenant separate from production data.
5. **GAP-MAGIC-WHITELABEL:** Custom email domain is a future (post-pilot) consideration.

---

## 7. v9.51 traceability

- This research artifact is a `SourceArtifact` (`SRC-MAGIC-RESEARCH`) in the knowledge graph.
- Findings are linked as `Assumption` and `Gap` nodes to the relevant `Capability` nodes.
- Edge E-007 is linked to `CAP-MAGIC-VERIFIER` and `FR-004`.

---

*Generated under Process v9.51 with external, verifiable sources.*
