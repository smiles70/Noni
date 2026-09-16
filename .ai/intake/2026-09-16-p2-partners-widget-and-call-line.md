# Intake — Mount Retell facility agent + live call line on /partners

**Date:** 2026-09-16
**Status:** in_progress
**Problem:** Triple-scan of the codebase confirmed Retell is already
fully configured (ADR-0032): persona-scoped chat agents, a live toll-free
AI receptionist (1 877 409-4144, intake 013), domain-locked public key —
but the new `/partners` page mounted neither. The "Prefer to talk" line
shipped gated behind `PARTNER_PHONE`, which was unset.

## Goal

- Mount `<ChatWidget journey="facility" />` on `/partners` — partnership
  visitors are the facility persona per ADR-0032's persona isolation.
- Set `PARTNER_PHONE` default to the existing toll-free line
  (`+1 (877) 409-4144`) so the call line renders; keep env override.
- Disclosure copy per intake 013: "answered by our AI receptionist, who
  can connect you to a person when needed."

## Retell pathway for conversational intake (owner question)

Retell natively covers the Claude-intake-agent pattern — no Claude
bridge needed:

1. **Agent function/tool call:** add a `submit_partner_inquiry` custom
   tool on the facility agent pointing at
   `POST /api/v1/site/partner-inquiry` — the chat/voice agent collects
   fields conversationally and posts structured JSON directly. Config
   lives in the Retell dashboard, not this repo.
2. **Post-call analysis + webhook:** Retell's analysis schema extracts
   org/contact/intent into structured JSON and posts it to a webhook
   URL — same result, zero agent-side tools.
3. **Claude in concert (if wanted):** Retell supports a Custom LLM
   endpoint — Retell owns telephony/transport/turn-taking; our backend
   bridges to Claude for reasoning. Higher effort; only worth it if we
   need Claude-specific behavior.

## Acceptance

- `/partners` mounts the facility chat agent (both form and thank-you
  states).
- Call line renders with `tel:+18774094144` + AI disclosure.
- Tests + staging green.
