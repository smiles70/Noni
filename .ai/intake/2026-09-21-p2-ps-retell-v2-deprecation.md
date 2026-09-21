# PS-RETELL-001 — Retell deprecation notice: POST /v2/create-web-call

**Date:** 2026-09-21 · **Priority:** P2 · **Status:** audited — no code change required
**Source:** Retell email notice to steven@mindbyndr.com, 2026-09-21 12:22 PM
(`org_L5WWbbRaCE4WYdSJ`, weekly repeats while calls continue).

## Problem statement

Retell deprecates the v2 browser SDK path and `POST /v2/create-web-call`
on 2026-09-30. Their usage scan flagged **one** request to that endpoint
from workspace `org_L5WWbbRaCE4WYdSJ`: Sep 20 16:42 PDT, client `curl`,
"Secret Key". If the surface is still in use, calls fail after removal.

## Root cause (confirmed in code, not assumed)

The flagged request does **not** originate from either codebase:

- `grep -rE "create.web.call|createWebCall|web_call"` over
  `/home/h/mynaani/Noni` and `/home/h/mynaani-crm` — **zero hits**
  (node_modules excluded).
- Frontend: `frontend/src/components/ChatWidget.tsx` loads Retell's
  hosted loader `dashboard.retellai.com/retell-widget-v2.js` — call
  creation happens inside Retell's own script, not our code. The "v2" in
  the URL is their loader's versioning, not the deprecated API path.
- Backend: `backend/services/retell_calls.py` uses
  `POST /v2/create-phone-call` — the **phone** endpoint, which the
  notice does not deprecate.
- The `curl` client + single request + Sep-20 timestamp match the prior
  session's manual smoke test ("smoke e2e create a call") — a one-off
  probe, not a code path.

## Options

- **A — No code change (selected).** Audit shows the deprecated surface
  is unused. The weekly notice will repeat once or twice (7-day window)
  and stop. If a future feature needs web-call creation, use
  `POST /v3/create-web-call` or `RetellClient.createWebCall()` (SDK 3.x).
- **B — Preemptively migrate backend phone-call path.** Not required —
  `/v2/create-phone-call` is not in this deprecation; migrating blind
  risks breaking the "Call me" lane for zero benefit.
- **C — Pin/update retell-client-js-sdk.** Not used — no dependency in
  package.json; the hosted widget is Retell-maintained.

## Edge cases

- Another curl/manual probe hits `/v2/*` → notice repeats; harmless.
- Retell later deprecates `/v2/create-phone-call` → new notice; then
  `retell_calls.py` needs the v3 path (same body per migration guide,
  response returns connection details).
- Retell updates `retell-widget-v2.js` internals → outside our control;
  the widget is their code.

## Acceptance criteria

- [x] Codebase audit: no usage of `/v2/create-web-call` or v2 SDK objects.
- [x] Staging smoke: ChatWidget loads `retell-widget-v2.js` and mounts
      (script is live, persona-scoped loader intact).
- [ ] Monitor: weekly notice should stop after the 7-day window clears.
