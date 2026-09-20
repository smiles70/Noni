# PS-BID17-006 — Resend end-to-end delivery unverified (inbox confirmation)

**Status:** narrowed by deep dive — see below | **Severity:** P1 verification gap
**Source:** staging integration check 2026-09-20

## Problem statement

`POST /api/v1/site/contact-inquiry` returned `delivered:true` — which
proves the inquiry was queued to the Resend background task, not that
Resend delivered to `help@mynaani.com`. The only proof of the full
delivery path is the email landing in the inbox.

## Verified vs. not

- ✅ Endpoint live, schema validation (422 on bad shape), honeypot
  fail-quiet contract (`delivered:false`, no send), retry hardening,
  task queued.
- ❓ Actual Resend API call + inbox delivery — backend-side, invisible
  from HTTP.

## Probe sent

Marked inquiry: `integration-check@mynaani.test`, subject:
"Contact request — Integration Check", body prefixed
"STAGING INTEGRATION CHECK 2026-09-20".

## Deep-dive findings (Railway CLI + Resend API, 2026-09-20)

- `EMAIL_OVERRIDE_TO=steven@mindbyndr.com` on staging — ALL staging
  email redirects there. **The probe went to steven@mindbyndr.com,
  not help@mynaani.com.** Correct staging isolation, not a bug.
- `EMAIL_FROM=onboarding@resend.dev` — Resend sandbox sender (staging
  only; prod must carry a verified domain — verify before promotion).
- `RESEND_API_KEY` is send-only restricted (401 on list-emails) —
  correct least-privilege.
- No `email rejected`/`send failed`/`inquiry delivery failed` lines in
  backend logs; retry + log-preserve contract confirmed in code.
- GAP-BID17-015 stands: Resend is the sole delivery path, no DB
  fallback — mitigated by retry + ERROR-log lead preservation.

## Acceptance (revised)

- Owner checks **steven@mindbyndr.com** for subject "Contact request —
  Integration Check". If present → delivery path proven end-to-end.
- Before production promotion: verify prod `EMAIL_FROM` is a verified
  sender domain and `EMAIL_OVERRIDE_TO` is empty.
