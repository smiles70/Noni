# Research — Adapted Comp AI CRM for partner capture + Retell expansion

**Date:** 2026-09-16
**Intake:** `.ai/intake/2026-09-16-p2-compai-crm-retell-capture.md`
**Persona:** B2B only — facility/partner journey

## Questions

1. Can `trycompai/crm` be forked, white-labeled (mynaani logo), hosted on
   Railway, limited to two internal users, and fed by every partner
   touchpoint (forms, Retell voice calls, Retell chat, tool calls)?
2. Is it a candidate for its own separate workspace?
3. In tandem: expand the Retell flow into deeper conversational
   qualification, with the KB trained on the 4 whitepaper PDFs hosted on
   mynaani.com.

## Source table

| # | URL | Org | Type | Finding |
|---|-----|-----|------|---------|
| 1 | https://github.com/trycompai/crm | Comp AI | OSS repo (canonical) | MIT-licensed agentic-first CRM; "the CRM is where the agent keeps its notes" |
| 2 | `docs/api.md` in repo | Comp AI | OSS docs | tRPC data surface + REST bridge (`/rest`), OpenAPI at runtime; `ALLOWED_SIGN_IN` allow-list gates account creation |
| 3 | `docs/setup.md` in repo | Comp AI | OSS docs | Bun + Docker; single root `.env`; `DATABASE_URL`, `BETTER_AUTH_SECRET`, `ALLOWED_SIGN_IN` |
| 4 | https://railway.com/deploy/comp-ai-crm | Railway (community template) | Ops | Existing template deploys 5 services: Next.js app, NestJS API, eve agent, mailbox-sync job, Postgres — proven Railway path |
| 5 | `docs/agent.md` in repo | Comp AI | OSS docs | 18 tools, 4 skills, durable eve runtime; `deny-all` sandbox egress; works with zero external keys |
| 6 | https://www.trycomp.ai/docs/self-hosting/docker | Comp AI | Vendor docs | Docker self-hosting exists for the Comp platform; per-service env files |
| 7 | https://docs.retellai.com/features/webhook-overview | Retell | Vendor docs | `call_analyzed`/`chat_analyzed` events POST full analysis (transcript, custom extraction) to a webhook; 10s timeout, 3 retries |
| 8 | https://docs.retellai.com/api-references/update-chat-agent | Retell | Vendor API | `post_chat_analysis_data` extracts typed fields post-chat; agent-level `webhook_url` |
| 9 | https://docs.retellai.com/api-references/add-knowledge-base-sources | Retell | Vendor API | `knowledge_base_files` accepts ≤25 files ≤50MB — direct PDF upload path |
| 10 | https://github.com/rafiulislam4246/retell-ai-production-blueprint | Community OSS | War-story | Production webhook patterns: event filtering, `custom_analysis_data` nesting, idempotency keys, CRM sync |
| 11 | Retell register-webhook docs | Retell | Vendor docs | Signature verification (`X-Retell-Signature`, HMAC-SHA256) — same header our adapter already checks |
| 12 | `.ai/research/2026-09-16-modern-contact-channel.md` | Internal | Prior research | 30-source memo: phone converts 5x forms for 55+; Retell tool path for intake |
| 13 | `docs/decisions/0032-website-chat-widget.md` | Internal | ADR | Persona KB isolation; privacy parity (`everything_except_pii`, 30-day retention) |
| 14 | `.ai/intake/2026-09-12-phone-number-placement-intake-013.md` | Internal | Intake | Voice receptionist + disclosure posture |
| 15 | `frontend/public/whitepapers/` | Internal | Code | The 4 PDFs: cognitive-engagement, geragogy-for-caregivers, geragogy-the-key-to-learning, the-ai-gap |

## Findings

### trycompai/crm is a strong fit

- **License:** MIT — fork + rebrand is permitted.
- **Two users:** `ALLOWED_SIGN_IN` env allow-list is exactly this — the
  app is single-tenant by design ("there are no organizations").
- **White-label:** workspace name + logo; header renders
  `<workspace name> CRM`. Small fork diff.
- **Railway:** an existing community Railway template proves the deploy
  (5 services). Vercel-coupled parts to adapt: Vercel Sandbox (Docker
  alternative exists), Vercel Blob (optional), Vercel AI Gateway (swap
  for a provider key — Anthropic), OIDC.
- **Capture surface:** tRPC routers + a `/rest` bridge — our backend can
  create contacts/activities programmatically.

### Separate workspace: yes

Different stack (Bun/TypeScript monorepo vs our Python/FastAPI),
different deploy target, and it's an internal tool not bound by the
geragogy contract. Recommend a fork as `smiles70/mynaani-crm` or a
sibling workspace — **not** a directory inside Noni.

### Capture architecture (recommended)

```
/partners + /for-communities forms ──▶ POST /partner-inquiry ──┐
Retell voice calls ──call_analyzed──▶                          ├─▶ CRM API
Retell chat agents ──chat_analyzed──▶ POST /retell/events ─────┤   (contacts,
submit_partner_inquiry tool call ───▶ (adapter, already built) ┘    activities,
                                                                   notes)
```

- One new backend endpoint `/api/v1/site/retell/events` receives Retell
  webhooks (signature-verified — same `X-Retell-Signature` path already
  built), normalizes call/chat analysis into a lead record, and forwards
  to the CRM.
- The form path forwards to the CRM alongside the email send.
- CRM API credentials stay server-side (env), never in the browser.

### Retell conversational expansion + PDF training

- `add-knowledge-base-sources` accepts `knowledge_base_files` — the 4
  PDFs upload directly to the **facility** KB (partnership audience).
  Persona rule: `geragogy-for-caregivers.pdf` could also go to the gift
  KB; decide per-document, default facility-only.
- Deeper conversation: `post_chat_analysis_data` / post-call analysis
  schema (`name`, `email`, `organization`, `organization_type`,
  `intent`, `preferred_contact`) extracts typed lead fields even when
  the tool isn't invoked — that webhook payload is the CRM write.
- Extend `scripts/retell_apply.py` with a `--pdfs` step pushing the
  whitepaper files.

## Decision matrix

| Option | Fit | Effort | Risk | Confidence |
|---|---|---|---|---|
| **A. Fork trycompai/crm → Railway, own workspace, webhook-fed** | High — agentic CRM + proven Railway template + allow-list auth | Medium-high (Vercel de-coupling, fork maintenance) | Upstream drift; ops burden of a 5-service deploy | **Medium-High** |
| B. Build lead table in our Postgres + admin page | High — zero new stack | Medium | Re-invents CRM UI; least leverage | Medium |
| C. Third-party CRM (HubSpot free tier) | Medium — fastest live | Low | Vendor lock; data leaves our infra; not white-label | Medium |
| D. n8n pipeline (deprecated workspace) | Low — deprecated | — | Owner excluded it | Low |

## Edge cases / remediation (top 10)

| # | Trigger | Impact | Remediation |
|---|---------|--------|-------------|
| 1 | Webhook replays (3 retries) | Dupe leads | Idempotency on `call_id`/`chat_id` |
| 2 | CRM down | Lost lead | Our DB is system of record; forward async w/ retry |
| 3 | PII into CRM | Compliance | Retell already `everything_except_pii`; CRM field map must not store transcript bodies by default |
| 4 | `call_analyzed` AND `call_ended` both fire | Double capture | Filter on `call_analyzed` only |
| 5 | Railway template image is third-party | Supply chain | Build own image from fork, not `hmseeb/` image |
| 6 | Two users → lockout | Ops | ALLOWED_SIGN_IN + Better Auth owner invariant; never demote last owner |
| 7 | Voice caller gives partial info | Thin records | Analysis schema marks missing fields; agent asks follow-up (KB doc says so) |
| 8 | PDF content drift | Stale answers | KB refresh on PDF change; version doc titles |
| 9 | Gift persona sees partner data | Persona leak | Tool/KB attached to facility agent only |
| 10 | CRM email mailbox sync unused | Confusion | Disable mailbox-sync service on deploy |

## Gaps needing owner input

1. `RETELL_API_KEY` (still needed for `retell_apply.py` + signature
   verification).
2. GitHub repo for the fork (`smiles70/mynaani-crm` or a workspace dir).
3. Anthropic/model-provider key for the CRM's agent (Vercel AI Gateway
   is Vercel-bound).
4. Which PDFs go to the gift KB (default: facility only).
5. Two named users for `ALLOWED_SIGN_IN`.

## Confidence

**Medium-High** — the Railway template and MIT license make the base
real; the Vercel de-coupling work is the main unknown and is bounded.
