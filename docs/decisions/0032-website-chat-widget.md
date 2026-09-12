# ADR 0032 — Retell website chat widget on caregiver and facility journeys

**Status:** Accepted (staging review; production requires owner approval)
**Date:** 2026-09-12
**Intake:** `.ai/intake/2026-09-12-website-chat-agent-intake-012.md`
**Research:** `.ai/research/2026-09-12-website-chat-agent.md` (31 verified sources)

## Context

MyNaani wants a chat surface that answers from the same CONFIRMED-only
knowledge base as the Retell phone receptionist. The research protocol
evaluated four options and selected **Option A — Retell chat agent +
official website widget (script tag)** with Medium-High confidence.

Owner decisions (2026-09-12):

- Placement: **caregiver and senior-care-facility journeys only —
  never the B2C learner journey.**
- The staging-only N8N-HELP-001 help-request widget is **retired — full
  clean replace**.
- Chat volume shares the receptionist's ~50 interactions/month budget.

## Decision

1. **Widget:** `ChatWidget` injects Retell's `retell-widget-v2.js` with a
   domain-locked public key (`VITE_RETELL_PUBLIC_KEY`) and the chat agent
   id (`VITE_RETELL_CHAT_AGENT_ID`). No backend proxy — the public key is
   designed for browser use and is domain-restricted to `mynaani.com`
   (+ staging preview). Unset env vars → no-op (dev, tests).
2. **Placement:** mounted on `/gift`, `/for-communities`, `/c/:slug`,
   `/org`, and gift-mode `/purchase/success` (conditional on
   `is_gift=true`). Never mounted on learner routes.
3. **Retell side:** separate chat LLM (`llm_13c7c67388fef34803a41180c0db`,
   gpt-4.1 temp 0) + chat agent (`agent_646dba13a4321b698970c15c68`)
   sharing knowledge base `knowledge_base_34c63c4e95ed70f5`. Escalation
   is textual only (chat has no `transfer_call`): help@mynaani.com and
   the toll-free number.
4. **Contract exemption:** the FAB + chat panel are non-inventory
   components rendered outside React's tree. They carry
   `data-contract-exemption="chat-widget"` and are bound by the geragogy
   constraints that can be configured: muted-blue token color, text-only
   fab label ("Ask a question"), `data-show-ai-popup="false"`,
   `data-auto-open="false"`, no urgency copy in title/bot name.
5. **Privacy parity:** `everything_except_pii` storage, 30-day retention,
   signed URLs — same posture as the voice agent. `PrivacyPage.tsx`
   updated to disclose Retell as a subprocessor and chat transcripts.
6. **N8N-HELP-001 retired:** widget, `api/help.ts`, `routes/help.py`,
   `help_tasks.py`, `support_request.py`, 4 migrations (replaced by a
   `retire_n8n_help` drop migration), and N8N-HELP docs removed.

## Consequences

- **SPA unmount:** the widget renders outside the React tree; `ChatWidget`'s
  cleanup removes the script and best-effort sweeps `retell`-named DOM
  hosts. Verify on staging that the FAB cannot persist onto learner
  routes after navigation.
- **CSP:** the Pages site currently has no CSP. If the backend header
  posture is ported to Pages, `script-src`/`connect-src` must allow
  `dashboard.retellai.com` + `api.retellai.com` (documented in the
  research memo edge-case matrix).
- **Disclosure parity:** the widget's first message states AI +
  transcript-storage (CA SB-1001 / EU AI Act art.50 pattern), mirroring
  the phone begin-message.
- **Upgrade path:** if a chat surface is ever wanted inside
  contract-bound product pages, Option B (custom React UI over
  `create-chat-completion` + thin FastAPI proxy) is the documented path —
  the widget must not be forced into the closed world.

## Testing

- `PurchaseSuccessPage.test.tsx`: widget marker present in gift mode,
  absent otherwise.
- `frontend/e2e/purchase.spec.ts`: same assertion end-to-end.
- Staging manual check: FAB absent on all learner routes; present on the
  four allowed journeys; navigation off a widget route removes the FAB.
