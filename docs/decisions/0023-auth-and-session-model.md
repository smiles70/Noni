# ADR 0023 — Authentication and Session Model

Date: 2026-05-11
Status: Accepted

## Context

The architect review (Google Principal critique) flagged several auth-shaped risks:

- Ambiguous session storage ("cookie or JWT in memory")
- No specified session revocation
- JWKS caching and failure-mode behavior unspecified
- Foreign key from app schema into Supabase-managed `auth.users` table couples our schema to a vendor schema

This ADR closes all four.

## Decision

### Identity provider

Supabase Auth, with Google as the sole OAuth provider at launch. Email/password and other providers are explicitly deferred.

### Token verification

The backend verifies Supabase-issued JWTs against the Supabase JWKS endpoint with:

- JWKS cached in-process for 10 minutes
- Required claims validated: `aud`, `iss`, `exp`, `nbf`
- Clock-skew tolerance: ±30 seconds
- Fail-closed on JWKS unreachability: requests requiring a valid token return 503 and an `auth.degraded` envelope, never a permissive fallback

### Session model

A successful OAuth callback exchanges the Supabase JWT for **our own server-issued session**:

1. The backend verifies the Supabase JWT exactly once.
2. The backend creates a row in `sessions` with `session_token_hash = sha256(token)`, `expires_at`, and the requester's IP / user-agent.
3. The backend returns an HTTP-only cookie:
   - `HttpOnly; Secure; SameSite=Lax; Path=/`
   - Signed with `SESSION_SECRET` (HMAC), 30-day expiration
   - Value: random 256-bit token; the cookie carries the token, never the Supabase JWT
4. Subsequent requests look up the session row by hash; revoked or expired sessions return 401 and an `auth.signed_out` envelope.

The Supabase JWT is never retained client-side or server-side beyond the callback handshake.

### Session revocation

Server-side row update: `UPDATE sessions SET revoked_at = now(), revocation_reason = ?`. Effective immediately on next request. Supported revocation reasons: user sign-out, admin intervention, password/identity change at provider, suspicious activity.

### Logical identity boundary

`accounts.auth_user_id UUID UNIQUE` references Supabase `auth.users.id` **logically, not via a foreign key.** Reasons:

- Supabase has changed `auth.users` shape historically; FKs into a vendor-managed table create migration risk.
- Allows the system to be re-pointed at another identity provider (Auth.js, Clerk, Authlib direct) by changing only the callback handler.
- Application-layer integrity is enforced by the callback (insert-or-fetch-by-`auth_user_id`).

### CSRF

`SameSite=Lax` covers top-level navigation. State-changing endpoints (`POST`, `PATCH`, `DELETE`) additionally require a `X-Requested-With: fetch` header set by the SPA's fetch wrapper, providing defense in depth.

### Rate limiting

The sign-in callback and any unauthenticated POST endpoints are rate-limited at the Cloudflare WAF (primary) and at the application layer via `rate_limit_counters` (defense in depth). See ADR 0024.

## Consequences

- Session revocation is row-level and instant.
- Vendor identity churn (Supabase outages, schema changes) does not impact our session lifecycle once a session is issued.
- All session metadata is observable in one table; support can identify and revoke sessions deterministically.

## Reversibility

- Changing identity provider: replace the `/auth/callback` handler; no schema change required (logical `auth_user_id` accepts any UUID-like external id).
- Migrating from cookies to bearer tokens for a future mobile client: add a `sessions.bearer_token_hash` column; the same `sessions` row backs either transport.

## References

- `docs/architecture/SYSTEM.md`
- `docs/architecture/SCHEMA.md` (tables `accounts`, `sessions`)
- ADR 0022 (vendor topology)
