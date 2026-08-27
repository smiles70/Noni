# Universal Intake Artifact: Magic.link Authentication Provider

**Intake Date:** 2026-08-27
**Artifact Type:** Change Request / Architecture Decision / Integration Plan
**Source:** User request via Devin session
**Intake Agent:** Process v9.51 Universal Intake Agent (UIA)
**Priority:** HIGH — closes deferred auth-provider decision
**Status:** Accepted; implementation plan issued

---

## Artifact Input

### User Request Summary
User requests selection and planned integration of **Magic.link** as the production authentication provider for Mynaani, replacing the removed Clerk integration. Reasons:
- Geragogy: passwordless email magic links are ideal for older adults (no passwords to remember, no password-reset loops).
- No auto-renew or dark-pattern surface; pay-as-you-go with generous free tier.
- Fits the existing Vite React frontend + FastAPI Python backend.

### Current State
- **Current Provider:** `mock` (`MockAuthProvider` in `backend/services/auth_provider.py`)
- **Removed Provider:** Clerk (fully decommissioned in previous session)
- **Deferred Decision:** Authentication provider tracked in `docs/deferred-decisions.md`
- **Open Need:** A real, production-ready identity provider that aligns with Mynaani values.

### Desired State
- **Target Provider:** Magic.link
- **Frontend:** `magic-sdk@~33.9.0` triggers `loginWithMagicLink`; stores the returned DID token as the Bearer credential.
- **Backend:** `magic-admin@~2.4.0` validates DID tokens in a new `MagicAuthProvider`; maps `email` -> `auth_user_id`; persists to `accounts`.
- **Configuration:** `AUTH_PROVIDER=magic`, `MAGIC_PUBLISHABLE_KEY` (frontend build arg), `MAGIC_API_SECRET_KEY` (backend secret).

---

## UIA Analysis

### Artifact Classification
- **Category:** Architecture Decision / Vendor Integration
- **Sub-category:** Identity Provider Selection and Integration
- **Impact Level:** HIGH — touches auth, security, deployment, privacy policy, tests
- **Governance Level:** Tier 1 — single-vendor, off-the-shelf SDKs

### Requirements Extraction

#### Functional Requirements
1. **FR-001:** Add Magic.link as a supported `AUTH_PROVIDER` value.
2. **FR-002:** Authenticate users via email magic links (passwordless).
3. **FR-003:** Validate DID tokens server-side and extract `email` + stable subject.
4. **FR-004:** Materialize `accounts` rows on first verified sign-in.
5. **FR-005:** Preserve existing `AuthProvider.tsx` session resolution contract.
6. **FR-006:** Support mock fallback for dev/tests.
7. **FR-007:** Update public privacy/terms to reference Magic instead of Clerk.
8. **FR-008:** Update CI/deploy secrets for `MAGIC_*` environment variables.

#### Non-Functional Requirements
1. **NFR-001:** No passwords, no dark patterns, no urgency framing.
2. **NFR-002:** No auto-renew or subscription vendor lock-in.
3. **NFR-003:** Token lifetime must be short (DID default 15 min) and refreshed only with user action.
4. **NFR-004:** Geragogy-first copy on the sign-in page.
5. **NFR-005:** Maintain WCAG 2.1 AA compliance.
6. **NFR-006:** Maintain the closed-world UI contract (RenderGuard).

#### Technical Requirements
1. **TR-001:** Add `magic-admin>=2.4.0,<2.6.0` to Python dependencies.
2. **TR-002:** Add `magic-sdk@~33.9.0` to `frontend/package.json`.
3. **TR-003:** Implement `MagicAuthProvider` class conforming to `AuthProvider` protocol.
4. **TR-004:** Implement `backend/services/magic_verifier.py` with fail-closed DID validation.
5. **TR-005:** Update `backend/core/config.py` with `MAGIC_*` settings.
6. **TR-006:** Update `auth_verifier.py` to route `magic` provider to the new verifier.
7. **TR-007:** Update `frontend/src/components/SignInPage.tsx` to call `magic.auth.loginWithMagicLink`.
8. **TR-008:** Update `frontend/src/auth/AuthProvider.tsx` to use the DID token from localStorage and the new env.
9. **TR-009:** Update `infra/.env.example`, `.env.prod.sops.yaml`, `deploy.yml`, `secrets-sync.sh`.
10. **TR-010:** Add unit + integration tests for the Magic verifier and sign-in flow.

---

## v9.51 Traceability

- **Requirement traceability:** Intake → ADR 0027 (`docs/decisions/0027-magic-link-auth.md`)
- **Source provenance:** User request + external Magic.link documentation
- **Evidence to produce:**
  - Unit test: `backend/tests/test_magic_verifier.py`
  - Integration test: `backend/tests/test_a3_auth.py` expanded for Magic DID tokens
  - Frontend test: `frontend/src/api/__tests__/auth.test.ts` updated
  - Build: `npm run build` bundle verification
  - Audit: `npm audit` and `pip-audit` clean

---

## Implementation Owner

Mynaani Engineering Team (see `.github/CODEOWNERS`)

## Trigger

Closes the deferred auth-provider bundle; pulls the first real older-adult pilot one step closer to deployment.
