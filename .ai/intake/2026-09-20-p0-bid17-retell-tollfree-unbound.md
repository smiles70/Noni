# PS-BID17-014 — Toll-free +18774094144 has no inbound agent bound

**Status:** needs owner decision | **Severity:** P0 potential live defect
**Source:** Retell API deep dive 2026-09-20 (`list-phone-numbers`)

## Problem statement

The toll-free number published on every marketing surface
(`+1 (877) 409-4144`) exists in the Retell account but reports
`inbound_agent_id: None` and `outbound_agent_id: None`. The "MyNaani
Receptionist" agent (`agent_83c7…`) exists separately. If callers are
meant to reach the Retell receptionist, the binding is missing and the
number rings unanswered.

## Caveats before calling this a defect

- The number may route through another telephony layer (Twilio SIP
  trunk, CRM telephony, n8n call flow) — Retell shows no binding but
  an upstream provider may terminate the call.
- Voice answering may be intentionally deferred (CAP-INT-RETELL-VOICE
  is a capability; the binding may be a pending ops task).

## Resolution path

- Check where `+18774094144` terminates (Twilio/CRM/Retell console).
- If it should hit the receptionist: bind
  `inbound_agent_id=agent_83c72268174e906ec2ed82a564` in Retell console
  or via `update-phone-number` API.
- One test call to the number is the definitive check.

## Acceptance

- A call to `+1 (877) 409-4144` reaches the intended agent/service —
  verified by an actual call or confirmed console binding.
