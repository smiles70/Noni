# PS-BID17-018 — Apex mynaani.com redirects to http:// (downgrade)

**Status:** owner-gated (domain/DNS config) | **Severity:** P1
**Source:** production cross-check 2026-09-20

## Problem statement

`https://mynaani.com/` returns `301 → http://www.mynaani.com/` — the
redirect target is plain HTTP. Browsers that haven't cached HSTS follow
the redirect over cleartext before re-upgrading; every apex hit briefly
traverses an insecure hop. `mynaani.com/caregiver` also returns 404
rather than redirecting (apex serves a bare 404 body, not the SPA).

## Verified

- `curl -I https://mynaani.com/` → `301`, `Location: http://www.mynaani.com/`
- `www.mynaani.com` serves 200 + full SPA on all routes.

## Remediation

- Fix the apex→www redirect target to `https://www.mynaani.com` at the
  registrar/Pages custom-domain layer (Cloudflare: check the apex
  domain config / redirect rule).
- Optionally enable HSTS `includeSubDomains; preload` on www.

## Acceptance

- `https://mynaani.com/` → `301` to `https://www.mynaani.com/`.
