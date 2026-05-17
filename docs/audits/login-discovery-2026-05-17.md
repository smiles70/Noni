# Login Discovery — Noni System Audit

**Date:** 2026-05-17
**Branch at audit time:** `main` @ `faac463`
**Stack:** Vite + React 18 + axios · FastAPI + SQLAlchemy + Postgres ·
Clerk (RS256/JWKS) | Mock (localStorage `mock:<email>`) · Docker Compose
(3 containers)
**Mode:** discovery only — no solutions proposed.

> This document is the persisted form of the Phase 1–26 system-discovery
> output. Companion artifacts:
>
> - `docs/audits/login-system-constraints-2026-05-17.md`
> - `docs/audits/login-constraint-refinement-2026-05-17.md`
>
> Frozen reference tag: `login-constraints-v1`.

---

## PHASE 1 — Codebase & environment

**Frontend topology** (`frontend/src/`)

- Entry: `main.tsx` → conditionally wraps `<App>` with `<ClerkProvider>`
  based on `VITE_AUTH_PROVIDER` ("mock"|"clerk"). When clerk, also mounts
  `<ClerkTokenBridge>` *inside* the provider.
- App: `App.tsx` is a **single in-memory view-state machine**
  (`useState<View>`). No router. Hard refresh always returns to landing.
- State model: `view: View`, `signedIn: boolean | null` (null = loading),
  `pendingView: View | null` (post-signin forwarding).
- HTTP client: `api/client.ts` exports a single shared
  `apiClient = axios.create({baseURL})`. Two interceptor install paths
  (mock at module load; Clerk inside `ClerkTokenBridge` useEffect).
- Auth surface: `api/auth.ts` exports `whoami()` + `deleteAccount()` +
  re-exports `setMockToken/clearMockToken`.

**Backend topology** (`backend/`)

- Entry: `backend/app/main.py` — FastAPI with `lifespan` running
  `run_migrations()` on boot.
- Auth dep: `backend/api/deps.py` — `_parse_bearer` →
  `verify_credential` → `_upsert_account` → `db.commit()` per request.
- Provider: `backend/services/auth_provider.py` — `MockAuthProvider` +
  `ClerkAuthProvider` (PyJWKClient, fail-closed).
- Endpoints (auth-relevant): `GET /auth/whoami`, `POST /me/delete`,
  `POST /me/delete/cancel`. **No** `/auth/callback`, **no**
  `/auth/signout` (removed per ADR 0024).
- DB: `Account(id UUID, auth_user_id UUID UNIQUE, email CITEXT UNIQUE
  NOT NULL, display_name, timestamps, deleted_at)`. `sessions` table
  exists but **unused**.

**Environment / secret handling**

- `.env` loaded by pydantic-settings. `VITE_AUTH_PROVIDER` +
  `VITE_CLERK_PUBLISHABLE_KEY` baked at **build time** via
  docker-compose `build.args`.
- Backend reads `AUTH_PROVIDER`, `CLERK_JWKS_URL`, `CLERK_ISSUER`,
  `CLERK_SECRET_KEY` (optional but **required to materialize email**
  for any Clerk user since default token lacks email).
- CORS: `allow_credentials=False`, wildcard methods/headers. Origins
  from env or default `http://localhost:5173`. Compose overrides to
  `http://localhost:8080,http://localhost:5173`.

**Build-vs-runtime gotchas**

- Frontend `VITE_*` is **baked at build**. Changing provider requires
  `docker compose build frontend`. No runtime toggle.
- Backend `AUTH_PROVIDER` is runtime. Mismatch (FE=clerk, BE=mock) is
  silently corrupt: backend accepts only `mock:<email>` tokens, rejects
  every Clerk JWT, frontend infinite-redirects to signin.

---

## PHASE 2 — Purpose & success criteria

- **Primary outcome:** older adult arrives → can read free curriculum
  unit 1 page 1 within ≤ 3 clicks, resume position next visit,
  optionally upgrade (modules 4–5) or delete account.
- **Critical path:** Landing → (sign in if required) → curriculum
  unit-1 page-1 rendered with progress persisted.
- **Success def:** `signedIn === true` AND a `curriculum.unit` envelope
  renders AND `noni_progress_v1` writes succeed.
- **Failure def:** stuck on `<PendingBanner>` ("One moment —
  loading."), or signin↔landing oscillation, or whoami 401 loop, or
  unhandled 5xx behind the paywall route.

---

## PHASE 3 — Intent vs implementation

**Apparent intent** (ADRs 0023→0024)

- Stateless bearer auth, single source of truth (the JWT), backend is
  dumb verifier, frontend is dumb attacher.
- Provider abstraction so mock/clerk are interchangeable behind the
  same `AuthProvider` protocol.
- No cookies, no CSRF, no session table coupling.

**Actual divergence**

- `accounts.email` is **NOT NULL UNIQUE**, but Clerk's default session
  token has no email. Backend silently round-trips to Clerk Backend API
  (`GET /v1/users/{sub}`) per first-sight account, with
  `CLERK_SECRET_KEY` required. → "stateless verifier" is **not
  stateless** on first sight; it's a 2-call provider lookup.
- `_upsert_account` writes (potentially commits) on what is logically a
  read (`/auth/whoami`). The `db.commit()` is inside the dep, not the
  route. → side-effect on every cold first-sight whoami.
- `NavBar` (mounted inside landing & curriculum) makes its **own**
  `whoami()` call even though `App.tsx` already has authoritative
  `signedIn` state. → N+1 whoami per page, each triggers the upsert dep.
- Mock + Clerk interceptors both write Authorization. Mock-mode guard
  prevents collision, but the **two distinct install paths** mean
  reading the request lifecycle requires reading 2 files.
- `App.tsx`'s `useEffect` defers initial `whoami()` in clerk mode
  (waits for `ClerkAuthSync.onAuthChanged`). In mock mode it fires
  immediately. → asymmetric startup contract.

---

## PHASE 4 — State ownership / source of truth

| Concern | Owner | Reader(s) | Conflict |
|---|---|---|---|
| Identity (who you are) | Clerk (or mock token) | backend `verify_credential` | none |
| Auth state (signed-in?) | Clerk SDK (`useAuth().isSignedIn`) | App.tsx, NavBar, ClerkSignOutButton, SignOutLink, SignInPage's ClerkSignInBranch | **5 readers, ad-hoc sync** |
| Authorization (entitlements) | Postgres `purchases`/`entitlements` | `require_entitlement` dep | none |
| Persisted progress | `localStorage.noni_progress_v1` | CurriculumRenderer | not cleared on sign-out |
| Mock token | `localStorage.noni.mock_token` | mock interceptor | not cleared by Clerk's signOut() |
| Email | `accounts.email` after first sight | NavBar, AccountSettingsPage, App | Clerk is upstream; can drift if user changes email in Clerk |

**Key conflict:** *Two competing views of "signed in"* —
`useAuth().isSignedIn` (Clerk in-memory) vs `whoami()` result (backend).
They're reconciled via the `ClerkAuthSync` → `refreshAuth` →
`setSignedIn` chain, but there is a window where they disagree (token
issued, JWKS slow, whoami 401).

---

## PHASE 5 — User journeys

**New user (Clerk mode)**

1. Landing → "Set up my account — free"
2. `requireAuth("curriculum")` → `signedIn === null` initially,
   `signedIn === false` after first `whoami` (Clerk SDK not yet
   hydrated) — note **App defers first whoami until ClerkAuthSync
   fires** in clerk mode; in practice signedIn stays `null` →
   `<PendingBanner>`.
3. Clerk SDK hydrates → ClerkAuthSync fires `onAuthChanged` (signed-out
   branch) → setSignedIn(false) → user is now on landing with
   signedIn=false. **They never reached `requireAuth("curriculum")`
   reroute.** Click again → SignIn widget mounts.
4. Complete Clerk flow → `useAuth().isSignedIn` flips → `ClerkAuthSync`
   waits for non-null `getToken()` → fires onAuthChanged →
   `handleSignedIn` → whoami → if 200, App advances to
   `pendingView ?? "curriculum"`.
5. First-sight backend upserts account (Clerk Backend API call for
   email).
6. Curriculum renders.

**Returning user (Clerk mode, cookies present)**

1. Landing renders with `signedIn === null` (PendingBanner risk).
2. Clerk SDK hydrates from its own cookies → `ClerkAuthSync` waits for
   token → onAuthChanged → refreshAuth → whoami 200 → setSignedIn(true).
3. Landing re-renders showing "Continue learning →" + SignOutLink +
   NavBar (Upgrade / Your account).

**Degraded scenarios**

- **JWKS network failure:** `ClerkAuthProvider.verify_credential` logs
  `clerk_jwks_lookup_failed`, returns None → 401 → App sets
  signedIn=false → user bounced to SignIn → Clerk SDK still reports
  signed-in → re-fire onAuthChanged with token → backend 401 again →
  **loop possible** (documented in code comments as the bug that
  motivated the gate-on-token logic).
- **Clerk Backend API down on first sight:** `fetch_user_profile`
  returns None → `_upsert_account` returns None → whoami 401 →
  infinite signin loop for a brand-new user. Existing users (already
  in `accounts`) are unaffected.
- **Cross-origin Clerk cookies blocked** (Safari ITP, container/proxy
  mismatch): isSignedIn stays false → standard signed-out flow, no
  loop.
- **`CLERK_SECRET_KEY` empty + new Clerk user:** same as above —
  guaranteed 401 forever.

---

## PHASE 6 — UI interaction map

| Action | Trigger | State assumption | API call | Expected outcome | Actual edge |
|---|---|---|---|---|---|
| "Set up my account — free" | LandingPage signed-out | signedIn=false | (none) | requireAuth → setView('signin') | If signedIn still `null`, gated branch shows SignIn anyway |
| "Log in" | LandingPage signed-out | signedIn=false | (none) | setView('signin') | none observed |
| "Continue learning →" | LandingPage signed-in | signedIn=true | (none) | requireAuth('curriculum') | none |
| "Sign out" (SignOutLink) | LandingPage signed-in | signedIn=true | clerk.signOut() locally | refreshAuth → signedIn=false → landing | leaves `noni_progress_v1`; next user sees prior progress |
| Submit SignIn form | SignInPage mock | envelope loaded | (none — just setMockToken) | onSignedIn → whoami → curriculum | mock token persists across Clerk sign-out |
| Complete Clerk widget | SignInPage clerk | ClerkProvider mounted | (Clerk handles) | useAuth flips → wait for token → whoami | window between isSignedIn=true and token-ready where button presses are silently ignored |
| "Lessons" in NavBar | curriculum or landing | onOpenMenu wired | (none) | setView('menu') | LandingPage does not pass onOpenMenu |
| "Your account" in NavBar | NavBar signed-in | signedIn=true | (none) | requireAuth('account') | NavBar's local `signedIn` can disagree with App's for ~100ms |
| "Delete my account" | AccountSettingsPage confirmed | signedIn=true | POST /me/delete | setView('landing') after 1500ms | does not call clerk.signOut() → loop risk on re-sign-in |
| `?reset=1` | any URL | n/a | (none) | clear progress + mock_token, reload | does NOT clear Clerk localStorage |

---

## PHASE 7 — Navigation / routing

**Routes (frontend):** none. There is **no URL-state binding**. Every
navigation is an in-memory `setView` call.

**Routes (backend):**

- `/auth/whoami` (auth required)
- `/me/delete`, `/me/delete/cancel` (auth required)
- `/api/curriculum/*` (mostly public; lesson + retrieval-choice gated
  by `get_current_account` in some places)
- `/api/billing/*` (entitlement-gated → 402)
- `/api/gifts/*`
- `/api/ui-envelope/{id}` (public)
- `/api/landing/*` (public)
- `/api/telemetry/*`
- `/health`, `/`

**Loops / dead-ends identified**

- `oauth_finishing` has no exit transition wired in App.tsx — the view
  is in the enum but never set anywhere in current code. Dead state.
- `signin ↔ landing` manual oscillation if user keeps trying.
- Documented hot loop (mitigated):
  `landing → curriculum → 401 → setSignedIn(false) → signin → Clerk
  signed-in → whoami → 401 → ...`. Currently held off by ClerkAuthSync
  gating on `getToken()` returning non-null, but the loop still exists
  logically if JWKS verification fails server-side.

---

## PHASE 8 — State machine & timing

**States (App.tsx logical):**

```
S_BOOT_UNKNOWN     signedIn=null, view=landing                (initial)
S_LANDING_OUT      signedIn=false, view=landing
S_LANDING_IN       signedIn=true,  view=landing
S_SIGNIN           view=signin    (signedIn may be null|false|true)
S_GATED_LOCKED     signedIn=false AND view ∈ GATED_VIEWS      (renders SignInPage)
S_GATED_LOADING    signedIn=null  AND view !== oauth_finishing(renders PendingBanner)
S_CURRICULUM_IN    signedIn=true,  view=curriculum
S_MENU             view=menu      (any signedIn)
S_ACCOUNT          signedIn=true,  view=account
S_PAYWALL          signedIn=true,  view=paywall
S_GIFT             signedIn=true,  view=gift_redeem
S_OAUTH_FIN        view=oauth_finishing                       (orphan)
```

**Timing facts**

- `signedIn` starts `null`. Mock mode: `whoami` fires on mount. Clerk
  mode: `whoami` deferred until `ClerkAuthSync` says "ready".
- `ClerkAuthSync` waits on
  `isLoaded && (isSignedIn === false OR getToken() returns non-null)`.
  The clock-window between
  `isLoaded=true, isSignedIn=true, getToken()=null` is the historical
  race.
- `ClerkTokenBridge` installs interceptor inside `useEffect` after
  `isLoaded`. If any axios call fires before that effect runs, it goes
  out unauthenticated. Mitigated by App.tsx deferring whoami in clerk
  mode — **but NavBar's own whoami inside its `useEffect` is not gated**
  and can race.
- Backend per-request: `verify_credential` makes **0** network calls
  when JWKS key is cached, 1 call on cold start or key rotation.
  `fetch_user_profile` makes 1 Clerk Backend API call **only when
  account row is missing AND token lacks email**.

**Race conditions observed**

1. **NavBar whoami vs ClerkTokenBridge interceptor install** in clerk
   mode cold boot.
2. **Two `whoami` callers writing simultaneously:** App.tsx and NavBar
   both trigger `_upsert_account` which calls `db.commit()`.
3. **localStorage cross-key staleness:** `?reset=1` doesn't clear Clerk
   keys.
4. **handleClerkAuthChanged scope:** only auto-advances view when
   `view === "signin"`.

---

## PHASE 9 — Auth model / trust boundaries

- **Trust placed in:** the JWT signature (RS256/JWKS) + `exp` + `iss` +
  presence of `sub`. Backend trusts nothing else about the bearer.
- **Per-request work:** parse header → JWKS-verify → derive UUID from
  `sub` via `uuid5(NAMESPACE_URL, "clerk:<sub>")` → upsert. No DB
  lookup for the JWT itself.
- **Redundant validation:** none on the path. But the *upsert with
  commit on a read* is a hidden write effect every single `whoami` call
  performs (no-op once row exists).
- **Email re-sync:** every whoami re-checks
  `claims.email != account.email`. If Clerk default token has no email,
  `claims.email is None` → no update → cached value stale forever.

---

## PHASE 10 — Failure modes & amplification

| # | Cause | Symptom | Propagation | User impact | Amplifier |
|---|---|---|---|---|---|
| F1 | `CLERK_JWKS_URL` unset / unreachable | every JWT verify fails | all `get_optional_account` deps return None → 401 | infinite signin loop | NavBar parallel whoami doubles request volume |
| F2 | `CLERK_SECRET_KEY` empty + new user | first-sight `_upsert_account` returns None | 401 on whoami | new user can never sign in | Clerk reports signed-in → loop |
| F3 | Clerk JWT expires mid-session | next API call 401 | refreshAuth sets signedIn=false | mid-lesson kick to SignIn | SDK auto-refresh fails if tab background-throttled |
| F4 | Clerk Backend API rate-limit on first-sight burst | first-sight 5xx | upsert returns None → 401 | user lockout | none |
| F5 | `accounts.email` UNIQUE collision (legacy row) | Race B in upsert: relinks row | quiet steal | previous owner's `auth_user_id` overwritten | no audit |
| F6 | Mock and Clerk both present in localStorage | wrong token sent | 401 | reset escape doesn't clear Clerk keys |
| F7 | `noni_progress_v1` survives sign-out | next user on shared device sees prior progress | wrong unit appears | confusion |
| F8 | NavBar/App `signedIn` disagree | landing shows signed-in chrome AND SignIn page | brief render flash | UX confusion |
| F9 | `oauth_finishing` view never exited | terminal pending banner | full lockout | manual reload required |
| F10 | Diagnostic `print()` in deps.py logs token prefix | 24-char token prefix in logs | log retention exposure | every authenticated request |

---

## PHASE 11 — Critical-path collapse

- **Singleton kills:** `CLERK_JWKS_URL`, `CLERK_SECRET_KEY` (only
  first-sight new users), `accounts.email NOT NULL`.
- **Two-element kills:** FE=clerk + BE=mock; Clerk widget + JWKS
  outage.
- **Three-element kills:** ClerkSignOut + leftover mock + accidental
  rebuild flipping provider.

---

## PHASE 12 — Error semantics

| Status | Origin | Frontend interpretation | Lossy? |
|---|---|---|---|
| 401 (any cause) | `get_current_account` | "signed-out" → bounce to SignIn | **Yes** — JWKS failure, expired, missing email, missing CLERK_SECRET_KEY, Backend-API failure all look identical |
| 402 + `envelope_id: billing.signin_or_purchase_required` | entitlement no session | should route to SignIn | only billing.ts checks `envelope_id` |
| 402 + `envelope_id: billing.purchase_required` | entitlement no grant | route to paywall | preserved |
| 5xx | uncaught | axios throws | App.tsx maps to signedIn=false for whoami (**wrong**) |
| network error | axios | same as 5xx | indistinguishable from auth failure |

`whoami` collapsing every error into `signedIn=false` is the single
largest loss of semantic information in the auth path.

---

## PHASE 13 — Side effects & data safety

| Path | Write | Idempotent? | Risk |
|---|---|---|---|
| `/auth/whoami` first sight | INSERT accounts + commit | yes (relink) | makes "read" endpoint a write endpoint |
| `/auth/whoami` returning visit | UPDATE accounts (email/display_name if changed) + commit | yes | unnecessary write per request |
| `_upsert_account` Race B | UPDATE existing account's `auth_user_id` | **No** — silent ownership transfer | dangerous |
| `clerk.signOut()` | clears Clerk cookies/localStorage | yes | does NOT call backend |
| `clearMockToken()` | localStorage.removeItem | yes | does NOT call Clerk SDK |
| `DELETE /me/delete` | marks row deleted | yes | does NOT revoke Clerk session → resurrection |

---

## PHASE 14 — System boundaries & contracts

| Boundary | Guarantee (intended) | Assumed (consumer) | Mismatch |
|---|---|---|---|
| Clerk → FE | `useAuth().isSignedIn` reflects current session | App: "isSignedIn true ⇒ I can call backend" | **getToken() can return null briefly** |
| FE → BE | Authorization attached to every authenticated call | BE: header attached or 401 | NavBar/bridge race can drop header |
| BE → DB | `accounts.email NOT NULL` | API layer: row always has email | upsert can fail to materialize → 401 |
| Clerk Backend API → BE | `GET /v1/users/{sub}` returns email | `fetch_user_profile` | rate limits, transient 5xx → 401 |
| Backend session | gone (ADR 0024) | `accounts.deleted_at` is the only deletion signal | Clerk still issues tokens to deleted accounts |
| `whoami` 401 contract | "not signed in" | App: signedIn=false | conflates 7+ distinct failure causes |

---

## PHASE 15 — Invariants & violations

1. **I1**: provider-signed-in + token-ready ⇒ whoami 200. Violated by
   F1, F2, F4, deleted_at, NULL email.
2. **I2**: signed-out user cannot mutate backend. Holds.
3. **I3**: read endpoints don't write. Violated.
4. **I4**: localStorage purged on sign-out. Violated for
   `noni_progress_v1`, mock token in Clerk mode, Clerk keys in mock mode.
5. **I5**: one user → one account row → one Clerk subject. Violated by
   Race B.
6. **I6**: deleted account cannot sign in again. Violated.
7. **I7**: App's signedIn agrees with NavBar's local signedIn. Violated.
8. **I8**: token error means token is bad. Violated.

---

## PHASE 16 — Failure isolation & recovery

- **Blast radius:** JWKS failure → entire signed-in app dies. DB outage
  → every endpoint dies. Clerk Backend API outage → only new users
  affected. Frontend build with wrong VITE_AUTH_PROVIDER → entire
  authenticated app dies until rebuild.
- **Recovery:** no automatic retries on auth path. Backend fails closed;
  frontend re-runs whoami on next `setView` through `requireAuth` or
  when ClerkAuthSync re-fires.
- **Convergence:** the system converges only because the user gets
  bored and reloads. No engineered convergence mechanism for any of
  F1–F10.

---

## PHASE 17 — Coupling & complexity

- `_upsert_account` couples JWT verification, Clerk Backend API client,
  and DB write into one dep.
- 5 frontend components touch Clerk hooks: `ClerkTokenBridge`,
  `ClerkAuthSync`, `SignInPage.ClerkSignInBranch`, `ClerkSignOutButton`,
  `SignOutLink.ClerkBranch`.
- `signedIn` is a derived value from a network call (whoami) which
  itself is a side effect (upsert) — three concerns conflated.
- View state is in-memory only; no URL coupling.
- `NavBar` is coupled to `whoami` instead of being stateless.

---

## PHASE 18 — Simplification opportunities

- `NavBar` performing its own `whoami`.
- `oauth_finishing` view (orphan).
- Diagnostic `print()` statements in `deps.py` and `auth_provider.py`.
- `sessions` table & associated unused config.
- Legacy Supabase env vars in `.env.example`.
- Email re-sync on every authenticated request.
- Two near-identical sign-out components.
- `commit()` inside `get_optional_account` for read-only routes.

---

## PHASE 19 — Minimum viable system model

- One identity provider behind one protocol (already true).
- One credential channel (Bearer; already true).
- One whoami semantics with **discriminated** error reasons.
- One reconciler for FE auth state (not five Clerk-touching components
  + NavBar).
- Lazy upsert on **mutation**, not on read.
- Persisted progress keyed by account id, not by localStorage shared
  across users on the same browser.

---

## PHASE 20 — Single points of failure

1. `ClerkAuthProvider.verify_credential`.
2. JWKS endpoint reachability.
3. `accounts.email NOT NULL UNIQUE` with token having no email claim.
4. `_upsert_account` (single function, three responsibilities).
5. `apiClient` interceptor install timing.
6. `whoami` semantics.
7. Frontend build's baked `VITE_AUTH_PROVIDER`.

---

## PHASE 21 — Reality vs user perception

| User believes | Actual state | Wedge |
|---|---|---|
| "I'm signed in" | Backend says 401 (JWKS / Backend-API failed) | sees SignIn page reappear |
| "I signed out" | localStorage progress retained; mock token may persist | next user inherits |
| "I deleted my account" | `deleted_at` set; Clerk session intact | resurrection |
| "I'm on lesson 5" | progress is browser-scoped, not account-scoped | wrong unit |
| "Reset wiped my data" | Only Noni's keys; Clerk persists | unexpected auto-signin |
| Email = current Clerk email | Cached at first sight; never refreshed | stale display |

---

## PHASE 22 — Observability

- **Logging present:** `logger.info` for JWKS failures, JWT rejections,
  Backend API failures; `print(..., flush=True)` for
  `DIAG_AUTHZ_HEADER`, `VERIFY_*` markers.
- **Logging absent:** envelope_id emitted on 401, JWKS duration,
  `fetch_user_profile` invocation count, Race B occurrences.
- **Frontend telemetry:** `console.warn` from client.ts and
  ClerkTokenBridge; no aggregate signal.
- **Tracing:** none. No request id propagates.
- **Blind spots:** Race B, upsert frequency on whoami, signedIn FE/BE
  disagreement, NavBar-vs-App skew, leftover localStorage, deleted
  resurrection.

---

## PHASE 23 — Synthesis

### TOP 5 design flaws blocking reliability

1. `/auth/whoami` is structurally a write endpoint (commit-on-read)
   wrapped in a verify-then-upsert dep that conflates three failure
   modes into one 401.
2. Frontend auth state lives in **two** independent caches.
3. `accounts.email NOT NULL UNIQUE` is incompatible with Clerk's
   default token.
4. Build-time `VITE_AUTH_PROVIDER` decouples FE/BE provider config.
5. Sign-out is asymmetric.

### TOP 5 production failure risks

1. JWKS network failure → full signed-in app outage.
2. Clerk Backend API rate-limit → 100% of new sign-ups fail.
3. Email-collision relink (Race B) silent ownership transfer.
4. Deleted-account resurrection.
5. Diagnostic `print()` of Authorization-header prefix.

### TOP 5 simplification opportunities

1. Remove `sessions` table + `SESSION_*` settings.
2. Remove `oauth_finishing` view.
3. Collapse NavBar's whoami into a prop from App.
4. Remove `commit()` from `get_optional_account`.
5. Collapse two sign-out components.

### TOP 5 invariants currently violated

- I1, I3, I4, I5, I6 (see Phase 15).

---

## PHASE 24 — End-to-end navigation simulation

**Session A: brand-new visitor, Clerk mode, default Clerk token (no
email), `CLERK_SECRET_KEY` empty**

| # | User action | Network | BE behavior | UI result |
|---|---|---|---|---|
| 1 | Open `localhost:8080` | landing.page envelope, /api/landing/page | 200, 200 | PendingBanner → landing |
| 2 | ClerkAuthSync mounts | none | n/a | onAuthChanged signed-out → whoami → 401 → signedIn=false |
| 3 | Landing re-renders | NavBar fires its own whoami | 401 (DIAG_AUTHZ_HEADER=None ×2) | hero shows CTA |
| 4 | Click "Set up my account — free" | none | n/a | SignInPage → Clerk widget |
| 5 | User completes Clerk sign-up | (Clerk handles) | n/a | nothing visible yet |
| 6 | ClerkAuthSync re-fires | GET /auth/whoami with Bearer | verify OK, claims.email=None, fetch_user_profile None (no key), upsert None → 401 | refreshAuth signedIn=false → setView('curriculum') |
| 7 | App renders curriculum but signedIn=false → SignInPage | none | n/a | **same SignIn widget, no error shown** |
| 8 | Reload | repeats | repeats | **loop with no surfaced reason** |

**Session B: returning user, healthy Clerk + secret key**

1. Open → PendingBanner.
2. ClerkAuthSync hydrates → whoami 200, signedIn=true.
3. Landing shows "Continue learning →" + SignOut + NavBar.
4. NavBar fires its own whoami — duplicate.
5. Click "Continue learning →" → curriculum.
6. NavBar fires whoami AGAIN.
7. Click "Sign out" → clerk.signOut() → cookies cleared → refreshAuth →
   401 → signedIn=false → view=landing.
8. `noni_progress_v1` retained; another user signs in on same browser →
   stale unit shows.

**Session C: Clerk fine, account row has `deleted_at` set**

1. Sign in via Clerk → JWT verifies, upsert finds existing row,
   ignores deleted_at, returns Account, whoami 200.
2. App treats as signed-in normally. **Deleted user is back.**

---

## PHASE 25 — Structured artifacts

### Critical user path

```
Landing → CTA click → Clerk SDK hydrate → SignIn widget → Clerk complete →
ClerkAuthSync.onAuthChanged → whoami → upsert → 200 → setView(curriculum) →
curriculum.unit envelope → lesson page 1 render → localStorage progress write
```

### Failure chains

- **FC1 — Clerk signed-in but whoami 401:** Clerk OK → claims.email=None
  → fetch_user_profile None → upsert None → 401 → signedIn=false →
  GATED_LOCKED renders SignInPage → useAuth still true → loop.
- **FC2 — JWKS unreachable:** every protected call → verify None → 401
  → all signed-in views renderable only as SignInPage → users perceive
  "everyone got logged out".
- **FC3 — Race B silent relink:** legacy row email E1, sub S1 → new
  user with E1 sub S2 → INSERT fails (unique) → SELECT by email →
  overwrite auth_user_id → S1 orphaned.
- **FC4 — Resurrection of deleted account:** delete → deleted_at →
  view=landing → user clicks Continue → Clerk session alive → whoami →
  upsert finds row by auth_user_id → returns it (deleted_at ignored) →
  signedIn=true.
- **FC5 — Stale progress:** UserA signs out → noni_progress_v1 remains
  → UserB signs in → loads UserA's progress.
- **FC6 — NavBar/App disagreement:** App fires whoami before
  interceptor installed → 401 → signedIn=false → simultaneously NavBar
  fires after interceptor → 200 → flash.

---

## PHASE 26 — ASCII diagrams

### End-to-end user flow

```
[Browser]                                        [FastAPI]              [Clerk Cloud]
   |                                                 |                       |
   |-- GET / (HTML) ----------------------------->  nginx                    |
   |<-- index.html / bundle.js (with VITE_* baked)  |                        |
   |                                                 |                       |
   | main.tsx: provider==="clerk"?                   |                       |
   |   yes -> <ClerkProvider><ClerkTokenBridge/><App/></ClerkProvider>       |
   |                                                 |                       |
   | ClerkSDK hydrate <----------------------- session cookies ---- Clerk ---|
   |                                                                          |
   | ClerkAuthSync onAuthChanged -> App.refreshAuth -> whoami()               |
   |   axios.get('/auth/whoami')                                              |
   |   interceptor attaches Authorization: Bearer <JWT>                       |
   |-- GET /auth/whoami  Authorization: Bearer ... -> FastAPI                 |
   |                                          get_optional_account:          |
   |                                            verify_credential (JWKS)     |
   |                                            _upsert_account              |
   |                                              if no email: fetch_user_   |
   |                                              profile (Clerk Backend)<- |
   |                                            db.commit()                  |
   |<---- 200 OR 401 ----------------------------------------------------     |
   |                                                                          |
   | App.signedIn = res ? true : false                                        |
   | NavBar also fires its OWN whoami (duplicate)                             |
   | render gated view OR SignInPage                                          |
```

### State machine

```
                    +----------------+
   boot ----------> | BOOT_UNKNOWN   |
                    +----------------+
                       |          |
        whoami 200     |          | whoami 401 OR error
                       v          v
              +---------------+  +-----------------+
              | LANDING_IN    |  | LANDING_OUT     |
              +---------------+  +-----------------+

   ORPHAN: OAUTH_FINISHING  (in enum; never entered)

   OSCILLATION:
     SIGNIN <-> GATED_LOCKED   when (Clerk says yes) AND (whoami 401)
```

### Critical path

```
LANDING_OUT
  | click CTA
  v
SIGNIN  (Clerk widget)
  | user completes; isSignedIn=true
  | ClerkAuthSync awaits getToken() != null
  v
whoami(JWT) -> verify(JWKS) -> upsert(email present OR fetch_user_profile OK) -> 200
  v
CURRICULUM -> envelope load -> first lesson render -> progress write

BREAKPOINTS:
  [B1] JWKS unreachable                  -> SIGNIN loop
  [B2] CLERK_SECRET_KEY empty + new user -> SIGNIN loop
  [B3] interceptor not yet installed     -> NavBar 401 (recovers, noisy)
  [B4] accounts.deleted_at on row        -> resurrects silently
  [B5] noni_progress_v1 from prior user  -> wrong lesson surfaces
```

---

# END OF AUDIT
