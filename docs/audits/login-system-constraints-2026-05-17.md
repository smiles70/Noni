# System Constraint Model — Noni Login Domain

**Date:** 2026-05-17
**Source:** Phase 1–26 discovery audit
(`docs/audits/login-discovery-2026-05-17.md`).
**Mode:** constraints only. No solutions. Every clause derives from a
discovered fact.
**Frozen reference tag:** `login-constraints-v1`.

---

## 1. SUCCESS_STATE

`SUCCESS_STATE` is the conjunction of conditions that must hold
simultaneously for the system to be considered correct for a given user
session:

```
SUCCESS_STATE := AUTH_VALID
              ∧ BACKEND_ACCEPTED
              ∧ UI_CONSISTENT
              ∧ NAV_CORRECT
              ∧ LEARNING_ENTRY_REACHED
              ∧ PROGRESS_BOUND_TO_ACCOUNT
```

Definitions:

- **AUTH_VALID** — Identity provider reports a hydrated, signed-in
  subject AND a non-null credential is currently obtainable from that
  provider.
- **BACKEND_ACCEPTED** — A protected backend endpoint, called with the
  obtained credential, returned a 2xx with a stable account identifier.
- **UI_CONSISTENT** — Every component currently mounted reads the same
  auth state value; no two mounted components hold contradictory views
  of "signed in".
- **NAV_CORRECT** — The currently rendered view is the view requested
  by the user (or the deterministic post-signin destination), not a
  fallback induced by a contradictory error.
- **LEARNING_ENTRY_REACHED** — When the user's intent was to learn,
  the rendered view is the curriculum entry point that corresponds to
  their persisted progress for the authenticated account.
- **PROGRESS_BOUND_TO_ACCOUNT** — The curriculum progress visible to
  the user is the progress associated with the account identified in
  `BACKEND_ACCEPTED`, not progress associated with a different (or no)
  account.

`SUCCESS_STATE` must be an *assertable* predicate at runtime, not a
colloquial label.

---

## 2. BUILD CONSTRAINT LIST (ranked)

1. **B1 — Single auth-state owner.** There must be exactly one module
   that holds the authoritative `signedIn` value. Every other component
   must read it; no component may compute its own copy via an
   independent network call.
2. **B2 — One credential pipeline.** The Authorization header must be
   attached by exactly one mechanism per build. Two interceptors
   writing the same header are forbidden.
3. **B3 — Build/runtime provider symmetry.** Frontend `AUTH_PROVIDER`
   (build-baked) and backend `AUTH_PROVIDER` (runtime) must be enforced
   to match by a startup assertion that fails the deployment loud.
4. **B4 — No write effects on read endpoints.** Endpoints whose
   semantic is "read current state" must not commit DB rows. Account
   materialization must occur on a write event, not on whoami-equivalent
   reads.
5. **B5 — Discriminated 401.** The backend must distinguish the cause
   of authentication failure (invalid token, expired token, missing
   claim, missing email, profile fetch failure, DB unavailable, account
   deleted, account not yet materialized). The wire response must carry
   a stable machine-readable reason code.
6. **B6 — Disjoint sign-out.** Sign-out must purge every client-state
   surface that the user perceives as belonging to "their session":
   current provider's credential, mock token (if present), persisted
   curriculum progress keyed to the previous account.
7. **B7 — Deletion is terminal.** A successfully deleted account must
   not be re-materializable by a subsequent valid token from the same
   identity-provider subject without an explicit re-creation event.
8. **B8 — One Clerk subject ↔ at most one account row.** Email-collision
   relink must not silently transfer ownership of an existing account
   row to a different identity-provider subject.
9. **B9 — No unreachable view states.** Every view value the
   application can hold must have at least one entry transition AND at
   least one exit transition. Orphan states are a build error.
10. **B10 — No diagnostic credential leakage.** No log line, in any
    environment, may contain any prefix of any token, header, or cookie
    value.
11. **B11 — No dependence on optional secrets for the success path.**
    The critical path to `SUCCESS_STATE` must not require any
    environment variable that is documented as optional.
12. **B12 — Schema-token compatibility.** A required DB column may not
    require a value that the chosen token format does not reliably
    provide; column nullability must match token reality.

---

## 3. SYSTEM INVARIANTS (runtime guarantees)

- **I-A.** If the identity provider reports `signedIn=true` AND
  credential acquisition succeeds AND no transport error occurred, then
  a protected endpoint call must not respond as "not signed in" for any
  reason other than verified credential rejection (signature, exp, iss,
  sub).
- **I-B.** A protected read endpoint must not write to durable storage
  as a precondition of returning success.
- **I-C.** Sign-out is monotonic. After a sign-out completes, no
  client-side surface continues to assert any identity tied to the
  prior session.
- **I-D.** Every account row corresponds to at most one
  identity-provider subject for its lifetime; the (subject → row)
  mapping is monotonic — once established, the row's subject does not
  silently change.
- **I-E.** A row marked deleted must not satisfy any "current account"
  lookup, regardless of any otherwise-valid token presented for it.
- **I-F.** Persisted user progress is scoped by authenticated account
  identity; it must not be rendered for any other account.
- **I-G.** No two mounted components may simultaneously render based on
  contradictory values for "is the user signed in".
- **I-H.** A failure of any optional dependency (provider Backend API,
  JWKS cache miss network round-trip, Clerk Backend lookup) must not
  cascade to denial of service for users whose accounts are already
  materialized.
- **I-I.** No view transition driven solely by an error response may
  produce a state that re-issues the same request without external user
  action.
- **I-J.** Auth state resolution must complete before any view that
  depends on auth state renders its decision. Rendering during the
  unresolved window must be visually distinguishable from rendering in
  either resolved branch.

---

## 4. AUTH DOMAIN CONTRACT

### 4.1 Source of truth

- **Identity owner:** the configured identity provider (Clerk in
  production, mock in dev/tests).
- **Authentication-state owner:** the identity provider's hydrated SDK
  state on the client.
- **Authorization (entitlement) owner:** the backend, evaluated
  per-request against persisted purchases/grants.
- **Account-record owner:** the backend database, keyed by provider
  subject.

These four owners are distinct; no role may be assumed by a different
owner.

### 4.2 Authentication guarantees

- Provider signed-in state is treated as **asynchronously hydrated**;
  the rest of the system must consume an explicit "ready" signal, not a
  synchronous boolean.
- Credential acquisition (`getToken()` equivalent) is treated as
  asynchronous and may return null in a transient window after the SDK
  reports signed-in. That window must be a first-class state, not
  collapsed into "not signed in".
- A backend rejection of a credential is informational about the
  credential, not a re-statement of provider state. The frontend must
  not infer provider sign-in/sign-out from backend response codes
  alone.
- Backend credential verification must be a pure function of (token,
  configured verification material). It must not depend on the success
  of any other network call to declare a token valid or invalid.

### 4.3 Forbidden auth patterns

- **F-A1:** Treating any backend endpoint's response as the source of
  truth for "is the user signed in".
- **F-A2:** Performing any DB write as a *precondition* of credential
  verification or whoami.
- **F-A3:** Collapsing distinct failure causes (signature, exp,
  missing-claim, profile-fetch, DB-down) into a single 401 with no
  machine-readable reason.
- **F-A4:** Assuming a credential is synchronously available at the
  moment a component mounts.
- **F-A5:** Two or more components independently fetching auth state
  from the network.
- **F-A6:** Build-time selection of provider on one side without
  runtime cross-check on the other.
- **F-A7:** Logging any prefix of any credential, header, or cookie at
  any level in any environment.
- **F-A8:** Allowing a deleted account to be resurrected by a
  subsequent valid token without an explicit re-creation flow.

---

## 5. GERAGOGY (LEARNING EXPERIENCE) CONTRACT

### 5.1 Learning entry guarantee

After a successful sign-in, the user must reach the curriculum entry
point that matches their persisted progress for the authenticated
account, in a single, observable transition. No interstitial "you
appear to be signed out" surface may flash between sign-in completion
and learning entry.

### 5.2 Progression guarantees

- Every user-initiated action must produce one of: (a) advance, (b)
  explicit reversible pause with reason, (c) explicit terminal failure
  with surfaced reason. Implicit oscillation between two views is
  forbidden.
- A transient backend or network failure must not cause progression to
  reset, rewind, or re-prompt for sign-in if the user is in fact signed
  in (per §4.2).
- A user who has reached lesson N and refreshes must return to lesson N
  if their identity is still valid; under no circumstance may they
  silently land on lesson 1 of unit 1.

### 5.3 Experience consistency

- The visible identity (e.g., email shown in the chrome) must match the
  account that owns the visible progress at all times.
- No view transition may discard the user's stated intent (the
  destination they were heading to before a sign-in detour) without a
  deterministic reason.
- The "where am I" state must be readable from one place at all times:
  visible view label, current unit/page indicator, and identity chrome
  must agree.

### 5.4 Forbidden geragogy patterns

- **F-G1:** Sign-in completion that lands the user back on the sign-in
  surface.
- **F-G2:** Progress display that belongs to a different account on the
  same browser.
- **F-G3:** Mid-lesson eviction to sign-in caused by transient backend
  failure when the provider still reports signed-in.
- **F-G4:** A "loading" state that is indistinguishable from a "blocked"
  state.
- **F-G5:** A reset/escape hatch that wipes only some of the user's
  perceived state, leaving a confusing partial reset.

---

## 6. USER FLOW & NAVIGATION CONTRACT

### 6.1 Interaction guarantees

- Every primary action surfaces a deterministic next state; no action
  is permitted to be a no-op when the user expects movement.
- An action that cannot currently be honored must surface a visible,
  accurate reason; silent failure is forbidden.
- The currently rendered chrome (NavBar, sign-out controls, account
  label) must match the currently rendered body's auth assumption.

### 6.2 Navigation guarantees

- No transition pair (X → Y → X) may occur as a direct consequence of
  a single deterministic failure mode.
- Every reachable state must have at least one user-visible exit (Back,
  Cancel, or completion).
- A gated route must be reachable when its gate conditions are met, in
  one transition, from at least one user-discoverable surface.
- A direct page reload while signed in must restore the user to a state
  at least as advanced as their persisted progress; reload must not be
  a regression.

---

## 7. STATE TRANSITION RULES

### 7.1 Valid transitions (must remain expressible)

- `BOOT_UNKNOWN → LANDING_OUT` on resolved-not-signed-in.
- `BOOT_UNKNOWN → LANDING_IN` on resolved-signed-in.
- `LANDING_OUT → SIGNIN` on user CTA.
- `LANDING_IN → CURRICULUM` on user CTA.
- `SIGNIN → <pendingView | CURRICULUM>` on sign-in completion.
- `CURRICULUM → MENU` on user CTA; `MENU → CURRICULUM` on user CTA.
- `LANDING_IN → ACCOUNT`; `ACCOUNT → LANDING_OUT` on sign-out;
  `ACCOUNT → LANDING_OUT` on confirmed deletion.
- `CURRICULUM → PAYWALL` on terminal-of-free-track gate.
- `PAYWALL → GIFT_REDEEM → CURRICULUM`.
- Any state → `LANDING_OUT` on confirmed sign-out.

### 7.2 Forbidden transitions (must not exist)

- `SIGNIN → GATED_LOCKED → SIGNIN` chain in a single failure cycle.
- `LANDING_IN → SIGNIN` due to a transient backend failure while the
  identity provider still reports signed-in.
- Any transition to a state that has no exit transition
  (`OAUTH_FINISHING` as currently defined).
- `ACCOUNT_DELETED → CURRICULUM` via a subsequent sign-in on the same
  provider subject.
- `SIGN_OUT → LANDING_OUT_with_prior_user_progress_visible`.
- Any transition that produces a UI where chrome and body disagree
  about `signedIn`.
- Any auto-issued repeat of the same failing protected request without
  external user action.

---

## 8. TEMPORAL GUARANTEES

- **T1 — Hydration before decision.** No component that branches on
  auth state may render its decision branch before the auth-state-owner
  has emitted "ready".
- **T2 — Interceptor before request.** No protected request may be
  issued until the credential-attaching mechanism has been installed
  and is live for the active provider.
- **T3 — Token before whoami.** A whoami-equivalent call in provider
  mode must not be issued until the provider reports signed-in AND a
  non-null credential has been observed.
- **T4 — Provider parity before traffic.** The frontend's baked
  provider and the backend's runtime provider must agree before any
  authenticated traffic is routed; a mismatch must abort the boot, not
  produce 401s.
- **T5 — Sign-out completion before re-entry.** Sign-out cleanup
  (provider, mock token if applicable, progress) must complete before
  the user is permitted to re-enter SIGNIN.
- **T6 — Account materialization is idempotent and non-blocking on
  read.** The first-sight materialization may occur asynchronously
  relative to whoami; whoami's success must not require materialization
  to have *just now* completed.
- **T7 — One auth resolution per boot.** The system must resolve auth
  state exactly once per page load; subsequent re-resolutions must be
  triggered only by explicit events (sign-in, sign-out, provider
  session change), not by component mounts.

---

## 9. FAILURE & RECOVERY RULES

### 9.1 Handling guarantees

- **R1.** Every failure on the auth path must produce a discriminated
  reason code observable to the frontend.
- **R2.** No failure may cause an automatic re-issue of the same
  request without user action.
- **R3.** A transient failure (network, JWKS lookup, provider Backend
  API) must not flip `signedIn` from true to false unless the
  credential itself has been definitively rejected.
- **R4.** A definitive failure (token rejected by signature, exp, iss)
  must transition to `LANDING_OUT` exactly once and remain stable until
  the user acts.

### 9.2 Failure isolation

- **R5.** Failure of an optional dependency (provider Backend API,
  profile lookup) must not deny service to users whose accounts are
  already materialized.
- **R6.** A failure in one route's dependency must not propagate to
  unrelated routes.

### 9.3 Recovery rules

- **R7.** The system must converge to either a stable success state or
  a stable, surfaced-error state within a bounded number of transitions
  for any single failure mode. Unbounded retry loops are forbidden.
- **R8.** Recovery must not require the user to know about dev-only
  escape hatches (`?reset=1` etc.) to escape a stuck state.

---

## 10. CRITICAL PATH PROTECTIONS

### 10.1 Critical path

```
LANDING_OUT → SIGNIN → SUCCESS_STATE → CURRICULUM(entry-point)
```

### 10.2 Collapse prevention

- **C1.** No single optional configuration value (e.g., a Backend-API
  secret) may gate the critical path.
- **C2.** No single network dependency may have a failure mode that
  converts the entire signed-in app into a sign-in loop.
- **C3.** No single function may simultaneously own (a) credential
  verification, (b) external profile lookup, and (c) durable account
  creation.
- **C4.** No state on the critical path may be entered without a
  defined exit to either success or surfaced error.
- **C5.** The critical path must succeed for an existing user even if
  every optional sub-dependency is unavailable, provided the credential
  itself is verifiable.

---

## 11. SYSTEM BOUNDARY CONTRACTS

### 11.1 Frontend ↔ Identity provider

- **Guaranteed by provider:** an asynchronous hydration signal; an
  asynchronous credential acquisition that may transiently return null;
  a sign-out that drops local provider state.
- **Must not be assumed:** that signed-in implies credential is
  immediately available; that the credential carries any specific
  application claim (e.g., email); that sign-out propagates to the
  application's other state surfaces.

### 11.2 Frontend ↔ Backend

- **Guaranteed by backend:** verification result is a pure function of
  (token, configured verification material); 2xx body shape stable;
  failure responses carry discriminated reason codes (per B5).
- **Must not be assumed:** that 401 means "credential bad"; that whoami
  is side-effect-free under all backend versions; that a successful
  response materializes any cross-tab state.

### 11.3 Backend ↔ Database

- **Guaranteed by DB:** uniqueness of `(auth_user_id)` and `(email)`
  enforced; `accounts` row uniquely identifies an account.
- **Must not be assumed:** that NOT-NULL columns can always be
  populated from token claims; that a soft-deleted row should be
  treated as live by lookup paths; that two distinct provider subjects
  sharing an email is a benign condition.

### 11.4 Backend ↔ Identity-provider Backend API

- **Guaranteed by provider:** profile lookups are best-effort,
  rate-limited, may transiently fail.
- **Must not be assumed:** that profile lookups will succeed within the
  lifetime of a single request; that they are part of the synchronous
  critical path.

---

## 12. SIMPLIFICATION DIRECTIVES

- **S1.** Remove the unused `sessions` table and all `SESSION_*`
  config.
- **S2.** Remove the orphan `oauth_finishing` view.
- **S3.** Remove duplicated whoami in `NavBar`; consume App's auth
  state instead.
- **S4.** Remove `db.commit()` from any read-only auth dependency
  path.
- **S5.** Collapse `ClerkSignOutButton` and
  `SignOutLink.ClerkBranch`/`MockBranch` into one provider-aware
  sign-out surface.
- **S6.** Remove diagnostic `print()` statements that emit any portion
  of any credential or header.
- **S7.** Remove the optional Clerk Backend API call from the
  synchronous critical path.
- **S8.** Remove legacy Supabase env entries from `.env.example` once
  auth-domain redesign lands.
- **S9.** Remove email-collision relink from `_upsert_account`.
- **S10.** Replace ad-hoc `?reset=1` partial wipe with a single,
  complete sign-out path.

---

## 13. ENGINEERING RISK MAP

- **E1.** Migrating away from `accounts.email NOT NULL UNIQUE` requires
  a Postgres migration with backfill and re-indexing. Sequence: schema
  change → backfill → constraint relaxation → app change.
- **E2.** Eliminating commit-on-read in `whoami` requires moving
  account materialization to an explicit event.
- **E3.** Build-time/runtime provider mismatch enforcement requires
  emitting the FE-baked provider into the bundle as an asserted value
  AND adding a backend startup probe.
- **E4.** Discriminated 401 reason codes are a wire-format change.
  Frontend must be tolerant of both shapes during the rollover window.
- **E5.** Removing the duplicated NavBar whoami changes API request
  volume and timing; existing dashboards may need re-baselining.
- **E6.** Collapsing sign-out surfaces requires that the new component
  be tested against both providers in CI.
- **E7.** Email-collision relink removal converts a previously silent
  class of cases into surfaced errors; admin runbook required.
- **E8.** Deletion semantics change (B7) requires deciding the deletion
  ↔ provider-session interaction; this crosses a service boundary.
- **E9.** Rebuild discipline: any change to `VITE_AUTH_PROVIDER` policy
  mandates a frontend image rebuild.
- **E10.** Telemetry blind spots (audit §22) must be filled *before* a
  redesign, otherwise success cannot be measured.

---

## 14. ACCEPTANCE TEST SUITE

### A. Critical path

- **T-A1.** Returning user with a valid provider session opens the
  app.
  - Expected: reaches `SUCCESS_STATE`; visible curriculum entry matches
    persisted progress; no SIGNIN view rendered at any point.
  - Forbidden: any frame in which user shown SIGNIN; any frame in which
    `signedIn` is false.
- **T-A2.** New user completes provider sign-up.
  - Expected: reaches `SUCCESS_STATE` and lands on the curriculum entry
    point with progress=clean.
  - Forbidden: SIGNIN re-rendered after completion; whoami called more
    than once before render; any 401 surfaced to the user.
- **T-A3.** Critical path with optional secret unavailable (existing
  user).
  - Expected: signs in successfully; reaches `SUCCESS_STATE`.
  - Forbidden: 401, redirect to SIGNIN, "stuck" state.

### B. Auth correctness

- **T-B1.** Provider signed-in; backend transient 5xx on protected
  route.
  - Expected: UI does NOT flip `signedIn` to false; user remains in
    current view; transient-error surface shown.
  - Forbidden: redirect to SIGNIN; view eviction; auto-retry burst.
- **T-B2.** Provider signed-out (sign-out in another tab).
  - Expected: tab transitions to `LANDING_OUT` exactly once; chrome
    and body agree on `signedIn=false` within one render.
  - Forbidden: chrome/body disagreement frame.
- **T-B3.** Token rejected by signature/exp.
  - Expected: response carries discriminated reason; UI transitions to
    `LANDING_OUT` once.
  - Forbidden: indistinguishable 401; loop back into SIGNIN.

### C. State transitions

- **T-C1.** Probe every reachable view for an exit transition.
  - Expected: every reachable view has at least one user-visible exit.
  - Forbidden: any view whose only exit is page reload.
- **T-C2.** Attempt to enter `OAUTH_FINISHING`.
  - Expected: state unreachable (or removed entirely).
  - Forbidden: state reachable but has no exit.
- **T-C3.** Force the FC1 chain (provider signed-in + whoami 401).
  - Expected: bounded transitions, then stable error surface.
  - Forbidden: SIGNIN ↔ GATED_LOCKED oscillation across more than one
    cycle.

### D. Temporal

- **T-D1.** Boot in provider mode with slow SDK hydration.
  - Expected: no protected request issued before hydration ready
    signal; no `signedIn` flip until ready.
  - Forbidden: any protected request without Authorization header in
    network log; any `signedIn=false` rendered while provider
    hydrating.
- **T-D2.** Boot with mismatched FE/BE provider.
  - Expected: deployment startup fails loudly; no user-visible 401
    cascade.
  - Forbidden: silent 401 storm.

### E. Failure & recovery

- **T-E1.** Single JWKS network outage during a session.
  - Expected: existing user's view does not regress; explicit transient
    surface.
  - Forbidden: forced sign-in, forced sign-out, infinite retry.
- **T-E2.** Provider Backend API unreachable.
  - Expected: all already-materialized users continue to function.
  - Forbidden: any signed-in user perceives denial of service.
- **T-E3.** DB unavailable for 1 second.
  - Expected: failures discriminated; landing page envelopes still
    load.
  - Forbidden: signed-in users evicted to SIGNIN.

### F. Geragogy

- **T-F1.** User on lesson N refreshes.
  - Expected: returns to lesson N (or further) for the same account.
  - Forbidden: drops to lesson 1 unit 1.
- **T-F2.** User signs out, second user signs in on same browser.
  - Expected: second user's progress is theirs.
  - Forbidden: any first-user progress, email, or chrome shown to
    second user.
- **T-F3.** Mid-lesson transient backend hiccup.
  - Expected: lesson stays open; user informed only if failure is
    durable.
  - Forbidden: eviction to SIGNIN; reset to lesson 1.

### G. Account lifecycle

- **T-G1.** Delete account, then attempt to sign in again with same
  provider subject.
  - Expected: cannot resurrect; explicit "create new account" surface
    required.
  - Forbidden: silent re-creation; access to prior progress.
- **T-G2.** Two distinct provider subjects share an email.
  - Expected: second subject does NOT relink first subject's row;
    surfaced error.
  - Forbidden: silent ownership transfer.

### H. Hygiene & observability

- **T-H1.** Inspect logs across all environments for credential
  leakage.
  - Expected: zero log lines containing any prefix of any token,
    header, or cookie.
  - Forbidden: any `DIAG_AUTHZ_HEADER`-style leakage.
- **T-H2.** Inspect mounted components for duplicate auth-state
  network calls.
  - Expected: at most one whoami-equivalent call per boot.
  - Forbidden: NavBar (or any other component) issuing its own whoami.
- **T-H3.** Inspect read endpoints for write effects.
  - Expected: no INSERT/UPDATE/DELETE issued during any
    whoami-equivalent request.
  - Forbidden: any commit during a read.

---

# END OF SYSTEM CONSTRAINT MODEL
