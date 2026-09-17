# Pre-intake — Adapted Comp AI CRM for partner capture + Retell expansion

**Date:** 2026-09-16
**Status:** pre-intake — research protocol running before options
**Persona scope:** B2B — facility / partner journey (AGENTS.md
dual-audience rule; never touches learner/gift surfaces)

## Problem statement

Partner inquiries currently land only as emails in `PARTNER_INBOX`.
Owner wants a **white-labeled CRM** — an adapted fork of
`trycompai/crm` carrying the mynaani logo — deployed on our existing
Railway infrastructure, accessible by **two internal users**, capturing
*every* partner touchpoint:

- `/partners` + `/for-communities` form submissions
- Retell voice-receptionist calls (1 877 409-4144)
- Retell chat-agent conversations (gift/facility widgets)
- Retell `submit_partner_inquiry` tool calls

## Research questions

1. Is `trycompai/crm` a realistic base — stack, license, self-hosting
   surface, multi-user auth, API/webhook intake?
2. Does it fit our modular monolith + Railway, or is it a separate
   deployable? Is it a candidate for its **own workspace/repo**?
3. How do partner form submissions + Retell call/chat data flow in —
   Retell webhooks (post-call analysis) and/or our adapter endpoint
   forwarding?
4. In tandem: can the Retell facility/voice agents become more
   conversational — deeper qualification dialog + KB trained on the 4
   whitepaper PDFs already hosted on mynaani.com?

## Constraints

- Two internal users only — no public signup surface.
- White-label: mynaani logo/branding.
- Railway-hosted, same infra account as the backend.
- PII posture must match ADR-0032 disclosure commitments (chat/voice
  transcripts already disclosed; CRM becomes a PII store — privacy page
  likely needs updating).
- Geragogy/calm contract applies to learner-facing surfaces; an internal
  CRM is out of contract scope but must still be secure.
