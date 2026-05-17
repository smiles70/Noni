# Execution Playbook — Noni Login Redesign

**Date:** 2026-05-17
**Companion to:** `docs/design/login-redesign-2026-05-17.md`
**Frozen reference:** `login-redesign-v1` (this doc + the design doc).
**Acceptance source:** `backend/tests/test_login_constraints.py`,
`frontend/src/__tests__/login_contract.test.ts`,
`docs/audits/login-system-constraints-2026-05-17.md`.

> This document supplies the **stage gates**, **PR checklist**, and
> **engineer/LLM execution prompt** that wrap the design.
> Section 1 of the source package (test skeletons) is already shipped
> at the file paths above and is intentionally not re-listed here.

---

## SECTION 2A — STAGE 0 TELEMETRY GATE (MANDATORY BEFORE STAGE 1)

This is a **hard gate**. Stage 1 and Stage 2 implementation MUST NOT
begin until this is complete.

**Reason:** discriminated 401 (B5) cannot be validated without
telemetry; constraint compliance cannot be measured without signals
(E10).

### Required metrics (backend)

```
# Counter: auth outcomes by reason (B5)
auth_session_outcomes_total{
  code = "auth.no_credential" |
         "auth.malformed" |
         "auth.signature_invalid" |
         "auth.expired" |
         "auth.issuer_mismatch" |
         "auth.subject_missing" |
         "auth.account_deleted" |
         "auth.transient_verifier_unavailable" |
         "auth.transient_db_unavailable" |
         "ok.materialized" |
         "ok.unmaterialized"
}

# Counter: account materialization attempts
account_materialize_attempts_total{ result = "success" | "conflict" | "deleted" }

# Counter: email-collision detection (B8)
email_collision_observed_total

# Counter: FE/BE auth-state disagreement (I-G; emitted by FE)
signedin_render_disagreement_total

# Histogram: auth-session resolution latency
auth_session_latency_ms
```

### Required instrumentation rules

- Every `/auth/session` and `/auth/session/init` response MUST emit a
  labeled outcome metric. (B5)
- Every `materialize()` attempt MUST emit success/conflict/deleted.
- Frontend MUST emit `signedin_render_disagreement_total` from a single
  invariant probe inside `<AuthProvider>` if any consumer ever observes
  a state contradicting the context. (I-G)

### Hard block condition

```
IF telemetry is not visible in staging dashboards:
    STOP — do not proceed to Stage 1 or Stage 2.
```

---

## SECTION 2 — STAGE 1 IMPLEMENTATION WALKTHROUGH

**Critical rule:** Stage 1 MUST begin with the M1 schema migration. No
application logic changes are allowed before M1 completes.
**Reason:** B12 (schema-token compatibility) is a blocking constraint;
all auth fixes depend on it.

### STEP 1 — M1 schema migration (FIRST COMMIT in the redesign branch)

```sql
-- M1: relax email; remove relink risk surface.
ALTER TABLE accounts ALTER COLUMN email DROP NOT NULL;
DROP INDEX IF EXISTS accounts_email_key;          -- unique index
CREATE INDEX idx_accounts_email_active
    ON accounts (email)
    WHERE deleted_at IS NULL;
```

**Guarantees:**

- Backwards compatible (existing rows already have email).
- Reversible (can re-add the unique index after audit, before any
  NULL-email rows exist).
- Removes the synchronous dependency on the external profile fetch.

**Validate immediately after running:**

- Existing user sign-in still works end-to-end.
- An `INSERT INTO accounts (auth_user_id) VALUES (...)` with no email
  succeeds.
- T-A3 (existing user, no optional secret) passes against staging.

```
IF M1 fails or any validation regresses:
    STOP — roll back the migration, fix root cause, re-attempt.
```

### STEP 2 — Identity invariants (B8, I-D)

- Confirm `auth_user_id UNIQUE NOT NULL` is in place (already true in
  current schema; verify after M1).
- Add `prevent_auth_user_id_mutation` trigger:

  ```sql
  CREATE OR REPLACE FUNCTION prevent_auth_user_id_mutation()
    RETURNS TRIGGER AS $$
  BEGIN
    IF NEW.auth_user_id IS DISTINCT FROM OLD.auth_user_id THEN
      RAISE EXCEPTION 'auth_user_id is immutable';
    END IF;
    RETURN NEW;
  END; $$ LANGUAGE plpgsql;

  CREATE TRIGGER trg_accounts_auth_user_id_immutable
    BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION prevent_auth_user_id_mutation();
  ```

- Verify by writing a `UPDATE accounts SET auth_user_id = ...` test
  expecting a raised exception. T-G2 must pass.

### STEP 3 — Provider parity endpoint (B3, T4)

```python
# backend/api/routes/auth.py
@router.get("/auth/config")
def auth_config():
    return {"provider": settings.AUTH_PROVIDER, "version": settings.GIT_SHA}
```

```ts
// frontend/src/auth/AuthProvider.tsx (boot)
const remote = await fetch("/auth/config").then(r => r.json());
if (remote.provider !== import.meta.env.VITE_AUTH_PROVIDER) {
  throw new FatalConfigError(
    `provider mismatch: FE=${import.meta.env.VITE_AUTH_PROVIDER} BE=${remote.provider}`
  );
}
```

### STEP 4 — Deploy gating assertion

The probe must fail loud in dev AND prod; no partial mismatch tolerated.

**Hard block condition:**

```
IF T-D2 (provider mismatch fails fast) does not pass:
    STOP — DO NOT PROCEED to Stage 2.
```

---

## SECTION 3 — PR REVIEW CHECKLIST

Use this checklist before merging ANY auth-related PR. Any `NO` where
the answer is required to be `YES`, or any `YES` where the answer is
required to be `NO`, is a hard reject.

### Pre-stage gates

- [ ] Telemetry (E10) is live in staging dashboards.
- [ ] Schema migration (M1) completed successfully and was the first
      commit on the redesign branch.
- [ ] `/auth/config` provider-parity endpoint is deployed and enforced.

> 🚫 If any of the above is false → PR is blocked.

### Auth core

- [ ] Is there EXACTLY ONE auth-state owner? (B1)
- [ ] Is there EXACTLY ONE interceptor attaching tokens? (B2)
- [ ] Are there ZERO whoami-style "truth" endpoints used as the auth
      signal? (F-A1)
- [ ] Does any auth check perform a DB write? (B4 → MUST be NO)
- [ ] Does any auth logic depend on email being present? (B12 → MUST be NO)
- [ ] Does any path require `CLERK_SECRET_KEY` to succeed? (B11 → MUST be NO)

### State + timing

- [ ] Can any API fire before token exists? (T3 → MUST be NO)
- [ ] Is auth state resolved before gated rendering? (T1, I-J)
- [ ] Can `signedIn` flip false due to transient failure? (R3 → MUST be NO)

### Failure handling

- [ ] Are ALL auth errors discriminated? (B5)
- [ ] Is 401 ever interpreted generically? (MUST be NO)
- [ ] Can failure cause repeated retries without user action?
      (R2 → MUST be NO)

### Telemetry enforcement

- [ ] Does every `/auth/session` and `/auth/session/init` response
      emit a metric? (B5)
- [ ] Are discriminated error codes visible in dashboards?
- [ ] Are materialization attempts tracked
      (success/conflict/deleted)?

### Failure detection

- [ ] Can you observe `auth.transient_*` vs definitive in
      logs/metrics?
- [ ] Can you confirm no silent 401 collapse exists?

### Data safety

- [ ] Is email required for auth? (B12 → MUST be NO)
- [ ] Is `auth_user_id` the only identity key? (B8 → MUST be YES)
- [ ] Can two users share one account row? (MUST be NO)

### User experience (geragogy)

- [ ] Can user loop between login and app? (MUST be NO)
- [ ] Can progress leak across users? (MUST be NO)
- [ ] Does login ALWAYS lead to curriculum or pendingView? (§5.1 — REQUIRED)

### Security

- [ ] Any logs print token / header / cookie? (B10 → MUST be NO)
- [ ] Any implicit credential fallback? (MUST be NO)

### Architecture

- [ ] Does the design introduce new coupling? (C3 violation check)
- [ ] Are auth responsibilities separated (verify vs DB-read vs
      DB-write vs external profile fetch)? (C3)

---

## SECTION 4 — IMPLEMENTATION EXECUTION PROMPT

Use this verbatim to guide an engineer or LLM during the build:

> You are implementing an authentication system under strict
> constraints defined by the System Constraint Model
> (`login-constraints-v1`).
>
> Before writing any application logic:
>
> 1. You MUST implement schema migration M1 (B12) as the FIRST commit.
> 2. You MUST instrument telemetry (E10) and confirm staging
>    visibility BEFORE Stage 2 begins.
>
> You are NOT allowed to continue if:
>
> - telemetry is not observable in staging dashboards
> - schema is incompatible with the token model (`accounts.email` is
>   still NOT NULL or still UNIQUE)
> - the `/auth/config` probe is not in place
>
> During implementation:
>
> - Treat auth verification as a pure function (no DB writes, no
>   external API calls).
> - Treat token availability as asynchronous; never assume
>   synchronous availability at component mount.
> - Treat 401 as multi-class (discriminated reason codes), never
>   boolean.
> - Treat sign-out as a single ordered, atomic operation; partial
>   sign-out is forbidden.
> - Treat progress as server-authoritative; never persist progress to
>   localStorage.
>
> If any change violates:
>
> - B1 (single auth-state owner)
> - B2 (one credential pipeline)
> - B4 (no write on read)
> - B5 (discriminated errors)
> - B11 (no optional secret on success path)
> - B12 (schema-token compatibility)
> - T3 (token before request)
>
> STOP and refactor. All code must satisfy constraints before
> proceeding.
>
> You are building a system that must be **correct by construction**.

---

# END OF EXECUTION PLAYBOOK
