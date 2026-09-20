# PS-BID17-016 — PRODUCTION inquiry email path is dead (no RESEND_API_KEY)

**Status:** NEEDS OWNER ACTION — prod env config | **Severity:** P0 live defect
**Source:** production cross-check 2026-09-20

## Problem statement

The production `noni-api` service has **no `RESEND_API_KEY`, no
`EMAIL_PROVIDER`, no `EMAIL_FROM`** in its Railway environment. The
inquiry path (`/api/v1/site/contact-inquiry`, `/partner-inquiry`) still
returns `{"status":"received","delivered":true}` to visitors — but the
background send calls `email.send()` which hits
`not settings.RESEND_API_KEY` → logs `email skipped` → returns False.
After retry, `_send_inquiry_with_retry` logs the lead at ERROR level.

**Net effect: every real contact/partner inquiry on production tells
the visitor it was received, emails nobody, and survives only as a log
line.** GAP-BID17-013 + GAP-BID17-015 realized in production.

## Verified

- `railway variables --service noni-api` (production): full var list
  contains zero EMAIL/RESEND keys — confirmed against complete dump.
- `email.send()` fail-quiet path confirmed in
  `backend/services/email.py` — silent by design.
- Endpoint live + honeypot contract verified (`delivered:false` on
  bot submission, no send attempted).
- No `email skipped`/`delivery failed` lines in current log window —
  meaning either no real inquiries in the window OR they predate it.
  Leads are preserved in logs by design; check log retention window
  for any real submissions that dropped.

## Remediation (owner decision — prod env change)

1. Set on production `noni-api`:
   - `RESEND_API_KEY` (send-only key, like staging)
   - `EMAIL_PROVIDER=resend`
   - `EMAIL_FROM` = verified sender domain (NOT `onboarding@resend.dev`
     — that's sandbox; needs a verified mynaani.com sender)
   - `EMAIL_OVERRIDE_TO` = **empty** (no override on prod)
   - `CONTACT_EMAIL`/`PARTNER_EMAIL` = real inboxes
2. Optional but recommended (GAP-BID17-015): DB-persist inquiries so a
   Resend outage can't drop leads — currently only log-preserved.
3. Grep Railway logs for `inquiry delivery failed` / `email skipped`
   to recover any leads that dropped during the gap window.

## Acceptance

- A real `/contact` submission on production produces a delivered
  email at the real inbox — verified by actual send + receipt.
- Staging remains override-isolated.
