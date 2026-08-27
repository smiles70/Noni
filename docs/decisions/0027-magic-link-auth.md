# 0027 - Authentication provider: Magic.link passwordless magic links

## Status

Accepted (pre-implementation; binds future code).

## Context

The codebase previously used Clerk for production authentication. Clerk was fully removed because the project had no access to a live Clerk instance and because the team wanted a provider that better supports Mynaani's geragogy-first constraints (no dark patterns, no urgency, no subscription auto-renew). The `AUTH_PROVIDER=mock` path was left as a bridge for dev/tests.

The auth-provider decision is the most important open item in `docs/deferred-decisions.md`. It blocks any pilot with real older adults because persistent, attributable accounts are required for per-learner state.

### Constraints from ARCHITECTURE.md
- Rule 5 (No Urgency Framing): no timers or countdowns.
- Rule 6 (No Dark Patterns): no hidden costs or deceptive copy.
- Rule 7 (Explicit Review): no automated actions without user confirmation.
- Rule 8 (Cognitive Safety First): the flow must be calm and forgiving for older adults.

### Vendor evaluation (external evidence)
- **Magic.link:** passwordless email magic links; no passwords to remember or reset; clear per-send or MAU pricing; no auto-renew by default; simple Vite + FastAPI integration via `magic-sdk` (client) and `magic-admin` (server).
- **NextAuth.js:** framework-first for Next.js/SvelteKit/Express; no supported FastAPI adapter; would require a separate Node auth service.
- **Auth0:** mature but adds another third-party dependency; pricing and UI less aligned with Mynaani values.
- **Supabase Auth:** re-implementing a previously decommissioned path is not justified.
- **Custom FastAPI JWT:** high security responsibility; not needed with a geragogy-aligned off-the-shelf option.

## Decision

1. **Select Magic.link** as the production authentication provider.
2. **Auth flow:**
   - User enters email on the `SignInPage` and presses "Send me a sign-in link".
   - `magic-sdk` calls `magic.auth.loginWithMagicLink({ email })`.
   - Magic sends the user an email with a secure magic link.
   - On success the SDK returns a DID token (default 15-minute lifetime) which is stored as the Bearer credential in localStorage under `noni.magic_token`.
   - AuthProvider's interceptor attaches the DID token to every `apiClient` request.
   - Backend `MagicAuthProvider` validates the DID token with `magic-admin`, extracts `email` and `issuer`, and hashes them into a stable `auth_user_id`.
3. **Backend routing:**
   - `backend/services/magic_verifier.py` owns DID token validation.
   - `MagicAuthProvider` in `backend/services/auth_provider.py` implements the existing `AuthProvider` protocol.
   - `auth_verifier.py` adds a `magic` branch.
4. **Frontend routing:**
   - `frontend/src/lib/magic.ts` initializes `new Magic(VITE_MAGIC_PUBLISHABLE_KEY)`.
   - `SignInPage.tsx` uses the Magic SDK; `AuthProvider.tsx` treats the DID token like any other Bearer token.
5. **Configuration keys:**
   - `VITE_MAGIC_PUBLISHABLE_KEY` — frontend build-time, non-secret, dashboard public key.
   - `MAGIC_API_SECRET_KEY` — backend secret, from Magic Dashboard.
   - `AUTH_PROVIDER=magic` (backend) and `VITE_AUTH_PROVIDER=magic` (frontend).
6. **Mock fallback remains:** `AUTH_PROVIDER=mock` continues to work for dev/tests and CI; Magic-specific code is isolated behind the `AuthProvider` protocol and build-time env.
7. **Version pins:**
   - `magic-admin>=2.4.0,<2.6.0` (Python; v2.4.0 published 2026-05-06, vetted).
   - `magic-sdk@~33.9.0` (npm; v33.9.0 published 2026-07-02, vetted).

## Consequences

- **Positive:**
  - No passwords for older adults to remember or reset.
  - No subscription or auto-renew in the auth vendor contract.
  - Magic sends the transactional email, removing the need for a separate email-provider decision for auth.
  - SDKs are well documented; integration fits the existing `AuthProvider` protocol.
- **Negative / Risks:**
  - External vendor dependency; migration away later requires another provider replacement.
  - Magic's free tier has limits; cost must be modeled before launch.
  - DID tokens are short-lived (15 min); a session refresh strategy must be designed for long learning sessions.
  - Email deliverability is outside our control.
- **Open follow-ups:**
  - Session refresh / re-auth policy for 15-minute DID tokens.
  - Billing/pricing impact on the Magic free tier.
  - Update public privacy/terms pages to name Magic.link.

## Related

- ADR 0023 (auth and session model)
- `docs/deferred-decisions.md`
- `.ai/intake/2026-08-27-magic-link-auth.md`
- `.ai/process/MAGIC_LINK_INTEGRATION_PLAN.md`
