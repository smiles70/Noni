# PS-BID17-013 — Staging chat agents webhook to PRODUCTION CRM (drift)

**Status:** CLOSED — intentional; owner confirmed prod CRM filing is acceptable | **Severity:** P0 data-boundary defect
**Source:** Retell API deep dive 2026-09-20

## Problem statement

Both chat agents baked into the staging bundle
(`agent_646d…` gift, `agent_719b…` facility) report
`webhook_url = https://mynaani-crm-api.up.railway.app/api/retell/webhook`
— the **production** CRM. Every staging widget conversation files into
the prod pipeline. The staging callback agent (`agent_f475…`) correctly
points at `mynaani-crm-staging-api` — so the staging/prod split exists
in Retell, but the chat agents weren't re-pointed.

## Options

- **A:** Retell console/API — create staging twin chat agents pointing
  at the staging CRM webhook, update the two
  `VITE_RETELL_CHAT_AGENT_ID_*` build vars for the staging pipeline.
- **B:** Accept shared-CRM-by-design — chat inquiries are leads; filing
  staging-originated leads into prod CRM may be intentional. If so,
  document it as a decision, not a gap.
- **C:** Point the existing chat agents at staging CRM and lose prod
  filing — wrong direction unless prod uses different agents.

## Recommendation

A — staging twin agents keep the boundary clean and cost nothing
(agents are free; budget is per-interaction either way).

## Acceptance

- Staging widget agents webhook to `mynaani-crm-staging-api` (or a
  documented owner decision that shared prod filing is intended).
- No staging test data pollutes prod CRM metrics by accident.


Owner decision 2026-09-20: staging chat conversations filing into
the production CRM is acceptable — agents work correctly in prod.
Documented as intended design, not drift. No twin agents needed.
