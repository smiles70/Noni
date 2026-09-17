# Intake — Learner "I'm stuck" help channel (geragogy-compliant)

**Date:** 2026-09-18
**Status:** open — research in progress
**Process:** v9.51 pipeline; research in
`.ai/research/2026-09-18-learner-help-channel.md` (expanded source
quota per owner request)

## Problem statement

A learner (B2C, 55+) who gets stuck in the curriculum currently has
no way to signal "I need help" from inside the journey. We need a
help-request path that:

- complies with the geragogy contract (`docs/library/CONTRACT.md` —
  closed-world, low-arousal, no chatbot surfaces in the curriculum),
- does not assume we hold a phone number (Stripe checkout may only
  collect email — to be verified),
- and lands somewhere Steven/Kim actually see and can respond —
  the RocketChat internal ops channel (p19) is the candidate
  destination.

## Explicit scope tension to resolve

p19 scoped RocketChat to **internal-only** ("Explicitly out of
scope: Omnichannel/livechat, site visitors, any customer-facing
surface"). A learner help channel makes RocketChat (or whatever we
choose) customer-facing for the first time. This intake must either
amend that boundary deliberately or propose a non-RC path.

## Questions the research must answer

1. What does the geragogy contract actually permit/prohibit for a
   help affordance inside the curriculum? (Internal.)
2. What identity do we hold on a paying learner — email only, or
   phone too? Does Stripe checkout collect phone? (Internal.)
3. What do older-adult UX studies say about help-seeking channels —
   phone vs form vs chat vs email — for this persona? (External.)
4. Candidate mechanisms, ranked against the contract + stack:
   - a) "Request a call back" → Retell outbound call (p18) or
     human callback
   - b) Simple "email us / help request" form → CRM + RocketChat
     alert
   - c) RocketChat Omnichannel/Livechat embedded on learner pages
     (likely contract-violating — verify)
   - d) SMS or other channel
5. How does a help request reach Steven/Kim — RC alert, CRM contact
   + task, email?
6. Stuck detection: should the UI *offer* help proactively (N failed
   attempts / idle / rage-clicks) or only respond when asked?
   Geragogy implications of proactive interruption.

## Open items

- Persona guard: learner surfaces only — this must never leak to
  facility/gift journeys (dual-audience rule).
- Whether "stuck" state exists anywhere (progress data is
  localStorage-only per AGENTS — server-side stuck detection may be
  impossible today).
