# Intake — Learner "I'm stuck" help channel (geragogy-compliant)

**Date:** 2026-09-18
**Status:** open — research in progress
**Process:** v9.51 pipeline; research in
`.ai/research/2026-09-18-learner-help-channel.md` (expanded source
quota per owner request)

## Problem statement

A learner (B2C, 55+) who gets stuck in the curriculum currently has
no way to signal "I need help" from inside the journey. We need a
help-request path that complies with the geragogy contract and
reaches a human.

## Agreed design (owner-approved 2026-09-18, mock reviewed)

- **Single option, one card.** Tapping "Help" in the NavBar swaps
  the lesson body for a help card in the same slot — a state
  change, not a reflow. No widget, no overlay.
- **Copy:** "Get help with this lesson" — "Tap the button and
  someone will call you right away." — button **"Call me"**.
- **Flow:** Call me → one-time phone-number Field (saved to the
  learner's contact; one tap on subsequent visits) → "Call me now"
  → Retell **outbound agent (p18) dials within seconds, 24/7**
  → confirmation: "We're calling you now — keep your phone nearby.
  It will ring from 1-877-409-4144."
- **Quiet footnote:** "Prefer writing? help@mynaani.com" — not a
  competing option.
- **RocketChat stays internal-only** — the learner never touches
  it; `#crm-alerts` receives the callback request so a human can
  follow up.

## Required state

1. `LessonRenderer` (shared by free + paid tracks): Help in NavBar
   swaps the lesson body to the help card; "Back to lesson" restores
   the exact position (indicator line persists). RenderGuard proposal
   accounts for the added Button/Field/Card components.
2. `POST /api/help/callback` (backend): `{phone, unitId?, pageIdx?}`
   → stores the request, files the contact in the CRM (existing
   intake path), triggers the Retell outbound call, returns a
   confirmation state.
3. Retell outbound capability (p18): `create-phone-call` from
   +18774094144 with the voice agent → calls the learner.
4. `#crm-alerts` ping (p19 notifier) on each callback request.
5. Learner surfaces only — never on facility/gift journeys.
6. Unit + Playwright coverage per journey-guard rules; the help
   card is a curriculum-adjacent surface.

## Resolved decisions (from research)

- RC Omnichannel/Livechat rejected — floating widget violates the
  closed component inventory; typing-based chat is the weakest
  channel for this persona.
- Proactive stuck-detection rejected — React may not infer state
  (CONTRACT §IV); interruption harms this persona (COGA).
- One option, not three — choice-overload evidence (Medicare Part
  D study; "Older Adults Prefer Less Choice") favors a single path.
- Phone beats callback-form-first — voice is the preferred channel;
  the number is collected once at request time (checkout collects
  email only, verified `payment_provider.py:241`).

## Open items

- Envelope/RenderGuard: does the help card need a backend-approved
  `ui-envelope` state, or is it a client-side state swap within the
  existing curriculum envelope? Decided at plan stage.
- Whether the callback POST also stamps `source=HELP` on the CRM
  contact so `#crm-alerts` reads `[help]` not `[form]`.
- Sequencing vs p18 (outbound agent must exist for "calls in
  seconds" — interim fallback: alert humans to call manually).
