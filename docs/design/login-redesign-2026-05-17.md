# System Design — Noni Login Domain (post-redesign)

**Date:** 2026-05-17
**Source constraints:** `login-constraints-v1` (frozen tag).
Companion: `docs/audits/login-constraint-refinement-2026-05-17.md`
and `docs/design/login-execution-playbook-2026-05-17.md`.
**Mode:** complete design. No deferred decisions on the critical path.
**Frozen reference tag (this doc):** `login-redesign-v1`.

---

## PHASE 1 — ARCHITECTURE OVERVIEW

```
┌────────────────────────────────────────────────────────────────────────┐
│                            BROWSER (Vite SPA)                          │
│                                                                        │
│  main.tsx                                                              │
│    └─ <ProviderShell>            // chooses Clerk or Mock provider     │
│         └─ <AuthProvider>        // SINGLE owner of auth state (B1)    │
│              ├─ installs ONE axios interceptor (B2, T2)                │
│              ├─ owns AuthContext: BOOT|SIGNED_OUT|AUTHENTICATING|     │
│              │     READY|REJECTED|TRANSIENT_ERROR                      │
│              ├─ runs provider-parity probe at boot (B3, T4)            │
│              └─ <App>                                                  │
│                   ├─ useAuth()  // read-only consumers                 │
│                   ├─ <Router>   // in-memory view machine              │
│                   ├─ <Chrome>   // identity strip; reads context       │
│                   └─ <Body>     // current view; reads context         │
└────────────────────────────────────────────────────────────────────────┘
                              │  HTTPS  Authorization: Bearer <JWT>
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FastAPI (backend)                              │
│                                                                        │
│  /auth/config          (GET)  provider parity probe (B3, T4)           │
│  /auth/session         (GET)  pure-read session resolve (B4, B5, T6)   │
│  /auth/session/init    (POST) materialize account (write event) (T6)   │
│  /me/progress          (GET/PUT) progress per account (I-F)            │
│  /me/delete            (POST) terminal deletion (B7, I-E)              │
│  /me/recreate          (POST) explicit re-creation surface (B7)        │
│                                                                        │
│  Layers:                                                               │
│    routes        → thin; depend on get_session_subject()               │
│    deps          → verify_token (PURE, no DB) (C3)                     │
│                  → get_subject_account (READ-ONLY lookup, no commit)   │
│    services      → AccountMaterializer (write) (B4)                    │
│                  → ProgressStore (write) (I-F)                         │
│                  → ProviderProfileFetcher (best-effort, off-path) (C3) │
│  log middleware  → header redactor (B10)                               │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Postgres                                         │
│  accounts(id, auth_user_id UNIQUE NOT NULL, email NULL,                │
│           display_name NULL, created_at, updated_at, deleted_at NULL)  │
│                                                                        │
│  learner_progress(account_id PK, module, unit_id, page_index,          │
│                   updated_at)                                          │
│                                                                        │
│  REMOVED: sessions table, SESSION_* config (S1)                        │
└────────────────────────────────────────────────────────────────────────┘

External (best-effort, OFF the critical path):
  - Identity provider JWKS endpoint (cached, with stale-cache fallback)
  - Identity provider Backend API (consumed only by ProviderProfileFetcher
    in a background job; never blocks /auth/session)
```

**Boundaries:**

- Identity = provider; Authentication state = provider SDK on client;
  Authorization (entitlements) = backend; Account record = DB. Four
  owners, no overlap. (§4.1)
- FE never asks the backend "am I signed in?"; it asks "is my
  credential currently accepted?". The provider SDK is the only
  signed-in/out signal. (F-A1)

---

## PHASE 2 — AUTHENTICATION FLOW DESIGN

### 2.1 Boot sequence (T1, T2, T3, T4, B3)

```
1. main.tsx renders <ProviderShell> with VITE_AUTH_PROVIDER baked.
2. <AuthProvider> mounts:
     a. emits AuthState = BOOT.
     b. fires GET /auth/config (no auth needed).
        - response { provider: "clerk" }; if mismatch with VITE_AUTH_PROVIDER,
          throw fatal; render <FatalConfigError/> (no children mount). (B3, T4)
     c. installs axios interceptor that calls AuthProvider.getCredential().
        Interceptor is the ONLY writer of Authorization. (B2)
     d. awaits provider SDK isLoaded signal (T1).
3. Once isLoaded:
     - if NOT signed-in → AuthState = SIGNED_OUT (no whoami call). (T3)
     - if signed-in → AuthState = AUTHENTICATING; await getToken() ≠ null. (T3)
4. With token in hand:
     - GET /auth/session (single call, only place that resolves session). (T7)
     - On 200 with materialized=true:  AuthState = READY.
     - On 200 with materialized=false: POST /auth/session/init (write event);
                                       on success → READY. (B4, T6)
     - On 4xx with discriminated reason:
         · auth.account_deleted        → REJECTED (terminal)        (B7, I-E)
         · auth.signature_invalid      → REJECTED (terminal)        (R4)
         · auth.expired                → ask SDK to refresh ONCE; if still
                                          rejected → REJECTED       (R4)
     - On 5xx OR network error:
         · AuthState stays AUTHENTICATING for one bounded retry,
           then TRANSIENT_ERROR (signed-in preserved).               (R3, R7)
5. Once READY: <Body> may render any view. <Chrome> reads same state.  (I-G)
```

### 2.2 Per-request lifecycle (B2, T2)

```
component → apiClient.get(url)
  └─ axios request interceptor:
       const cred = await AuthProvider.getCredential();
       if (cred) headers.Authorization = `Bearer ${cred}`;
       return config;
  └─ network → backend
       backend: verify_token(cred) → claims (PURE; no DB)
                get_subject_account(claims.sub) → row | None  (READ ONLY)
                route handler executes
  └─ axios response interceptor:
       if 401 with code in DEFINITIVE_SET → AuthProvider.markRejected(code)
       if 401/5xx with code in TRANSIENT_SET → AuthProvider.markTransient()
       else → pass through
```

The interceptor never re-issues a failed request automatically. (R2)

### 2.3 Verification path (C3, B11)

```
verify_token(token):
    parts = parse(token)
    if invalid_format: raise AuthError("auth.malformed")
    if provider == clerk:
        key = jwks_cache.get(kid) or jwks_cache.refresh(kid)
        if not key: raise AuthError("auth.transient_verifier_unavailable")
        try:
            claims = jwt.decode(token, key, algs=["RS256"], iss=CLERK_ISSUER)
        except SignatureError: raise AuthError("auth.signature_invalid")
        except ExpiredError:   raise AuthError("auth.expired")
        except IssuerError:    raise AuthError("auth.issuer_mismatch")
        if not claims.sub:     raise AuthError("auth.subject_missing")
        return claims
    elif provider == mock:
        ...
```

**No** Backend API call. **No** DB call. **No** dependency on
`CLERK_SECRET_KEY`. (B11, C1, C3)

### 2.4 Account materialization (B4, T6)

`POST /auth/session/init` is the only path that writes accounts. Called
explicitly by FE after first `200 / materialized:false` response.

```
materialize(claims):
    with db.begin():
        try:
            row = INSERT INTO accounts (auth_user_id, email, display_name)
                  VALUES (uuid_from_sub(claims.sub),
                          claims.email,            -- may be NULL (B12)
                          claims.name)
                  ON CONFLICT (auth_user_id) DO NOTHING
                  RETURNING id;
        except ...:
            row = SELECT id FROM accounts
                  WHERE auth_user_id = uuid_from_sub(claims.sub)
                    AND deleted_at IS NULL;        -- I-E
        if row is None:
            return CONFLICT  -- deleted; FE must POST /me/recreate to proceed
        return row.id
```

**No `email`-collision relink.** Two distinct subjects with the same
email is an explicit `409 auth.email_already_owned`. (B8, I-D)

A background job (`ProviderProfileFetcher`) lazily fills
`email`/`display_name` for rows with NULL values. Failure of this job
NEVER blocks any user request. (I-H, R5)

---

## PHASE 3 — SYSTEM STATE MODEL

### 3.1 Authoritative client state

```
AuthState ::= BOOT
            | SIGNED_OUT
            | AUTHENTICATING            // signed-in, session not yet resolved
            | READY  { accountId, displayName? }
            | REJECTED { code }         // terminal until user action
            | TRANSIENT_ERROR { code }  // signed-in retained; banner shown
```

### 3.2 View state (separately held by Router)

```
View ::= LANDING | SIGNIN | CURRICULUM | MENU | ACCOUNT
       | PAYWALL | GIFT_REDEEM
       -- REMOVED: OAUTH_FINISHING (B9, S2)
```

The two state spaces are independent: `View` is what the user is
looking at; `AuthState` is whether the system trusts them. The Body
renders by composing both. There is no `signedIn:boolean` value
anywhere in the codebase.

### 3.3 Valid transitions

```
AuthState transitions (driven by AuthProvider only):
  BOOT             → SIGNED_OUT             on (isLoaded, !isSignedIn)
  BOOT             → AUTHENTICATING         on (isLoaded, isSignedIn)
  AUTHENTICATING   → READY                  on /auth/session 200 (materialized)
  AUTHENTICATING   → READY                  on /auth/session/init 200
  AUTHENTICATING   → REJECTED               on definitive 4xx
  AUTHENTICATING   → TRANSIENT_ERROR        on transient failure (R3)
  TRANSIENT_ERROR  → READY                  on next protected call 200
  TRANSIENT_ERROR  → REJECTED               on definitive 4xx
  READY            → SIGNED_OUT             on signOut() completion
  REJECTED         → SIGNED_OUT             on signOut() completion
  SIGNED_OUT       → AUTHENTICATING         on provider isSignedIn=true event

View transitions (driven by user actions only):
  LANDING ↔ SIGNIN via CTA / Back
  LANDING → CURRICULUM | ACCOUNT | PAYWALL | MENU
  SIGNIN → pendingView | LANDING (on cancel)
  CURRICULUM ↔ MENU
  PAYWALL → GIFT_REDEEM → CURRICULUM
  ANY → LANDING on signOut() completion
```

### 3.4 Forbidden transitions (eliminated by construction)

| Forbidden | Eliminated by |
|---|---|
| `READY → SIGNED_OUT` due to transient backend failure | R3, TRANSIENT_ERROR is its own state |
| `SIGNIN → GATED_LOCKED → SIGNIN` oscillation | View body never reads provider/auth signals; gating is `AuthState === READY ? Body : <SigninBody>`. REJECTED is terminal; no auto re-issue. (I-I, R2, R4) |
| Entry to `OAUTH_FINISHING` | Removed from enum (B9) |
| Resurrection of deleted account | Lookup excludes `deleted_at IS NOT NULL`; init returns 409 `auth.account_deleted`. (B7, I-E) |
| Silent ownership transfer on email collision | Materializer keys ONLY on `auth_user_id`; no email-relink branch exists. (B8, I-D) |
| Sign-out leaving prior progress | `signOut()` is sequential and atomic; progress is server-side. (B6, I-F) |
| Two components with contradictory `signedIn` | There is no `signedIn` boolean; consumers read `AuthState` from one context. (B1, I-G) |

### 3.5 Convergence proof sketch

For any single failure, the system reaches a stable state in O(1)
AuthState transitions:

- Transient failure → AUTHENTICATING/TRANSIENT_ERROR; user input
  required to leave. No auto-re-issue. (R2)
- Definitive failure → REJECTED; user input required.
- Provider signed-out event → SIGNED_OUT in one transition; no re-fetch.

There is no cycle in the AuthState graph that does not require external
input. (R7)

---

## PHASE 4 — USER FLOW & NAVIGATION DESIGN

### 4.1 New user (Clerk mode)

```
LANDING/SIGNED_OUT
  └─ click "Set up my account — free"
       view = SIGNIN
  └─ user completes Clerk widget
       provider event → AuthState = AUTHENTICATING
  └─ AuthProvider:
       getToken() → JWT
       GET /auth/session → 200 { materialized: false, subject }
       POST /auth/session/init → 200 { account_id }
       GET /me/progress → 200 { module:1, unit:"unit-1", page:0 }
       AuthState = READY { accountId, displayName: claims.name? || null }
       view = pendingView ?? CURRICULUM
  └─ Body renders CurriculumRenderer at progress.unit/page (I-F)
```

### 4.2 Returning user

```
LANDING/BOOT
  └─ AuthProvider boot (§2.1)
       provider hydrates, isSignedIn=true
       getToken() → JWT
       GET /auth/session → 200 { materialized: true, account_id, display_name }
       AuthState = READY
  └─ Chrome shows email/displayName; Body shows landing-signed-in surface.
  └─ click "Continue learning"
       GET /me/progress → 200 { module, unit, page }
       view = CURRICULUM
```

### 4.3 Gated entry while SIGNED_OUT

```
LANDING/SIGNED_OUT
  └─ user clicks gated entry
       Router stores pendingView = CURRICULUM; view = SIGNIN
  └─ user completes provider flow → AUTHENTICATING → READY
  └─ Router consumes pendingView once: view = CURRICULUM. (§5.1)
```

### 4.4 Sign-out

```
ANY/READY
  └─ click "Sign out"
       signOut():
         1. await provider.signOut()           // drops Clerk session
         2. await fetch DELETE /auth/session   // optional revoke; best-effort
         3. clear AuthContext → SIGNED_OUT
         4. Router: view = LANDING
       // No localStorage progress to clear; progress is server-side.
       // No mock token in clerk build; no clerk keys in mock build.
       // (B6, I-C, T5)
```

### 4.5 Account deletion

```
ACCOUNT/READY
  └─ user confirms deletion
       POST /me/delete → 200
       trigger signOut()
       view = LANDING; AuthState = SIGNED_OUT
  └─ if user re-signs in with same provider subject:
       GET /auth/session → 401 auth.account_deleted (terminal)
       AuthState = REJECTED
       Body shows "Account deleted. Create a new account?" with single
       primary action that calls POST /me/recreate. (B7)
```

### 4.6 Navigation guarantees

- No redirect loops (I-I, R2): the only entrypoint to AUTHENTICATING is
  a provider event or initial boot. REJECTED does not re-enter it.
- No dead-ends (B9, C4): every View has a Back/Home affordance in
  `<Chrome>`; REJECTED state always offers SignOut or Retry-as-different-user.
- Reload non-regression (§6.2): reload triggers boot; boot resolves
  session; READY restores progress from server. (T-F1)
- Geragogy progression preserved (§5.1, §5.2): single render commit
  from SIGNIN to CURRICULUM at the user's resume point.

---

## PHASE 5 — FAILURE HANDLING MODEL

| Failure class | Condition | System behavior | UI outcome | Constraints |
|---|---|---|---|---|
| Provider SDK slow hydration | `isLoaded=false` | AuthState=BOOT; no protected request issued | `<BootBanner>` (visually distinct from blocked state) | T1, I-J, F-G4 |
| Token transiently null | isSignedIn=true, getToken() null | AuthState=AUTHENTICATING; bounded await (≤5s) | `<BootBanner>` | T3, R3 |
| JWKS lookup transient failure | `auth.transient_verifier_unavailable` | TRANSIENT_ERROR if from READY; AUTHENTICATING retries once if from boot | Banner: "Reconnecting…"; user stays on view | I-A, I-H, R3, R5, C2 |
| Token signature invalid / expired (after refresh attempt) | discriminated 401 | AuthState=REJECTED; provider session dropped | `<RejectedSurface>` | B5, R4, I-A |
| `auth.account_deleted` | GET /auth/session 401 with this code | AuthState=REJECTED | `<DeletedAccountSurface>` with "Create new account" | B7, I-E |
| `auth.email_already_owned` | POST /auth/session/init 409 | AuthState=REJECTED with code | `<EmailConflictSurface>` with admin-contact link | B8, I-D |
| Provider Backend API unreachable | irrelevant for any sync request | Background job retries | none (existing users unaffected) | I-H, R5, C2, C3, C5 |
| DB unavailable on auth path | 503 from /auth/session | AuthState=TRANSIENT_ERROR | Banner; user stays | R6 |
| DB unavailable on /api/landing/* | 503 from public route | route returns 503; landing fallback | unrelated to auth path | R6 |
| Mid-lesson 5xx on non-auth route | e.g. /api/curriculum/* | NOT propagated to AuthState | inline retry button; no eviction | R3, R6, F-G3 |
| FE/BE provider mismatch | /auth/config probe fails | FatalConfigError page; no children mount | ops alert | B3, T4, F6 |

**Convergence rules enforced:** no auto re-issue (R2); no transient
failure flips READY→SIGNED_OUT (R3); every definitive failure
terminates in REJECTED (R4, R7); no optional dependency failure denies
service to existing users (R5, I-H); routes are isolated (R6).

---

## PHASE 6 — DATA & ACCOUNT MODEL

### 6.1 Schema (post-migration; supersedes B12, B7, B8, I-D, I-E)

```sql
CREATE TABLE accounts (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id    UUID         NOT NULL UNIQUE,
    email           CITEXT       NULL,            -- B12: nullable
    display_name    VARCHAR(256) NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ  NULL
);
-- NO UNIQUE constraint on email. Prevents Race-B relink class entirely.
CREATE INDEX idx_accounts_email_active
    ON accounts (email)
    WHERE deleted_at IS NULL;

CREATE TABLE learner_progress (
    account_id    UUID         PRIMARY KEY
                  REFERENCES accounts(id) ON DELETE CASCADE,
    module        SMALLINT     NOT NULL DEFAULT 1,
    unit_id       VARCHAR(64)  NOT NULL DEFAULT 'unit-1',
    page_index    SMALLINT     NOT NULL DEFAULT 0,
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- REMOVED: sessions table (S1).
```

### 6.2 Account creation (B4, T6)

- Never during a GET. `POST /auth/session/init` is the sole creator.
- INSERT uses `ON CONFLICT (auth_user_id) DO NOTHING` (idempotent).
- If insert is no-op AND existing row's `deleted_at IS NOT NULL` →
  return `auth.account_deleted`. The `/me/recreate` endpoint clears
  `deleted_at` only with explicit user re-confirm.

### 6.3 Deletion (B7, I-E)

- `POST /me/delete`: set `deleted_at = now()`. Server triggers
  provider-side session revocation (best-effort).
- All lookups (`get_subject_account`) filter `deleted_at IS NULL`.
- On a subsequent valid token from same subject: `/auth/session` returns
  401 `auth.account_deleted`. FE renders DeletedAccountSurface.
  Explicit `POST /me/recreate` is the only path back.

### 6.4 Identity binding (B8, I-D)

- Subject → row mapping is monotonic by construction:
  `auth_user_id UNIQUE NOT NULL`; materializer never UPDATEs
  `auth_user_id`; no email-relink branch exists.
- Email collisions surface as 409 `auth.email_already_owned` with a
  documented admin-runbook resolution path (E7).
- Optional DB protection: trigger `prevent_auth_user_id_mutation` raises
  on `UPDATE accounts SET auth_user_id = ...`.

### 6.5 Progress (I-F)

- Server-authoritative. Client never persists progress to localStorage.
- `GET /me/progress` returns the row for the authenticated account.
  `PUT /me/progress` upserts.
- Cross-user contamination is structurally impossible. (T-F2)

---

## PHASE 7 — API CONTRACTS

### 7.1 `GET /auth/config` (public; no auth)

```json
200 OK
{ "provider": "clerk" | "mock", "version": "<git-sha>" }
```

FE asserts `provider === VITE_AUTH_PROVIDER` at boot. Mismatch → fatal.
(B3, T4)

### 7.2 `GET /auth/session` (Bearer required; pure read)

```json
200 OK (materialized)
{ "subject": "<sub>", "materialized": true,
  "account_id": "<uuid>", "email": "..."|null, "display_name": "..."|null }

200 OK (token valid but row missing)
{ "subject": "<sub>", "materialized": false,
  "account_id": null, "email": null, "display_name": null }

401 Unauthorized
{ "error": { "code": "<code>", "message": "<human-readable>" } }
```

**Discriminated reason codes** (B5, R1):

| code | meaning | FE handling |
|---|---|---|
| `auth.no_credential` | header missing | SIGNED_OUT |
| `auth.malformed` | token malformed | REJECTED |
| `auth.signature_invalid` | RS256 verify failed | REJECTED |
| `auth.expired` | exp claim past | REJECTED (after one SDK refresh attempt) |
| `auth.issuer_mismatch` | iss claim mismatch | REJECTED |
| `auth.subject_missing` | no `sub` claim | REJECTED |
| `auth.account_deleted` | row has `deleted_at` set | REJECTED → DeletedAccountSurface |
| `auth.transient_verifier_unavailable` | JWKS network failure | TRANSIENT_ERROR |
| `auth.transient_db_unavailable` | DB unreachable | TRANSIENT_ERROR |

The route never writes. (B4, I-B)

### 7.3 `POST /auth/session/init` (Bearer required; write event)

```json
200 OK
{ "account_id": "<uuid>" }

401 — same as /auth/session
409
{ "error": { "code": "auth.email_already_owned",
             "message": "An account already exists for this email." } }
```

Idempotent; safe to retry once on network errors.

### 7.4 `GET /me/progress` / `PUT /me/progress`

```json
GET 200
{ "module": 1, "unit_id": "unit-1", "page_index": 0,
  "updated_at": "2026-05-17T20:14:32Z" }

PUT body
{ "module": 1, "unit_id": "unit-2", "page_index": 3 }
PUT 200 { "ok": true }
```

### 7.5 `POST /me/delete`, `POST /me/recreate`

```
POST /me/delete
  200 OK { "ok": true }   // sets deleted_at; revokes provider session best-effort

POST /me/recreate
  200 OK { "account_id": "<uuid>" }   // clears deleted_at if subject matches
  409 { "error": { "code": "auth.account_not_deleted" } }
```

### 7.6 Universal error envelope

```json
{ "error": { "code": "<dot.namespaced.code>",
             "message": "<short human string>",
             "detail": <optional, structured> } }
```

Frontend has a single error-classifier function mapping `code` →
behavior class (`DEFINITIVE`, `TRANSIENT`, `SIGNED_OUT`,
`INFORMATIONAL`).

---

## PHASE 8 — SIMPLIFICATION IMPLEMENTATION

| ID | Removed / collapsed | Replacement | Why it improves correctness |
|---|---|---|---|
| S1 | `sessions` table; `SESSION_*` config | nothing (Bearer only) | Removes phantom data model. |
| S2 | `oauth_finishing` view | nothing | Satisfies B9; T-C1/T-C2 trivially true. |
| S3 | NavBar.whoami() | NavBar consumes `useAuth()` | One auth-state owner; B1, T7, I-G. |
| S4 | `db.commit()` in `get_optional_account` | dep is read-only; commit lives in `materialize()` | B4, I-B. |
| S5 | `ClerkSignOutButton`, `SignOutLink.{ClerkBranch,MockBranch}` | single `<SignOutButton>` calling `useAuth().signOut()` | B6, I-C. |
| S6 | `print(DIAG_AUTHZ_HEADER=…)`, `VERIFY_*` prints | structured logger with header redactor | B10. |
| S7 | `fetch_user_profile()` from sync request path | `ProviderProfileFetcher` background job | B11, C1, C3, C5; F2 eliminated. |
| S8 | Supabase env vars in `.env.example` | removed | Removes misleading config. |
| S9 | Email-collision relink in upsert | INSERT ON CONFLICT (auth_user_id) DO NOTHING | B8, I-D; FC3 eliminated. |
| S10 | `?reset=1` partial wipe | nothing (sign-out is now complete) | R8; F-G5 eliminated. |

Components removed from `frontend/src/`:

- `ClerkAuthBridge.tsx` (already orphan-on-disk).
- `ClerkAuthSync.tsx` (folds into AuthProvider).
- `ClerkTokenBridge.tsx` (interceptor moves into AuthProvider).
- `ClerkSignOutButton.tsx`, half of `SignOutLink.tsx` (collapsed).
- `lib/progress.ts` localStorage path (replaced by `/me/progress`).

Net component count delta on auth path: **8 → 3** (`ProviderShell`,
`AuthProvider`, `SignOutButton`).

---

## PHASE 9 — EXECUTION PLAN

> Detailed walkthrough lives in
> `docs/design/login-execution-playbook-2026-05-17.md`. Summary:

### Stage 0 — Telemetry (HARD GATE; precedes Stage 1)

E10. Counters and histograms instrumented and visible in staging
dashboards before any Stage 1 code lands.

### Stage 1 — Schema and identity alignment (BLOCKING)

B12, B3, T4, B11, B7, B8, I-D, I-E. M1 schema migration is the
**first commit**.

### Stage 2 — Auth model and state ownership (FOUNDATIONAL)

B1, B2, B4, B5, B10, T1, T2, T3, T6, T7, I-A, I-B, I-G, I-J.

### Stage 3 — Failure stabilization

C1–C5, R1–R8, B6, B9, T5, I-C, I-H, I-I.

### Stage 4 — UX/geragogy completion

I-F, §5.1–§5.3, §6.1–§6.2, F-G1–F-G5.

---

## PHASE 10 — TEST VALIDATION PLAN

For each acceptance test, the design feature(s) that guarantee passage:

| Test | Design feature(s) that guarantee it |
|---|---|
| T-A1 | AuthProvider single-resolution boot (T7); read-only `/auth/session` returns materialized=true; chrome and body both consume `useAuth()` (B1, I-G); progress fetched from server (I-F). |
| T-A2 | New-user path uses POST /auth/session/init (B4); verify_token is pure (C3); curriculum entry from `/me/progress` (I-F). No 401 because verifier doesn't depend on email or secret (B11, B12). |
| T-A3 | `verify_token` does not call provider Backend API; existing user's row already exists; `materialize()` not invoked on read path (B4, B11, C5, I-H). |
| T-B1 | Response interceptor maps 5xx to TRANSIENT_ERROR (R3); READY preserved; banner shown (B5, R1, I-A). |
| T-B2 | Provider sign-out event handler transitions atomically to SIGNED_OUT (B1); chrome and body re-render in same commit (I-G). |
| T-B3 | Backend emits `auth.signature_invalid`; FE classifier marks DEFINITIVE; AuthState=REJECTED; no further request (R2, R4). |
| T-C1 | Every View has Back/Home in `<Chrome>`; `OAUTH_FINISHING` removed (B9). |
| T-C2 | `OAUTH_FINISHING` not in View enum; setView call sites validated by exhaustive type check. |
| T-C3 | REJECTED is terminal-on-protected-path; AuthProvider does not auto-re-issue (R2); FC1 has no edge to follow. |
| T-D1 | AuthProvider gates protected calls on AuthState ∉ {BOOT, AUTHENTICATING-without-token} (T1, T2, T3); interceptor only attaches on non-null credential. |
| T-D2 | `<AuthProvider>` boot probe `GET /auth/config` asserts provider name; mismatch throws fatal (B3, T4). |
| T-E1 | `auth.transient_verifier_unavailable` → TRANSIENT_ERROR; READY preserved (R3, I-A, I-H). |
| T-E2 | `verify_token` does not call provider Backend API; existing-user path uses no Backend API (C3, I-H, R5). |
| T-E3 | Routes use independent DB sessions; landing routes are public (R6); auth path returns `auth.transient_db_unavailable`. |
| T-F1 | Reload triggers AuthProvider boot → READY → `/me/progress` GET → CurriculumRenderer at returned page (I-F). |
| T-F2 | Progress is server-side; localStorage progress removed; new user fetches their own `/me/progress` (B6, I-F). |
| T-F3 | Failures on `/api/curriculum/*` route through their own retry banner; do not feed AuthProvider (R3, R6). |
| T-G1 | `get_subject_account` filters `deleted_at IS NULL`; init returns 409 `auth.account_deleted`; `/me/recreate` is the only path back (B7, I-E). |
| T-G2 | Materializer keys only on `auth_user_id`; email-collision branch removed; 409 `auth.email_already_owned` (B8, I-D). |
| T-H1 | Logging middleware redacts Authorization/Cookie; `print()` removed (B10). |
| T-H2 | One auth resolution per boot enforced by AuthProvider (B1, T7). |
| T-H3 | `/auth/session` is read-only by code review; integration test inspects DB session for COMMITs (B4, I-B). |

---

## PHASE 11 — TRACEABILITY

| Design decision | Satisfies | Eliminates |
|---|---|---|
| Single `<AuthProvider>` owns auth state | B1, T7, I-G | F8, FC6 |
| Single axios interceptor in AuthProvider | B2, T2 | F6, audit §8 race-2 |
| `GET /auth/config` parity probe | B3, T4 | F6 mismatch class |
| `accounts.email` nullable; UNIQUE dropped | B12, B8, I-D | FC3, F5 |
| Materialization moved to `POST /auth/session/init` | B4, T6, I-B | FC1 (commit-on-read) |
| `verify_token` purified | C1, C3, B11 | F1 (cascade), F2, FC1 (cause), FC2 |
| Discriminated error codes | B5, R1 | FC1 (loop signal), FC2 (signal) |
| Transient vs definitive split | I-A, R3, R4, R7 | F1, F3, F4 (UI eviction) |
| `learner_progress` server-side; localStorage progress removed | I-F, B6 | F7, FC5 |
| Single `signOut()` ordered routine | B6, I-C, T5 | F6, F7 |
| `deleted_at` filter; `/me/recreate` explicit | B7, I-E | FC4 |
| `OAUTH_FINISHING` removed | B9, C4 | F9 |
| Header-redactor logging middleware | B10 | F10 |
| `ProviderProfileFetcher` background job | C3, I-H, R5, C5 | F4 (existing-user denial) |
| BOOT distinct from SIGNED_OUT | I-J, T1, F-G4 | F-G4 |
| TRANSIENT_ERROR distinct from SIGNED_OUT | I-A, R3, F-G3 | FC1 silent eviction |
| REJECTED terminal until user action | I-I, R2, R4, R7 | FC1 oscillation |
| Router consumes `pendingView` once at READY | §5.1, §5.3 | F-G1 |
| Chrome & Body subscribe to AuthContext only | I-G, §5.3 | F-G2 |

---

## QUALITY-BAR ASSERTIONS

- **Zero infinite loops possible:** every AuthState terminal node
  (REJECTED, SIGNED_OUT, READY) requires external event to transition
  out. No automatic re-issue. (T-C3)
- **Zero false signed-out states:** READY → SIGNED_OUT requires either a
  provider sign-out event or a definitive 401 reason. (T-B1, T-E1, T-F3)
- **Zero cross-user data leakage:** progress is server-side, scoped by
  account_id. (T-F2)
- **Complete convergence:** AuthState graph is a DAG except for
  user-driven re-entries. (T-C3, T-E1, T-E2)

---

# END OF SYSTEM DESIGN
