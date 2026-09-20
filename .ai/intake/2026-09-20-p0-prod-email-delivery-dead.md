# PS-BID17-016 — PRODUCTION inquiry EMAIL path dead; leads still captured via CRM tracker

**Status:** REMEDIATED 2026-09-20 — pending owner inbox confirmation | **Severity:** P1 (downgraded 2026-09-20)

**Correction:** initial filing called this total lead loss. Owner correction:
the crm.js tracker auto-captures every form submit (`form_submit` events
with field values → `/api/t/e`). Both ContactPage and
PartnershipInquiryPage inputs carry `name` attributes, so lead capture
works — leads land in CompAI CRM → n8n → `#crm-alerts`. What's dead on
prod is only the **email notification leg**.
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


## Remediation applied (2026-09-20, Railway CLI)

Set on production `noni-api`:
- `RESEND_API_KEY` = owner-provided send-only key
- `EMAIL_PROVIDER=resend`
- `EMAIL_FROM=onboarding@resend.dev` (sandbox — delivers only to
  account owner; mynaani.com NOT verified in Resend, 403 confirmed)
- `EMAIL_OVERRIDE_TO=steven@mindbyndr.com` (delivers all inquiries to
  owner inbox until domain verified)

## Verified

- Key+sender+recipient proven end-to-end via direct API send
  (message id returned, delivery to account owner).
- Real contact-inquiry on prod → `delivered:true`, no `email skipped`
  or failure lines in logs.
- Look for subject "Contact request — EmailPath Verification" +
  "[mynaani] prod email path verification" at steven@mindbyndr.com.

## Domain verification progress (2026-09-20)

Resend domain `mynaani.com` created via full-access key —
id `027efb86-a671-4c96-a4be-9d11ae907730`, status `not_started`.
DNS records required (mynaani.com DNS is at **GoDaddy** —
domaincontrol.com nameservers — not Cloudflare):

| Type | Name | Value |
|---|---|---|
| TXT | resend._domainkey | p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCfbVfZ2XBKDmiob9u2PdgfxtTRvnhYGXrvhZAOssVZy2avq4yeIsfAZKtWVMYM7HyQxyJRSDslH6vgftxxYjWUrg8/rHM+4EO1ouDYbGtHLt6Q7k3/78b7wS8WIcuGgfNMQLDYxpynSfpXoaXAYkCO+JPRqmTkF/LCGsmVXE4k6wIDAQAB |
| MX  | send | feedback-smtp.us-east-1.amazonses.com (priority 10) |
| TXT | send | v=spf1 include:amazonses.com ~all |
| CNAME | rsend | send.forge.rmta.net |

Owner adds at GoDaddy DNS management → Resend auto-verifies → then
set prod `EMAIL_FROM=<x@mynaani.com>` and clear `EMAIL_OVERRIDE_TO`.

## Still open

- Verify `mynaani.com` domain in Resend (DNS) → then set
  `EMAIL_FROM=<verified sender>` and clear `EMAIL_OVERRIDE_TO`.
- GAP-BID17-015 (no DB fallback for inquiries) remains.
