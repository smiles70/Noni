# Auth Provider Assessment — Post-Clerk Decommission

**Process:** v9.51 (traceable evidence, external verifiable sources)
**Date:** 2026-08-26
**Status:** Clerk removed; mock auth verified; production provider is deferred.

---

## 1. What was done

### 1.1 Clerk removal
- Removed `@clerk/clerk-react` from `frontend/package.json` and lockfile.
- Removed `ClerkProvider` and `noniTheme` from `frontend/src/main.tsx`.
- Removed `useClerkAuth` and the Clerk branch from `frontend/src/auth/AuthProvider.tsx`.
- Removed `ClerkSignInBranch` and `SignIn`/`useAuth` Clerk imports from `frontend/src/components/SignInPage.tsx`.
- Removed `backend/services/clerk_verifier.py`.
- Removed `ClerkAuthProvider` and Clerk circuit breaker from `backend/services/auth_provider.py`.
- Removed Clerk verification path from `backend/services/auth_verifier.py`.
- Removed `CLERK_*` settings from `backend/core/config.py`.
- Updated `backend/api/routes/auth.py` parity probe to report `AUTH_PROVIDER` directly (no Clerk hard-coding).
- Updated `backend/app/main.py` warnings.
- Removed Clerk secrets from `infra/.env.example` and `infra/.env.prod.sops.yaml`.
- Removed Clerk references from `scripts/setup-infrastructure.ps1`, `scripts/audit-fly-secrets.ps1`, `scripts/auto_deploy.py`, `infra/scripts/secrets-sync.sh`, `.github/workflows/deploy.yml`, `SECURITY.md`, `docs/ONBOARDING.md`, `docs/TEST_STRATEGY.md`, `docs/ROLLBACK.md`, and `docs/CURRENT_STATE.md`.

### 1.2 Mock auth verification
- `npm run type-check` ✅
- `npm run test:unit` ✅ 120 passed, 15 expected fail
- `npm run build` ✅ bundle verified (no localhost refs, API URL correct)
- `pytest backend/tests/test_iscs.py` + `test_geragogy_signals.py` + `test_a3_auth.py` ✅ 18 passed (3 DB-backed tests blocked by no Postgres)

The mock provider (`MockAuthProvider`) is functional and is now the only identity provider in the code path.

---

## 2. Research question: Can NextAuth.js be used for Noni?

### 2.1 External sources

1. **NextAuth.js FAQ** — `https://next-auth.js.org/faq`  
   > "NextAuth.js was originally designed for use with Next.js and Serverless."

2. **Auth.js installation docs** — `https://authjs.dev/getting-started/installation`  
   Framework packages listed: Next.js, Qwik, SvelteKit, Express. Vite/React is not a first-class framework package. `next-auth` is the Next.js package; `@auth/core` is framework-agnostic but requires a framework integration.

3. **GitHub issue #2294** — "Make `next-auth` framework agnostic (Vite, Vue, Express...)"  
   Maintainer update: SvelteKit and Nuxt proof-of-concepts exist; Vite integration is possible but undocumented and requires custom wrappers.

4. **GitHub discussion #3462** — "next-auth without next.js"  
   Confirms that using `next-auth` outside Next.js either needs a tiny Node/Express backend wrapper or a separate Next.js auth-only app.

5. **CoderLegion / Auth.js v5** — `https://coderlegion.com/24071/how-to-add-auth-js-nextauth-v5-authentication-in-next-js-16-2026`  
   Describes Auth.js v5 as built for full-stack frameworks (Next.js), with adapters, route handlers, and middleware/proxy.

### 2.2 Assessment

| Fit criterion | NextAuth.js / Auth.js for Noni |
|---|---|
| Frontend is Vite + React (no Next.js) | ❌ No first-class package. Vite/React integration is possible only via custom `@auth/core` wrapper or a separate Node auth service. |
| Backend is FastAPI (Python) | ❌ NextAuth/Auth.js expects Node.js/Express route handlers. There is no official FastAPI adapter. |
| Deployment is Fly.io + Cloudflare Pages | ⚠️ Would require a Node auth micro-service on Fly or Cloudflare Pages functions; adds infrastructure. |
| Geragogy needs (calm, password-optional, no dark patterns) | ⚠️ Depends on provider chosen. Credentials provider is possible but requires custom DB adapter. |
| Open-source and self-hosted option | ✅ `@auth/core` is open source, but a full implementation still needs Node. |
| Implementation effort | **High** for Noni's stack: would require either (a) rewriting/migrating the auth surface to a Node service, or (b) writing a custom `@auth/core` ↔ FastAPI bridge. |

**Conclusion:** NextAuth.js is **not a natural fit** for the current Noni stack. The codebase is a Vite React SPA plus a FastAPI backend. NextAuth/Auth.js's documented integrations are Next.js, SvelteKit, SolidStart, and Express. There is no supported path to drop it into a Vite+FastAPI app without adding a Node auth layer or a custom bridge.

---

## 3. Recommended alternatives (v9.51-compatible)

For a production provider that fits the existing Python/Vite stack, the following are more direct:

| Option | Why it fits | Trade-offs |
|---|---|---|
| **Magic.link** | Passwordless, email-magic-link flow is excellent for older adults; simple API; can be verified in FastAPI. | External service; cost at scale. |
| **Auth0** | Mature, can issue RS256 JWTs, FastAPI can verify via JWKS just like the old Clerk path. | External dependency; pricing. |
| **Supabase Auth** | Already using Supabase for Postgres; can be self-hosted; built-in RLS. | Previously decommissioned; would need re-implementation. |
| **Custom FastAPI OAuth** | `authlib` or `fastapi-users` with Google OAuth; full control; zero vendor lock-in. | Higher implementation and security responsibility. |

The existing `AuthProvider` protocol in `backend/services/auth_provider.py` was intentionally left provider-agnostic. A new production provider can be added as a new class implementing `AuthProvider(Protocol)` without touching the `AuthProvider.tsx`/session flow.

---

## 4. If NextAuth.js is still chosen: required steps

For v9.51 traceability, the following steps would be required:

1. **Add a Node/Express auth service** on Fly.io (e.g., `auth.noni.fly.dev`) running `@auth/express` with `@auth/core`.
2. **Implement an `Auth.js` configuration** with a provider that fits geragogy (e.g., Google OAuth, Magic.link, or Credentials with email/OTP).
3. **Expose `/api/auth/*` endpoints** in the Node service for sign-in, sign-out, callback, session, and CSRF.
4. **Cross-domain cookie/session handling** between `noni-web.pages.dev` and `auth.noni.fly.dev` (CORS, `SameSite`, secure, HttpOnly).
5. **Issue a backend-verifiable token** (e.g., signed JWT or opaque token) that the FastAPI `/auth/session` endpoint can validate.
6. **Update `AuthProvider.tsx`** to call the NextAuth endpoints instead of mock localStorage.
7. **Update `backend/services/auth_provider.py`** with a new provider class matching the token shape.
8. **Write ADR and update `docs/deferred-decisions.md`** to close the auth-provider decision.
9. **Add new PRA evidence** (test flow, provider parity, security review).
10. **Generate new Nelson/PRA artifacts** with the provider change recorded.

---

## 5. Update: 2026-08-27 selection and implementation

Magic.link has been selected and implemented (Phases 1-3) as the production authentication provider. See:
- Intake: `.ai/intake/2026-08-27-magic-link-auth.md`
- ADR: `docs/decisions/0027-magic-link-auth.md`
- Integration plan: `.ai/process/MAGIC_LINK_INTEGRATION_PLAN.md`
- Implementation research: `.ai/process/MAGIC_IMPLEMENTATION_RESEARCH.md`
- Deferred decision closed: `docs/deferred-decisions.md`
- Code: `backend/services/magic_verifier.py`, `backend/services/auth_provider.py`, `frontend/src/lib/magic.ts`, `frontend/src/components/SignInPage.tsx`

## 6. Immediate recommendation

1. Implement the steps in `.ai/process/MAGIC_LINK_INTEGRATION_PLAN.md`.
2. Keep `AUTH_PROVIDER=mock` for dev/tests and CI.
3. Do **not** pursue NextAuth.js for the current Vite+FastAPI stack unless the team is willing to add and operate a Node auth micro-service.
4. After integration, regenerate PRA and Nelson evidence and update the knowledge graph.

---

*Generated with external verifiable sources under Process v9.51.*
