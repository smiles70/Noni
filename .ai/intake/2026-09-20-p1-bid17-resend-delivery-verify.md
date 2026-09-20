# PS-BID17-006 — Resend end-to-end delivery unverified (inbox confirmation)

**Status:** owner-gated | **Severity:** P1 verification gap
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

## Acceptance

- Owner confirms probe email received at `help@mynaani.com` (or Resend
  dashboard shows the send event).
- If absent: check Railway backend logs for
  `inquiry delivery failed after retry` — the lead is preserved in logs
  by design on double failure.
