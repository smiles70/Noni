# Intake — ADMIN-LOGIN-001: internal staff console login at /admin

**Date:** 2026-09-07 · **Process:** v9.51 · **Requester:** owner · **Gate:** staging → prod

## Request

`/admin` shows a centered-logo login card: username + password + Login
button, matching site design. Authenticated staff see the admin console.
Two permanent staff usernames (case-insensitive): `kim`, `steven`.
Password: owner-supplied, NOT committed to the repo (env var, hashed).
Not Magic-link, not Stripe — internal employer-only access.

## Security decisions (must be explicit, per Process evidence rules)

- Password lives ONLY as `ADMIN_CONSOLE_PASSWORD_SHA256` env var —
  constant-time hash compare server-side. Plaintext never in code/git.
- Usernames live in `ADMIN_CONSOLE_USERS` env var (default `kim,steven`),
  normalized lowercase — case-insensitive per request.
- Login issues an HMAC-signed staff session token (`staff:`-prefixed
  Bearer) keyed by `ADMIN_SESSION_SECRET` (env; fail closed if unset).
- `require_staff` accepts EITHER an allowlisted account id (existing
  path) OR a valid staff session token. Learner surface unchanged.
- Login endpoint is rate-limited (5 attempts/min/IP) — a credential
  endpoint without throttling is not enterprise-acceptable.
- **Recorded caveat:** shared credential removes per-actor attribution in
  OrgAuditLog (`actor_account_id` will carry the shared staff identity).
  Recommended follow-up: per-user credentials or SSO. Implemented per
  owner instruction.
- **Recorded caveat:** prod still runs AUTH_PROVIDER=mock; the staff
  session is independent of that path and remains safe, but the rest of
  prod auth remains impersonable until Magic keys are set.
