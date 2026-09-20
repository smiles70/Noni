# Intake — Backend email service for partner inquiry form

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** The `/partners` form currently submits via a `mailto:`-generated
client-side message. The mailto-vs-form research
(`.ai/research/2026-09-16-contact-form-vs-mailto.md`) concluded this is NOT
enterprise grade — FAANG/enterprise partner flows POST structured data to a
server that owns routing, retention, spam control, and delivery.

## Goal

`POST /api/v1/site/partner-inquiry` — a typed, public, rate-conscious
endpoint that accepts the partner form payload and delivers it to the
partnership inbox.

## Design constraints

- FastAPI + Pydantic on Railway; no existing email infrastructure in repo.
- Transactional email via API provider (Resend/SendGrid/Postmark) when
  `EMAIL_API_KEY`/`EMAIL_FROM`/`PARTNER_INBOX` env vars are configured.
- When provider credentials are absent (staging/dev), the endpoint must
  still succeed — log the inquiry and return `202` with
  `delivered: false` so the user never sees a failure for our missing
  wiring. Structured log line for later pickup.
- Honeypot field for basic bot rejection; no CAPTCHA (geragogy).
- Frontend submits via `fetch` POST; shows thank-you on success; falls
  back to the mailto path only if the POST itself fails.
- No secrets committed; provider chosen via env, not code.

## Acceptance

- Backend: pydantic model, route, unit tests (happy path, validation
  errors, honeypot reject, no-credentials fallback).
- Frontend: form posts to endpoint, keeps mailto as error fallback only.
- Smoke/e2e updated; staging UAT green.
