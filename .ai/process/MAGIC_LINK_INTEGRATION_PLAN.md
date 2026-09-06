> **Deprecated:** legacy platform retired; production runs on Railway.

# Magic.link Integration Plan

**Process:** v9.51
**Date:** 2026-08-27
**Status:** Plan issued; implementation pending
**ADR:** `docs/decisions/0027-magic-link-auth.md`
**Intake:** `.ai/intake/2026-08-27-magic-link-auth.md`

---

## 0. External prerequisites

1. Create a Magic Auth application at `https://dashboard.magic.link`.
2. Copy the **Publishable API Key** (`pk_live_...` or `pk_test_...`) for the frontend.
3. Copy the **Secret API Key** (`sk_live_...` or `sk_test_...`) for the backend.
4. (Optional) configure the Magic email template branding and redirect URI.

---

## 1. Backend

### 1.1 Add dependency
- `pyproject.toml` `dependencies`:
  ```toml
  "magic-admin>=2.4.0,<2.6.0",
  ```
- Run `pip install -e .` in the venv.

### 1.2 Add configuration
- `backend/core/config.py`:
  ```python
  AUTH_PROVIDER: str = "mock"
  MAGIC_API_SECRET_KEY: str = ""
  MAGIC_PUBLISHABLE_KEY: str = ""
  ```

### 1.3 Implement DID verifier
- Create `backend/services/magic_verifier.py`:
  - Initialize `magic_admin.Magic(api_secret_key=settings.MAGIC_API_SECRET_KEY)`.
  - Expose `validate_did_token(token: str) -> AuthClaims` that:
    - calls `magic.Token.validate(token)`
    - catches `DIDTokenExpired`, `DIDTokenInvalid`, `DIDTokenMalformed`
    - returns `AuthClaims` with `auth_user_id = uuid5(NAMESPACE, email)`, `email`, `subject = email`
  - Fails closed (returns `None` or raises `AuthError` mapped to `auth.*` codes).

### 1.4 Implement `MagicAuthProvider`
- In `backend/services/auth_provider.py` add:
  ```python
  class MagicAuthProvider:
      def verify_credential(self, credential: str) -> Optional[AuthClaims]:
          from backend.services.magic_verifier import validate_did_token
          return validate_did_token(credential)
      def fetch_user_profile(self, subject: str) -> Optional[UserProfile]:
          return None  # email already in DID claim
  ```
- Update `get_auth_provider()`:
  ```python
  if provider == "magic":
      return MagicAuthProvider()
  ```

### 1.5 Update `auth_verifier.py`
- Add `_verify_magic(token: str) -> AuthClaims` using `get_auth_provider()`.
- Update `verify_token()` branch table:
  - `mock` -> `_verify_mock`
  - `magic` -> `_verify_magic`
  - else -> `auth.transient_verifier_unavailable`

### 1.6 Tests
- `backend/tests/test_magic_verifier.py`
  - Mock `magic_admin.Magic`.
  - Test valid DID -> `AuthClaims`.
  - Test expired/invalid/malformed -> `AuthError`.

---

## 2. Frontend

### 2.1 Add dependency
- `frontend/package.json`:
  ```json
  "magic-sdk": "~33.9.0"
  ```
- Run `npm install` at the repo root.

### 2.2 Add environment
- `frontend/src/lib/env.ts`:
  ```typescript
  export const MAGIC_PUBLISHABLE_KEY: string = (
    import.meta.env.VITE_MAGIC_PUBLISHABLE_KEY ?? ""
  ).trim();
  ```
- `frontend/.env.example`:
  ```
  VITE_MAGIC_PUBLISHABLE_KEY=
  ```

### 2.3 Create Magic client
- `frontend/src/lib/magic.ts`:
  ```typescript
  import { Magic } from "magic-sdk";
  import { MAGIC_PUBLISHABLE_KEY } from "./env";

  export const magic = MAGIC_PUBLISHABLE_KEY
    ? new Magic(MAGIC_PUBLISHABLE_KEY)
    : null;
  ```

### 2.4 Update `SignInPage.tsx`
- On submit, call `magic?.auth.loginWithMagicLink({ email, showUI: true })`.
- On resolve, store the returned DID token in localStorage as `noni.magic_token`.
- Call `notifyAuthChanged()`.

### 2.5 Update `AuthProvider.tsx`
- `useCredentialSource()` should use `noni.magic_token` when `AUTH_PROVIDER === "magic"`.
- The session timeout (30 min) should consider DID lifetime; may need refresh logic later.

### 2.6 Tests
- `frontend/src/api/__tests__/auth.test.ts`:
  - Mock `magic-sdk` and the DID token exchange.
- `frontend/src/auth/__tests__/AuthProvider.test.tsx`:
  - Add `VITE_MAGIC_PUBLISHABLE_KEY` to the env mock.

---

## 3. Infrastructure and secrets

### 3.1 Update environment files
- `infra/.env.example`
- `infra/.env.prod.sops.yaml`
- `frontend/.env.example`
- `frontend/Dockerfile` build args
- `docker-compose.yml`
- `.github/workflows/deploy.yml`
- `scripts/setup-infrastructure.ps1`
- `scripts/audit-legacy-platform-secrets.ps1`
- `scripts/auto_deploy.py`
- `infra/scripts/secrets-sync.sh`

Add:
- `MAGIC_API_SECRET_KEY`
- `VITE_MAGIC_PUBLISHABLE_KEY`
- `AUTH_PROVIDER=magic` / `VITE_AUTH_PROVIDER=magic`

Remove any remaining Clerk placeholders in these files.

### 3.2 Update public pages
- `frontend/public/privacy.html`
- `frontend/public/terms.html`
Replace Clerk references with Magic.link.

---

## 4. Process and documentation

1. Update `docs/deferred-decisions.md` to mark auth provider as decided.
2. Update `docs/CURRENT_STATE.md`.
3. Update `.ai/repo-landscape/package-inventory.*` with `magic-admin` and `magic-sdk`.
4. Update the knowledge graph if appropriate.
5. Regenerate PRA and Nelson evidence after implementation.

---

## 5. Verification checklist

| Step | Evidence |
|---|---|
| `pip install -e .` succeeds | venv has `magic-admin` |
| `npm install` succeeds | `package-lock.json` updated |
| `npm run type-check` | pass |
| `npm run test:unit` | 120+ pass, no Clerk references |
| `npm run build` | bundle verified, `VITE_MAGIC_PUBLISHABLE_KEY` replaced |
| `pytest backend/tests/test_magic_verifier.py` | pass |
| `pytest backend/tests/test_a3_auth.py` | pass (with Magic DID test fixture) |
| `npm audit` / `pip-audit` | 0 criticals |

---

*Generated under Process v9.51.*
