# Functional Requirements Document (FRD) — Mynaani Authentication

**Document ID:** FRD-AUTH-001  
**Version:** 1.0  
**Date:** 2026-08-27  
**Status:** Accepted  
**Source:** `.ai/intake/2026-08-27-magic-link-auth.md`; ADR 0027  
**Owner:** Mynaani Engineering Team  

---

## 1. Scope

Defines what the Magic.link authentication feature must do for end users and the system.

## 2. Functional requirements

| ID | Requirement | Priority | Acceptance criteria |
|---|---|---|---|
| FR-001 | Add `magic` as a supported `AUTH_PROVIDER` value | High | `AUTH_PROVIDER=magic` bootstraps `MagicAuthProvider`; `mock` still works |
| FR-002 | Authenticate users via email magic links | High | User enters email; Magic sends link; SDK returns DID token on success |
| FR-003 | Validate DID tokens server-side and extract `email` + stable subject | High | Invalid/expired/malformed tokens return discriminated `auth.*` codes |
| FR-004 | Materialize `accounts` rows on first verified sign-in | High | First sign-in creates an `accounts` row with `email` and `auth_user_id` |
| FR-005 | Preserve existing `AuthProvider.tsx` session resolution contract | High | BOOT → SIGNED_OUT → AUTHENTICATING → READY flow unchanged |
| FR-006 | Support mock fallback for dev/tests | High | `AUTH_PROVIDER=mock` works without Magic keys in CI |
| FR-007 | Update public privacy/terms to reference Magic | Medium | `privacy.html` and `terms.html` no longer mention Clerk |
| FR-008 | Update CI/deploy secrets for `MAGIC_*` environment variables | Medium | `deploy.yml`, `secrets-sync.sh`, `.env.example` include `MAGIC_*` |

## 3. User flows

### 3.1 Sign-in (magic link)
1. Learner opens `/signin`.
2. Enters email and selects "Send me a sign-in link."
3. Magic sends email.
4. Learner clicks the link in their email.
5. Frontend receives DID token and stores it as the Bearer credential.
6. `AuthProvider` resolves the session via `/auth/session` and `/auth/session/init`.
7. Learner is redirected to `/welcome`.

### 3.2 Sign-out
1. Learner selects "Sign out" in account settings.
2. AuthProvider clears the DID token from localStorage.
3. Backend session ends; no server-side state cleanup is required.

## 4. Data requirements

- `accounts.auth_user_id` is derived as `uuid5(NAMESPACE, email)`.
- `accounts.email` is populated from the validated DID token claim.
- `accounts.display_name` is optional.

## 5. Interface requirements

- `SignInPage.tsx` must remain RenderGuard-compliant.
- The sign-in copy must be calm: "We will send you a one-time link. There is no password to remember."
- No loading spinners that create urgency.

## 6. Related documents

- BRD-AUTH-001: `docs/requirements/BRD.md`
- PRD-AUTH-001: `docs/requirements/PRD.md`
