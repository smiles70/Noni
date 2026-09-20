# Pre-intake research — bid-17 → production integration inventory

**Date:** 2026-09-19 · **Status:** INVESTIGATION COMPLETE — external source
gather pending · **Feeds intake:** `.ai/intake/2026-09-19-p1-bid17-production-implementation.md`
**Trigger (owner):** new intake for bid-17 design implementation; major 3rd-party
integrations on both live pages must not be lost. Sync check vs the live
mynaani app performed before any design decision.

## Research question

How to implement the winning bid-17 design system (dark, agency-grade) onto
`/caregiver` and `/for-communities` in the React frontend **without regressing
any existing third-party integration, telemetry contract, persona isolation,
or governance marker** — and what new ADRs the bid-17 aesthetic requires.

## 1. Integration inventory (verified against source, not intent)

### `/caregiver` → `CaregiverPage.tsx`

| # | Integration | Mechanism | Lose-it risk |
|---|-------------|-----------|--------------|
| C-1 | **Retell chat widget — gift agent** | `ChatWidget journey="gift"` injects `retell-widget-v2.js` (dashboard.retellai.com); `VITE_RETELL_PUBLIC_KEY` (domain-locked) + `VITE_RETELL_CHAT_AGENT_ID_GIFT`, agentVersion=0, FAB config, `data-contract-exemption="chat-widget"` | Wrong/absent agent id → gift visitors get facility KB or nothing; **AF-4 persona leak** |
| C-2 | **Retell voice line** | `SupportContact` → `tel:+18774094144` = `RETELL_FROM_NUMBER`/`PARTNER_PHONE`; inbound receptionist + outbound callback agent | Number dropped/misformatted (E.164 required) |
| C-3 | **Scroll-depth telemetry** | `trackScrollDepth("caregiver")` → POST `/api/v1/telemetry/marketing`, `marketing.scroll_depth` @25/50/90 via `telemetryContract` dedup | Page key rename breaks WS-D baseline continuity |
| C-4 | **Backend footer** | `Footer` → GET `/api/site/footer` (backend-served labels) | Static port loses labels |
| C-5 | **Stripe gift checkout** | `/gift` CTAs → `GiftCheckoutPage` → POST `/api/billing/checkout` → Stripe hosted page (ADR-0021, $59 DEC-0021-PRICE; GAP-001/002 on record) | Redirect/token regressions (known gaps) |
| C-6 | **Contact inquiry** | `/contact` → POST `/api/v1/site/contact-inquiry` | Route/copy loss |
| C-7 | **Whitepapers ×2** | `/whitepapers/cognitive-engagement.pdf`, `geragogy-for-caregivers.pdf` (caregiver set — persona-correct) | Persona leak if facility briefs substituted (ep-018 recurrence) |
| C-8 | **Gift-entry attribution** | `data-gift-entry` attrs on gift CTAs | Analytics attribution loss |
| C-9 | **ADR-0030 marker** | `data-contract-exemption="marketing.caregiver"` | Audit tooling loses exemption trace |
| C-10 | 7 external source citations | inline attribution + linked list | Evidence-standard regression (AF-2) |

### `/for-communities` → `ForCommunitiesPage.tsx`

| # | Integration | Mechanism | Lose-it risk |
|---|-------------|-----------|--------------|
| F-1 | **Retell chat widget — facility agent** | `ChatWidget journey="facility"`; `VITE_RETELL_CHAT_AGENT_ID_FACILITY` (`agent_646dba13…`, llm `llm_13c7c673…`, KB `knowledge_base_34c6…`); ADR-0032 KB partition — no gift pricing | Persona leak / dead FAB |
| F-2 | **Retell voice + callback** | `SupportContact` tel:+18774094144; backend POST `/api/v1/help/callback` → `retell_calls.create_callback` (`RETELL_CALLBACK_AGENT_ID`) + `file_help_contact` → **CompAI CRM tracking intake (Origin header required — commit 0a9248c)** | Call path + CRM filing both break |
| F-3 | **Scroll-depth telemetry** | `trackScrollDepth("for-communities")` → same endpoint | Baseline break (as C-3) |
| F-4 | **Backend footer** | `/api/site/footer` | As C-4 |
| F-5 | **Partner inquiry** | `/partners` → `PartnershipInquiryPage` → POST `/api/v1/site/partner-inquiry` + facility ChatWidget | Form + delivery path loss |
| F-6 | **Retell→CRM webhook** | POST `/api/v1/site/retell/partner-inquiry` (signature-verified) — agent files inquiries **during calls** | Silent partner-lead loss; hardest to notice |
| F-7 | **Partner doorway** | `/c/:slug` → `PartnerPage` → GET `/api/v1/org/by-slug/:slug` + facility widget + SupportContact | Org onboarding path loss |
| F-8 | **Founding-partner pricing** | Real table $375–$1,950/yr + custom tier | Invented/altered figures = AF-8 |
| F-9 | **Whitepapers ×2** | `/whitepapers/the-ai-gap.pdf`, `geragogy-the-key-to-learning.pdf` (facility set) | Persona leak |
| F-10 | **ADR-0030 marker** | `data-contract-exemption="marketing.b2b"` | As C-9 |
| F-11 | 7 external source citations | different list (Pew, NN/g, W3C/WAI, Owsley, H&Z, JMIR, Laganà) | AF-2 |
| F-12 | Header logo | `/mynaani-logo.webp` — caregiver header uses **text "mynaani"**; bid-17 uses linework icon | Logo-variant inconsistency (LOGO-TRADEMARK-001: icon <80px / lockup ≥80px) |

### Bid-17 pages themselves

Pure static mocks — zero scripts/forms/iframes. Live hooks: `tel:+18774094144`,
`/gift`, `/partners`, `/whitepapers/*`, `bid-17-home.html`. **Every integration
above must be ported INTO the redesign — the bids carry none of them.**

### Triple-check pass 2/3 — global & transitive dependencies (new rows)

| # | Integration | Mechanism | Lose-it risk |
|---|-------------|-----------|--------------|
| G-1 | **CompAI CRM tracking script — GLOBAL** | `index.html` inline loader, hostname-keyed: `mynaani.com`/`www` → `cmp_ef8f277f`, `staging.noni-web.pages.dev` → `cmp_4e2759d6`; injects `{crm-host}/t/crm.js?site=<id>` on **every route** | Hostname not in `sites` map → silent no-op, zero tracking; any new preview domain needs a map row |
| G-2 | **CRM event ingest (backend)** | `file_help_contact` → `{CRM_API_URL}/api/t/e`, `visitorId=help-{phone-last4}`, `Origin: https://www.mynaani.com` header **required** (ingest rejects originless — commit 0a9248c) | Origin/URL/SITE_ID drift → silent lead loss |
| G-3 | **Retell webhook signature** | `x-retell-signature` HMAC verify on `/api/v1/site/retell/partner-inquiry` | Secret rotation during deploy → unsigned rejections |
| G-4 | **`public/_redirects`** | `/whitepapers/gifting-ai-learning.pdf` → `cognitive-engagement.pdf` **301** | Asset restructure breaks renamed link |
| G-5 | **Magic auth Bearer interceptor** | `AuthProvider` attaches DID token globally (`MAGIC_TOKEN_KEY`); VITE_MAGIC_PUBLISHABLE_KEY, VITE_AUTH_PROVIDER | Global provider changes affect all POSTs |
| G-6 | **Shared-mount blast radius** | `ChatWidget`/`SupportContact` also mounted on: `GiftCheckoutPage`, `PurchaseSuccessPage` (gift-mode), `PartnerPage`, `PartnershipInquiryPage`, `OrgDashboardPage` — 7 mounts total | A ChatWidget change ships to all mounts, not just these 2 pages |
| G-7 | **Test pins (must update in same change)** | Unit: `data-contract-exemption` markers + exact whitepaper hrefs asserted. e2e: `caregiver.spec.ts` ("Gift mynaani"→/gift, whitepaper links, "our community program", axe) + `community.spec.ts` ("AI learning grounded in geragogy", "Talk to us", pricing, "Let's talk") | Copy/design change without test update = red CI |
| G-8 | **Global accessibility pref** | `applyLargeTextOnBoot` in main.tsx — user large-text preference applies to marketing pages too | Fixed-px redesign that ignores it = a11y regression |
| G-9 | **Env-var matrix** | Frontend: `VITE_RETELL_PUBLIC_KEY`, `VITE_RETELL_CHAT_AGENT_ID_{GIFT,FACILITY}`, `VITE_API_BASE_URL`, `VITE_MAGIC_PUBLISHABLE_KEY`, `VITE_AUTH_PROVIDER`. Backend: `RETELL_API_KEY`, `RETELL_CALLBACK_AGENT_ID`, `RETELL_FROM_NUMBER`, `CRM_API_URL`, `CRM_SITE_ID`, `STRIPE_{SECRET,PUBLISHABLE,PRICE_ID_MODULES_,SUCCESS_URL,CANCEL_URL,WEBHOOK_SECRET}`, webhook secret | Missing staging value → silent no-op (widget/CRM degrade quietly by design) |
| G-10 | **No CSP today** | No `_headers` file — only `_redirects`. If redesign adds CSP, must whitelist `dashboard.retellai.com` + both `*.up.railway.app` CRM hosts | New CSP without both domains = widget + tracker dead |
| G-11 | `data-gift-entry` | **Zero code consumers found** — attribution marker only (possibly scraped by CRM script; unverifiable client-side) | Keep attribute names verbatim |
| G-12 | `marketing.scroll_depth` | Confirmed in `ALLOWED_EVENTS` (E72-B1 contract) | Page-key rename = contract violation, event dropped |

### Pass 4 — independent agent sweep (frontend transitive deps + backend/infra)

**Probable live bugs (fix in this intake, don't "preserve"):**

| # | Finding | Evidence | Sev |
|---|---------|----------|-----|
| B-1 | **`/c/:slug` 404s today** — `PartnerPage` calls `/api/v1/org/by-slug/{slug}` but `organizations_router` mounts under `prefix="/api/v1/billing"` → real route `/api/v1/billing/org/by-slug/{slug}` | `main.py:374`, `organizations.py:338`, `PartnerPage.tsx:42` | **P0** |
| B-2 | **Scroll telemetry dead on staging** — relative `fetch("/api/v1/telemetry/marketing")` works on prod ONLY via Cloudflare `/api/*`→Railway edge proxy (out-of-repo config); staging Pages origin has no proxy → silent `.catch()` | `scrollDepthTelemetry.ts:52`, `SYSTEM.md:84` | P1 |

**Delivery paths (fail-quiet by design — verify envs, not just code):**

| # | Finding | Sev |
|---|---------|-----|
| B-3 | Partner/contact inquiries deliver via **Resend email ONLY** — no DB, no CRM forward on this path. `EMAIL_OVERRIDE_TO` catch-all can silently redirect ALL mail | P0 |
| B-4 | **Celery+Redis worker is a required deploy peer** — Stripe webhook defers to `process_stripe_webhook.delay()`; no worker → checkout "succeeds" but no entitlement/receipt | P0 |
| B-5 | Footer fetch uses **legacy `/api/site/footer` → 302 shim, Sunset 2026-12-01** — normalize to `/api/v1` in redesign, keep shim while edge caches old builds | P1 |
| B-6 | **AuthProvider gates every route**: `/api/v1/auth/config` parity probe → `AuthBlockedNotice` replaces whole tree on mismatch; session probes, `?redirect=` auto-nav, inactivity signOut all run on marketing pages | P1 |
| B-7 | **Honeypot contract**: all 3 lead endpoints expect `website` field (empty=human, truthy=synthetic-success drop). Redesigned forms MUST keep it | P1 |
| B-8 | **CORS allowlist hardcoded** — new preview/custom domains rejected until `CORS_ORIGINS` env updated | P1 |
| B-9 | Prod build ships `VITE_AUTH_PROVIDER='mock'` — Magic dormant; redesign must not assume Magic login | P1 |
| B-10 | Session/cookie auth on `/help/callback`, `/billing/checkout`, `/gifts/claim` — guest gift checkout rules + `Idempotency-Key` dedup header | P1 |

**Frontend architecture couplings:**

| # | Finding | Sev |
|---|---------|-----|
| B-11 | `styles.css` globals the pages silently rely on: `:focus-visible` ring (the ONLY focus indicator — axe pins depend on it), `html.large-text` 125%, skip-link styles → `#main-content` **but marketing `<main>` lacks the id — skip link already lands wrong (existing a11y bug)** | P1 |
| B-12 | StrictMode double-mount dedup assumptions (ChatWidget script-id + `shouldEmit` 30s key); `ResponsiveContainer` double max-width; `ViewportProvider` resize listener | P2 |
| B-13 | Magic SDK injects `auth.magic.link` iframe on these routes in prod builds | P2 |
| B-14 | Boot-time storage migrations (`noni_*`→`mynaani_*`, `?reset=1` wipe) in main.tsx | P2 |
| B-15 | ChatWidget unmount sweep removes ALL `[id*="retell"]` — collateral if another mount/vendor shares prefix | P3 |

**Ops/security surface:**

| # | Finding | Sev |
|---|---------|-----|
| B-16 | `SecurityHeadersMiddleware`: COEP `require-corp` + `frame-ancestors 'none'` + CSP `connect-src 'self'` on API responses — breaks if API ever proxied through Pages domain | P2 |
| B-17 | Retell signature check **disabled when `RETELL_API_KEY` unset** → webhook accepts unauthenticated inquiries → spam into `PARTNER_INBOX`; second CRM surface: `{CRM_API_URL}/api/retell/webhook` per-call | P2 |
| B-18 | Rate limits w/ synthetic-success semantics: Stripe webhook 10/min (429s legit retries), help callback 3/day phone+IP (returns "calling" when throttled), gift preview/claim 10/10min | P2 |
| B-19 | **SEO/meta entirely absent**: shared `<title>Mynaani</title>`, no per-route title/meta/OG/canonical/JSON-LD, no favicon/robots/sitemap/manifest, pure CSR — redesign is the moment to fix, nothing pins it today | P2 |
| B-20 | `public/terms.html` stale duplicate (May 2026, `support@` vs `help@` — contact inconsistency + duplicate content) | P2 |
| B-21 | `logo.webp` used by B2B page + Footer; caregiver uses text wordmark — variant inconsistency persists into redesign (K-6) | P3 |
| B-22 | **No webfont loaded** — renders system-ui despite Inter token; adding hosted fonts = new 3rd-party dep | P3 |
| B-23 | `/.well-known/security.txt` (RFC 9116), `whitepapers/README.txt` publicly served; no `_headers`; SPA fallback is implicit (new extensioned routes won't fall through) | P3 |
| B-24 | BetterStack log shipping on telemetry endpoints (sync 5s POST in-handler); dead config NOT to migrate: `N8N_*`, `EMAIL_PROVIDER`, CSV-export stub; Supabase vestigial | P3 |
| B-25 | `verify-bundle.mjs` asserts prod API URL in chunks; lazy-chunk first paint = `LoadingSkeleton`; `data-site-footer`/`aria-current`/`MIN_TOUCH_TARGET` audit attrs | P3 |

**Manual confirms still open:** prod 404 on `/api/v1/org/by-slug/x` (curl), staging telemetry 404 (curl), Railway env presence (`EMAIL_OVERRIDE_TO`, `RETELL_API_KEY`, `REDIS_URL`, `SERVICE_ROLE=worker`), Cloudflare `/api/*` proxy config (dashboard, not in repo).

## 2. Conflict check (vs AGENTS.md / ADRs / ontology)


| # | Conflict | Severity |
|---|----------|----------|
| K-1 | **Dark theme vs geragogy:** bid-17 is charcoal-dark; geragogy anti-slop table says "Dark mode default — older adults prefer light mode." Caregiver audience is 55+-adjacent. Marketing annex (ADR-0030) permits richer styling but NOT a dark default by default — **needs ADR/owner call** | P0 design decision |
| K-2 | **Palette tokens:** bid-17 uses `#26292E`/`#C9A24D`/gold — off-token. senior-living §4: marketing-exempt BUT "new palette or type values still require an ADR — extend tokens, don't inline hex" (AF-10) | P1 ADR required |
| K-3 | Widget FAB + panel are non-inventory components on a redesigned page — `data-contract-exemption` and SPA cleanup sweep must survive restructure | P1 |
| K-4 | Retell domain-lock: any new preview/staging domain must be registered in Retell dashboard or widget no-ops | P1 ops |
| K-5 | ~50 interactions/month shared Retell budget (ADR-0032) — richer pages may lift volume | P2 |
| K-6 | Logo: bid-17 linework icon vs live text-mark vs `logo.webp` — pick per LOGO rules, one answer both pages | P2 |
| K-7 | Graph: b2b surfaces tracked (3 nodes); caregiver/gift surface has **no graph node** — extraction gap to close when wiring the intake | P3 |

## 6. Deployment strategy — blue/green for a 2-route, frontend-only change

**Current topology (verified):** Cloudflare Pages `noni-web` (prod:
mynaani.com/www; staging: staging.noni-web.pages.dev) → edge proxies
`/api/*` → Railway `noni-api` (envs: staging, production; env-scoped tokens —
DEPLOY-ENV-SYNC-001) → shared Postgres/Redis + Celery (`SERVICE_ROLE=worker`).
**The redesign is frontend-only** — the API contract freezes; zero backend
deploy risk. That shrinks the problem to *safe frontend exposure*.

| Option | Mechanism | Rollback | Risk | Cost |
|--------|-----------|----------|------|------|
| **A — Route-level edge canary (RECOMMENDED)** | Twin Pages deployment of the redesign; Cloudflare edge rule/Worker serves **only `/caregiver` + `/for-communities`** from green; all other traffic → blue. Same `mynaani.com` URL → sessions, Retell domain-lock, CRM campaign, telemetry proxy all unchanged | Delete the edge rule — **seconds**, zero redeploy | Blast radius = 2 routes; lead flows still hit prod API so partner/gift inquiries keep working | Low: 1 Pages deploy + 1 edge rule |
| B — Full twin prod env | New Railway env + second Pages project + `green.mynaani.com`; shared prod DB | DNS flip — minutes | Overkill for 2 static-ish routes; ~15 envs to replicate; Retell/CRM/CORS/hostname maps all need green rows; DB shared anyway → not truly isolated | High ops |
| C — Current pipeline only | staging branch → staging env → merge → prod deploy; Pages keeps prior deployment for rollback | Pages "rollback to previous deployment" — minutes | 100% exposure on cutover; no canary; the thing we're avoiding | Zero new infra |

**Option A mechanics:**
1. Build redesign → deploy to twin Pages project (`noni-web-green` or a
   preview deployment of `noni-web`).
2. Edge: Cloudflare Worker/route rule matching
   `mynaani.com/caregiver*` + `mynaani.com/for-communities*` → fetch from
   green origin, preserving host header. (Config lives in Cloudflare
   dashboard — same place `/api/*` proxy lives; document it in-repo this
   time.)
3. Verify green on the real domain: all 45+ integration rows re-checked
   against live traffic, Retell widget fires (domain lock sees
   `mynaani.com` — no change needed), CRM campaign `cmp_ef8f277f` sees
   prod host (canary metrics blend into prod — acceptable, or flag by
   query param), telemetry flows through the same `/api/*` proxy.
4. Promote = extend the rule to 100% of the two routes → then merge to
   main and re-point those paths at the blue origin. Rollback = remove
   rule at any step.
5. Backend untouched throughout; Celery/Stripe/CRM paths see no
   difference — green and blue POST to the same endpoints (intentional:
   real partner leads must deliver during canary).

**Open config gaps to close first:** the `/api/*`→Railway proxy is
dashboard-only config (not in repo) — codify the green route rule in a
Worker or `_routes.json`/terraform so it's reviewable. Retell domain
lock covers `mynaani.com` — no green-domain registration needed under
Option A (needed only if a separate preview hostname is used for early
QA — then register that host in Retell dashboard + CRM `sites` map +
`CORS_ORIGINS`).

**External validation pending:** Cloudflare Workers route-matching +
Pages multi-deployment mechanics, Railway environment isolation
patterns — part of the §3 source gather before final selection is
locked into the intake.

## 3. External research plan (AGENTS.md §2–§5 — pending execution)

Question set for ≥20 verified sources before options are written:

- Retell web-widget embedding under SPA redesign (official docs + GitHub issues)
- Preserving chat-widget identity through DOM/theme rebuilds (script-injection
  patterns, SPA cleanup best practice — FAANG-grade sources)
- Dark-mode marketing surfaces for 55+/caregiver audiences (NN/g, W3C/WAI,
  academic contrast literature — settles K-1 with evidence, not taste)
- Design-token extension strategy for a dark marketing annex (ADR patterns)
- Persona-isolated AI-agent surface patterns (KB partitioning validation)

Edge-case/remediation matrix (top-30) to be built from those sources and
triple-checked against this codebase before intake options. Seed risks already
identified: rows K-1…K-7 plus widget re-mount on SPA nav, telemetry dedup-key
stability, `data-gift-entry` consumer continuity, webhook secret rotation
during deploy, staging-vs-prod agent id drift.

## 7. Dev + Hermes division of labor (model-diversity strategy)

**Rationale:** passes 1–4 all ran on one model family — correlated blind
spots are the residual risk (the pass-4 agent sweep is the proof: fresh
perspective = 25 new findings + 2 live bugs). Hermes 4 (Nous Research —
70B/405B, hybrid reasoning, strong schema adherence + trained tool-calling,
131K ctx, steerable/neutral) supplies an **independent assessor** that does
not share Dev's priors.

**Access paths (verified):**
- Nous Portal subscription → `hermes` CLI + subscription proxy
  (`hermes proxy start` → `127.0.0.1:8645/v1`, OpenAI-compatible, auto-auth)
- OpenRouter: `nousresearch/hermes-4-70b` / `hermes-4-405b`
  (OpenAI-compatible; needs `OPENROUTER_API_KEY`)
- Hermes Agent API server (`:8642/v1`) — full agent + Tool Gateway
  (web/image/TTS/browser) for autonomous research sweeps
- Nous docs caveat: Hermes-4 chat models are tuned for research/reasoning,
  not rapid tool-call loops — right-sized for judge/synthesizer work, not
  as the executor.

| Task | Dev (Devin) | Hermes |
|------|-------------|--------|
| ≥20-source research gather | Fetch + triple-verify every URL/claim | Hermes Agent Tool-Gateway sweep: candidate sources, syntheses, counter-arguments |
| Edge-case matrix (top-30) | Check each vs codebase + AGENTS.md conflicts | Generate candidate cases + remediations |
| Rubric second pass (required, ep-023) | Verify evidence links in files | Independent scoring of rendered copy vs RUBRIC.md |
| PR-time integration-loss hunt | Produce diff, run gates | Diff + 45-row inventory → "what broke?" adversarial review |
| K-1 dark-theme decision | Verify citations | Summarize 55+/contrast literature both directions |
| Persona-leak / register check | Mechanical scans (done) | Semantic register audit of drafted copy |
| Code/tests/deploy/graph writes | **Dev only** | never |
| Vision (logo/nav verification) | ocular/Gemini lane | n/a — Hermes 4 is text-only |

**Guardrails (same as subagent findings):** Hermes output is advisory —
every factual claim verified against code/webfetch before it enters an
artifact; secrets via env/secrets-manager only (key never in prompts or
files); calls logged to the budget ledger; no write access.

**Immediate use:** the pending external-research gather (§3) + the
second-pass rubric score on the redesign are the two highest-value
placements — the rubric explicitly requires an independent second pass.

## 8. Three-layer model stack — Dev + Hermes + Jev (TypeSafe) — DESCOPED

**Status:** owner on Jev API waitlist — descoped until a `TYPESAFE_API_KEY`
exists. Design retained below as a drop-in; every Jev gate has a fallback
(deterministic code or Hermes) so nothing in this intake blocks on it.

**Jev (TypeSafe AI, launched 2026-09-15)** is not generative: it answers
*typed questions* — `choice` (from options you define), `score` (rubric
scale), `noul` (yes/no probability) — in a single parallel pass,
70–500ms, ~$0.042/M input tokens, calibrated confidence per answer. It
cannot hallucinate a type (returns only defined options) — but it can
pick the wrong option, so it is a **triage layer, not a verdict layer**.
Access: `api.typesafe.ai/v1/systemone` (`TYPESAFE_API_KEY`), Vercel AI
Gateway `typesafe-ai/jev`, or `jev-mcp`/jev-agent-tool MCP server
(stdio — drops into `.devin/mcp_config.json`).

**The cascade (cheapest sufficient judgment wins):**

```
deterministic code (grep/pixel/axe) ──► Jev typed gates ──► Hermes deep review ──► Dev executes+verifies
     ~free, instant                    ~$0.0004, <0.5s        reasoning tokens       files/tests/deploy
```

| Surface | Jev role (typed fan-out, one call) | Escalation |
|---------|-----------------------------------|------------|
| **Integration-loss gate** | 45× `noul`: "does this diff preserve integration row N?" — per PR | p<0.9 → Hermes review → Dev verifies *(fallback now: Hermes reviews full diff vs inventory)* |
| **AF auto-fail screen** | 10× `noul` per candidate (exclamation? invented metric? persona leak? sticky mobile?) | any p>0.5 → human/Hermes *(fallback: mechanical scans + Hermes)* |
| **Persona-leak classifier** | `choice`{gift,facility,learner,neutral} per content block | non-matching block → flag *(fallback: vocab scans, already run)* |
| **Rubric pre-screen** | `score` per criterion before Hermes deep-score | spread → flag *(fallback: Hermes scores all)* |
| **Routing in research** | `choice`{keep,discard,verify} per gathered source | verify-bin → Dev webfetch *(fallback: Dev triages)* |

**Why this composition:** deterministic code already handles what's
checkable (vocab greps, pixel hashes, axe). Jev covers the *semantic
middle* — judgments too fuzzy for regex but too repetitive for frontier
tokens — at near-zero marginal cost with confidence gating. Hermes takes
the hard minority. Dev owns all writes and final verification.

**Guardrails:** Jev answers are typed inputs to *code policy*
(auto|review|escalate) — never auto-merge authority; `TYPESAFE_API_KEY`
via secrets/env only; question packs version-controlled (single file,
reviewed before use — TypeSafe's own guidance); decisions logged to the
audit trail. MCP option: `jev-mcp` stdio server in `.devin/mcp_config.json`
alongside ocular.




1. **K-1 direction:** dark bid-17 theme on the caregiver page — accept dark
   marketing surface for a 55+-adjacent audience, or light-adapt the winning
   design? (This is THE fork in the intake.)
2. Retell dashboard: confirm agent ids/keys for staging domain list.
3. Confirm `data-gift-entry` consumers (analytics pipeline) before markup
   changes.
4. Confirm bid-17 → production scope: both pages + home, or pages only?

## 5. Source table

Internal evidence (verified this session): `CaregiverPage.tsx`,
`ForCommunitiesPage.tsx`, `ChatWidget.tsx`, `SupportContact.tsx`,
`scrollDepthTelemetry.ts`, `siteChrome.ts`, `billing.ts`,
`backend/services/retell_calls.py`, `backend/api/routes/{site,help,organizations}.py`,
`backend/core/config.py`, ADR-0030/0032/0033, AGENTS.md personas,
b2b-agency-graph (personas/surfaces/nodes), nelson graph
(PER-CAREGIVER, US-002, CAP-001/002/003, REQ-006/007, GAP-001/002,
DEC-0021-PRICE), intakes 2026-09-12-013, 2026-09-16-p2-{compai-crm-retell-capture,
retell-facility-agent-partner}.

External source table: **pending** — research plan §3 executes next; intake
options remain blocked until ≥20 verified sources per AGENTS.md.

## 9. Failure-mode register — top 100 (Hermes-generated, Dev-verified vs repo)

Generation: Hermes-4-405B structured pass ×2 ($0.018) → Dev dedupe + repo
verification. Items marked **[CONFIRMED]** are already real in the codebase
today — they are not hypothetical.

### A. Integration loss (1–22)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 1 | Retell widget no-ops — agent id env unset/wrong for persona | M | P1 | FAB absent; silent |
| 2 | Wrong agent id → gift visitors get facility KB (or vice versa) | L | P0 | AF-4 leak; only visible in agent replies |
| 3 | Domain-lock blocks widget on unregistered preview host | H | P1 | Widget dead on new domain |
| 4 | ChatWidget unmount sweep removes another mount's `[id*="retell"]` | L | P2 | Cross-page FAB disappearance |
| 5 | Toll-free `tel:` dropped or misformatted (not E.164) | M | P1 | Call path dead |
| 6 | Callback endpoint loses `website` honeypot → toll fraud open | M | P1 | Spam calls billed to Retell budget |
| 7 | CRM `crm.js` hostname not in `sites` map → zero tracking **[CONFIRMED risk]** | H | P1 | Silent — no error anywhere |
| 8 | Backend ingest rejects events — `Origin` header missing **[CONFIRMED once, 0a9248c]** | M | P1 | Silent lead loss |
| 9 | Retell→CRM webhook signature secret drift → rejections | L | P1 | Partner leads dropped |
| 10 | `RETELL_API_KEY` unset → signature check off, webhook open **[CONFIRMED code]** | M | P2 | Spam injected to PARTNER_INBOX |
| 11 | Resend `RESEND_API_KEY` missing → inquiries log-and-noop | M | P0 | Total silent lead loss |
| 12 | `EMAIL_OVERRIDE_TO` left set in prod → all mail to catch-all | L | P0 | Looks delivered, isn't |
| 13 | Celery worker absent (`SERVICE_ROLE`/`REDIS_URL`) → checkout grants nothing | M | P0 | "Successful" purchase, no entitlement |
| 14 | Stripe `Idempotency-Key` dropped → duplicate-checkout protection lost | L | P2 | Double charges possible |
| 15 | Footer falls back silently — `/api/site/footer` fails or shim removed | M | P2 | Stale labels, no error |
| 16 | Legacy `/api/*` shim sunset (2026-12-01) kills un-normalized calls **[CONFIRMED]** | H | P2 | Post-sunset breakage |
| 17 | `/api/v1/org/by-slug` still wrong → `/c/:slug` stays 404 **[CONFIRMED BROKEN]** | H | P0 | Partner doorway dead today |
| 18 | Whitepaper PDFs renamed/moved without `_redirects` update | M | P2 | Evidence links dead |
| 19 | `hero-mynaani.jpg`/logo asset paths break in restructure | M | P2 | Visual regression |
| 20 | Retell per-call webhook (`{CRM_API_URL}/api/retell/webhook`) unreachable | L | P2 | Call analytics/contacts lost |
| 21 | `data-gift-entry` attrs renamed → gift-attribution markers lost | M | P2 | Silent analytics gap |
| 22 | Rate-limit synthetic-success semantics changed → users see errors | L | P1 | Throttled users told they failed |

### B. Silent-failure & config drift (23–36)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 23 | Relative telemetry fetch works only via prod edge proxy **[CONFIRMED dead on staging]** | H | P1 | Staging metrics absent, silent |
| 24 | Telemetry page keys renamed → `ALLOWED_EVENTS` drops events | M | P1 | Baseline discontinuity, silent |
| 25 | Env var missing in new deploy → designed no-op (widget/CRM/mailer) | H | P1 | Silent feature loss |
| 26 | Staging≠prod parity drift → staging green, prod broken | H | P1 | False confidence |
| 27 | Twin Pages deployment drifts from main build config | M | P1 | Canary tests wrong artifact |
| 28 | CORS allowlist misses new domain → all API calls rejected **[CONFIRMED hardcoded]** | H | P1 | Obvious but only post-deploy |
| 29 | Cloudflare `/api/*` proxy rule edited/lost (dashboard-only config) | L | P0 | Site-wide API outage |
| 30 | Green edge-rule serves wrong persona page or stale build | M | P1 | Canary shows wrong thing |
| 31 | Edge cache serves stale HTML/assets post-cutover | M | P2 | Old page persists |
| 32 | `?reset=1`/`noni_*`→`mynaani_*` migration skipped by bypassed boot | L | P2 | Returning users lose progress |
| 33 | New CSP added without retell/crm/magic/stripe domains | M | P1 | Widgets/tracker/checkout dead |
| 34 | Security-headers middleware breaks proxied/iframed API content | L | P2 | If API ever proxied via Pages |
| 35 | `Sunset`/`Deprecation` headers ignored → calls still on shim | M | P2 | Future cliff |
| 36 | Session cookie domain/samesite mismatch on canary host | L | P1 | Auth failures on green |

### C. Persona isolation & register (37–50)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 37 | Facility register on caregiver page (occupancy/NOI to a daughter buying a gift) **[happened before — ep-018]** | M | P1 | AF-4 auto-fail |
| 38 | Gift pricing/curriculum copy on communities page | M | P1 | AF-4 auto-fail |
| 39 | Wrong whitepaper set per persona (facility briefs on caregiver) **[happened — ep-023 fix]** | M | P1 | Evidence mismatch |
| 40 | CTA routes to wrong journey (`/gift` on B2B, `/partners` on gift) | M | P1 | Broken conversion |
| 41 | Retell agent answers with cross-persona pricing (KB leak) | L | P0 | Discovered only in transcripts |
| 42 | Owner-operator leads with mission language (reads as vendor naiveté) | M | P2 | Register audit |
| 43 | Caregiver page condescends ("easy even for grandma") | L | P1 | Tone violation |
| 44 | Tech-bro register ("revolutionary", "10x", urgency) on B2B | L | P1 | Anti-pattern scan |
| 45 | Analytics/telemetry not segmented by persona | M | P2 | Mixed baselines |
| 46 | Cross-nav links route persona to wrong surface mid-journey | M | P2 | Journey break |
| 47 | Support copy offers wrong contact path per persona | L | P2 | Gift user gets facility pitch |
| 48 | `data-contract-exemption` marker dropped → audit tooling loses trace | M | P2 | Unit test pins catch |
| 49 | Scope creep: learner-surface features leak onto marketing pages | M | P2 | Contract violation |
| 50 | Marketing dark styling leaks onto learner/caregiver-governed surfaces | M | P1 | Geragogy breach |

### D. Design, brand & tokens (51–62)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 51 | Dark default on 55+-adjacent caregiver page without ADR **[K-1 open fork]** | H | P1 | Geragogy conflict |
| 52 | Off-token hexes inlined → AF-10 **[CONFIRMED bid-17 uses #26292E/#C9A24D]** | H | P1 | Rubric auto-fail |
| 53 | Logo lockup rendered <80px (illegible wordmark) **[happened — second-pass audit]** | M | P2 | Trademark rule break |
| 54 | Wrong logo variant per surface (3 variants in play today) **[CONFIRMED inconsistency]** | H | P2 | Brand inconsistency |
| 55 | Stale asset reference (unversioned filename → cached medallion) **[LOGO-ICON-003 lesson]** | M | P2 | Old mark resurfaces |
| 56 | Medallion/filled variant where linework approved | L | P2 | Match-check catches |
| 57 | Trademark geometry altered (rotation/stretch/shadow/recolor) | L | P1 | LOGO-TRADEMARK-001 breach |
| 58 | Focus-visible ring lost in restyle — the ONLY focus indicator **[CONFIRMED dependency]** | H | P1 | axe/keyboard dead |
| 59 | `html.large-text` 125% pref ignored by fixed-px layout | M | P1 | A11y regression |
| 60 | Touch targets <40px on mobile CTAs | M | P2 | MIN_TOUCH_TARGET pin |
| 61 | Sticky/fixed element on mobile intercepts pointer events **[prior incident]** | M | P1 | AF-5 auto-fail |
| 62 | Webfont added as hosted 3rd-party dep without CSP/perf review | L | P3 | New dependency unvetted |

### E. Accessibility & UX (63–72)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 63 | Contrast <4.5:1 on dark theme for 55+ audience | H | P1 | axe violations |
| 64 | Skip link still lands on id-less `<main>` **[CONFIRMED broken today]** | H | P2 | Perpetuate a11y bug |
| 65 | Axe `color-contrast` undetermined over gradients — unchecked visually **[CONFIRMED ×2 pages]** | M | P2 | Incomplete ≠ pass |
| 66 | Motion/animation beyond opacity-fade on older-adult surface | L | P2 | Geragogy violation |
| 67 | `prefers-reduced-motion` not honored by new transitions | L | P2 | Vestibular harm |
| 68 | Keyboard trap/order broken in new nav | M | P1 | WCAG failure |
| 69 | ARIA/heading hierarchy broken (visual order ≠ DOM order) | M | P2 | SR confusion |
| 70 | Cognitive overload: >5 actions, competing CTAs on one screen | M | P2 | Density rule breach |
| 71 | Form labels/placeholders insufficient contrast or missing | M | P1 | Completion failure |
| 72 | Alt text missing on informational images | M | P2 | axe violation |

### F. Copy, evidence & claims (73–84)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 73 | Unsourced claim shipped (no graph node/asset) **[AF-2]** | M | P1 | Evidence audit |
| 74 | Invented metric/testimonial to close a rubric gap **[AF-8]** | L | P0 | Honesty breach |
| 75 | >6-word verbatim lift from agency/vendor source **[AF-3]** | L | P1 | Plagiarism check |
| 76 | Exclamation marks/imperative CTAs **[AF-7]** | L | P2 | Tone scan |
| 77 | Pricing figures drift from real table ($375–$1,950) | M | P1 | Procurement exposure |
| 78 | Dead citation links (external sources rot) **[ep-023 precedent]** | M | P2 | Link sweep |
| 79 | Outdated stats cited (occupancy/AI-adoption figures stale) | M | P2 | Credibility loss |
| 80 | Persona-mismatched sources section (7 vs 7 lists) | M | P2 | AF-4 adjacent |
| 81 | Urgency/scarcity mechanics (timers, "limited spots") | L | P1 | AF-7 + register |
| 82 | Copy promises features the product doesn't have | M | P0 | Trust/legal exposure |
| 83 | `terms.html` stale duplicate persists w/ `support@` vs `help@` **[CONFIRMED]** | H | P2 | Contact inconsistency |
| 84 | No meta description/OG on redesigned pages **[CONFIRMED absent]** | H | P3 | SEO/share dead |

### G. Tests, CI & process (85–100)

| # | Failure | L | I | Detection |
|---|---------|---|---|-----------|
| 85 | e2e copy pins break ("Gift mynaani", "AI learning grounded…", "Talk to us") **[CONFIRMED]** | H | P1 | Red CI |
| 86 | Unit pins break (exemption markers, whitepaper hrefs) **[CONFIRMED]** | H | P1 | Red CI |
| 87 | Axe e2e gate fails post-restyle | M | P1 | CI gate |
| 88 | Tests updated to match bugs (assertions weakened to pass) | L | P0 | Governance breach |
| 89 | `verify-bundle.mjs` fails — prod API URL missing from chunks | L | P2 | Build gate |
| 90 | Visual regression suite flags intentional changes, blocks merge | M | P2 | Baseline update needed |
| 91 | Blanket `git add` sweeps unrelated files **[2 prior incidents]** | M | P1 | Commit hygiene rule |
| 92 | `.github/` touched without `ALLOW_WORKFLOW_CHANGES=1` | L | P2 | Husky blocks commit |
| 93 | RESOLVED declared before owner sign-off **[anti-pattern, twice]** | M | P1 | Process breach |
| 94 | Prod merge without explicit owner approval **[hard rule]** | L | P0 | Deployment gate |
| 95 | Canary rollback path untested — first use is during an incident | M | P1 | Rehearse rollback |
| 96 | Rubric second pass skipped/self-graded **[ep-023 lesson]** | M | P1 | Independent pass required |
| 97 | Graph/intake drift — artifacts record intent not shipped state | M | P2 | Memory corruption |
| 98 | Hermes/Jev output trusted unverified into an artifact | M | P1 | Verification rule breach |
| 99 | Retell 50-int/mo budget exhausted by widget on richer pages | M | P2 | Agents stop answering |
| 100 | Scope creep: fix-list grows to learner surfaces mid-flight | M | P1 | Persona boundary breach |

**Highest-density quadrant (likelihood × impact):** #3, #7, #17, #25, #26,
#28, #37–39, #51–52, #58, #63–64, #85–86 — these belong in the intake's
mandatory verification checklist, not just this register.

## 10. Canary analysis & operational readiness (closes PF-01..PF-06)

Method follows the repo's own codified FAANG sources: Google SRE ch.16
canarying, Kayenta automated canary analysis, Spinnaker baseline-vs-canary
judge — all cited in `2026-09-15-deployed-e2e-strategy.md` (S-07/S-10/S-21).

### 10.1 Canary metric set (per route, blue vs green)

| Metric | Source | Baseline | Canary pass | Fail |
|--------|--------|----------|-------------|------|
| Widget mount rate | DOM probe: `[id*="retell"]` present | blue 7d | ≥99% of pageviews | <95% |
| Widget agent correctness | `data-project-key` + persona agent id | gift/facility mapping | 100% correct | any mismatch → immediate abort |
| Telemetry delivery | `POST /api/v1/telemetry/marketing` 2xx rate | blue 7d | ≥ blue −5% | < blue −15% |
| Inquiry POST success | `/api/v1/site/*-inquiry` 2xx | blue 7d | 100% | any 4xx/5xx spike |
| JS errors | `window.onerror` capture / console probe | blue 7d | ≤ blue | > blue +2/pageview |
| LCP (field or lab) | Lighthouse on route | pre-redesign capture | ≤ blue +200ms | > blue +500ms |

### 10.2 SLI table

| SLI | Measurement | Target |
|-----|-------------|--------|
| Route availability | 200 + expected marker text on GET | 99.9% during canary |
| Widget load success | script inject + FAB renders <3s | ≥99% of loads |
| Inquiry submit success | 2xx on `*-inquiry` POST | ≥99.5% |
| Telemetry delivery | 2xx on scroll-depth POST | ≥95% (best-effort contract) |
| Footer render | `/api/site/footer` 2xx + labels match | ≥99.9% |

### 10.3 Soak window + abort triggers

- **Soak:** 72h minimum, at least one business-hours window, minimum 200
  pageviews per route before promotion (lower bound — extend if traffic thin).
- **Immediate abort (auto):** wrong Retell agent id served; inquiry POST
  4xx/5xx; widget mount <95%; route 5xx.
- **Investigate-then-decide:** telemetry −5%..−15%; LCP +200..500ms; JS
  error rate elevated but non-fatal.
- **Abort = edge-rule flip per `docs/ROLLBACK.md` §BID-17 (<5 min, rehearsed).**

### 10.4 Synthetic monitoring during canary

Deferred-SaaS fallback (per e2e-strategy memo): deployed Playwright smoke
against both routes every 15 min during the 72h window — checks: HTTP 200,
marker copy, `[id*="retell"]` mount, footer labels non-fallback, no console
errors. Plus a manual probe checklist each soak-day: widget click-through,
inquiry dry-run on staging twin, CRM event visible in CompAI.

### 10.5 Performance budget (Phase-2 staging gate)

| Budget | Limit | Rationale |
|--------|-------|-----------|
| LCP (mobile, 4G throttle) | ≤2.5s | Core Web Vitals "good" |
| Total transfer per route | ≤1.5MB | 55+ audience, variable connections |
| JS bundle delta vs blue | ≤+15% | no new framework deps |
| Third-party scripts | +0 (retell + crm only) | no new hosted deps without review |
| Webfonts | system stack or ≤1 font, `display=swap` | no render-blocking fonts |

Measured by Lighthouse CI-equivalent run on staging before canary;
pa11y/Lighthouse baseline capture on blue first (pre-redesign numbers).

### 10.6 Binary-rollout limitation (recorded decision)

The edge-rule canary is **100%-or-nothing per route** — Cloudflare
route rules cannot do percentage splits without Workers+traffic-splitting
code we don't have. Accepted because: (a) blast radius is two low-traffic
marketing routes, not revenue-critical learner flows; (b) rollback is a
config flip <5min, faster than a % dial ramp-down; (c) staging gate +
soak abort triggers substitute for gradual exposure. If canary traffic
ever includes a revenue path, this limitation must be revisited —
Workers-based weighted routing is the upgrade path.

### 10.7 Capacity note (PF-07 — OPEN, owner)

Retell shared budget ≈50 interactions/mo (ADR-0032). Widget on richer
pages may lift volume; canary traffic projection needed from Retell
dashboard before Phase 3. Until pulled: treat agent-exhaustion as a live
abort trigger (monitor agent answer rate).

## 11. R2 verified source table (Hermes candidates → Dev triple-check)

**Method:** Hermes-4-405B produced 38 candidate cards ($0.014). Every URL was
fetched. Result: **24 verified, 14 discarded**. Hermes's PMC/arXiv
hallucination rate on paper IDs was ~100% — every generated PMC number
resolved to an unrelated paper; academic sources were recovered via Crossref
metadata + DOI resolution instead. This validates the untrusted-draft rule.

### Verified sources

| # | URL | Org/Author | Bucket | Relevance |
|---|-----|-----------|--------|-----------|
| S-01 | web.dev/articles/third-party-javascript | Google / Mihajlija | FAANG | 3P script cost, SPOF risk, audit hygiene — Retell+CRM embeds |
| S-02 | web.dev/csp | Google / Medley+West | FAANG | CSP allowlist mechanics — PF-08 |
| S-03 | web.dev/articles/color-and-contrast-accessibility | Google / Gash+Kearney+Andrew | FAANG | 4.5:1 AA / 7:1 AAA rationale, APCA note |
| S-04 | developers.cloudflare.com/pages/configuration/preview-deployments | Cloudflare | FAANG | Preview deploy mechanics — green deploy vehicle |
| S-05 | blog.cloudflare.com/cloudflare-pages-goes-full-stack | Cloudflare | FAANG | Pages+Workers: route-interception path for % rollout upgrade |
| S-06 | stripe.com/docs/payments/checkout/how-checkout-works | Stripe | FAANG | Hosted checkout under deploy — card data never touches app |
| S-07 | primer.style/accessibility/guidelines | GitHub Primer | FAANG | Design-system a11y + primitives (token) governance |
| S-08 | sre.google/workbook/canarying-releases | Google SRE / Warner+Davidovič | FAANG | Canary = partial, time-limited deploy + evaluation — §10 design basis |
| S-09 | doi.org/10.1080/00140139.2013.790485 | Piepenbrock et al., Ergonomics 2013 | Academic | Light mode wins for older adults too (smaller margin) — K-1 evidence |
| S-10 | doi.org/10.1016/j.apergo.2016.11.001 | Dobres+Chahine+Reimer (MIT AgeLab), Applied Ergonomics 2017 | Academic | Night+small text worst on dark — drives type/contrast ACs |
| S-11 | doi.org/10.1093/geront/gny113 | Mitzner et al., Gerontologist 2018 (PRISM trial) | Academic | Older-adult tech adoption trial evidence |
| S-12 | doi.org/10.1186/isrctn27927877 | Laganà, ISRCTN 2013 | Academic | Registered RCT: computer training mental-health impact — cited on bid |
| S-13 | doi.org/10.1201/b13018 | Czaja+Sharit, CRC Press 2016 | Academic | Training-design canon for older adults |
| S-14 | w3.org/WAI/WCAG21/Understanding/contrast-minimum | W3C WAI | Industry | SC 1.4.3 normative text — AC basis; 4.5:1 never rounded |
| S-15 | developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS | MDN | Industry | Preflight/origin mechanics — canary CORS gate |
| S-16 | developer.mozilla.org/.../Understanding_WCAG/Perceivable/Color_contrast | MDN | Industry | AA/AAA table incl. 3:1 UI-component ratio |
| S-17 | owasp.org/www-project-top-ten | OWASP | Industry | Top-10 baseline — injected-script risk framing |
| S-18 | cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html | OWASP | Industry | postMessage origin checks, sandboxed frames, ACAO rules |
| S-19 | content-security-policy.com | CSP reference | Industry | Directive reference for PF-08 allowlist authoring |
| S-20 | nngroup.com/articles/dark-mode | NN/g / Budiu 2020 | Industry | Lit review: light>dark normal vision; dark helps cataract; small text at night worst on dark |
| S-21 | nngroup.com/articles/usability-for-senior-citizens | NN/g / Kane 2019 | Industry | 123-participant program; ability declines 0.8%/yr from 25–60 |
| S-22 | argentum.org | Argentum | Industry | Owner-operator register source; State of Tech Adoption report |
| S-23 | leadingage.org | LeadingAge | Industry | ED/nonprofit register; LZ200 ranking |
| S-24 | nic.org | NIC | Industry | Occupancy/market analytics register for B2B claims |
| S-25 | pewresearch.org/internet/2017/05/17/technology-use-among-seniors | Pew / Anderson+Perrin | Industry | Hard adoption data behind bid stats |

### Discards (logged, not cited)

| Card | Reason |
|------|--------|
| stripe.com/blog/cors | 404 — fabricated |
| docs.railway.* environments | Unreachable ×2 — verify manually later; repo workflows are primary evidence |
| PMC8204637 / 8 PMC batch-d | All resolve to unrelated papers (cervical cancer, hang cleans, neurogenesis) — misattributed |
| arXiv 2001.04335 | Resolves to AI-ethics paper, not persona isolation — misattributed |
| eng.lyft.com progressive-rollouts | 404 — fabricated slug |
| sciencedirect persona survey | Unverifiable/likely fabricated |
| TUM thesis PDF | 404 |
| polaris.shopify.com/foundations/colors | Moved to shopify.dev API docs — stale URL |
| deque.com WCAG contrast post | 404 |
| salesforce design-tokens blog | 404 |
| ARIA switch example | Real but off-topic for this question set |

**Quota check:** FAANG 8 ≥5 ✓ · Academic 5 ≥5 ✓ · Industry 12 ≥5 ✓ ·
Discussion 0 ≤5 ✓ — **25 verified sources, all buckets satisfied.**

## 12. R3 synthesis — decision matrices

### 12.1 Implementation vehicle

| Option | Integration risk | Effort | Fit | Verdict |
|--------|-----------------|--------|-----|---------|
| A. Rewrite `CaregiverPage`/`ForCommunitiesPage` in React, port bid-17 markup to components | Lowest — mounts, markers, hooks all preserved in place | Medium | Keeps ChatWidget/SupportContact/telemetry wiring native | **SELECTED** |
| B. Serve bid-17 as static HTML on the routes | High — widget mount, CRM hostname map, telemetry, footer API all bypassed; SPA nav break | Low | Rejected: breaks G-1/G-6 mounts and React Router | Rejected |
| C. Hybrid: React shell + innerHTML port | Med — dangerouslySetInnerHTML bypasses React event bindings; CSP/maintenance smell | Medium | No benefit over A | Rejected |

### 12.2 Deploy topology (unchanged by gather — sources corroborate)

| Option | Blast radius | Rollback | Cost | Verdict |
|--------|-------------|----------|------|---------|
| A. Edge route-canary, 2 routes to green | 2 routes | <5min config flip (rehearsed) | Low | **SELECTED** — S-08 canonical pattern |
| B. Full twin production backend | Site-wide if shared deps drift | Rebuild-level | High + drift | Rejected — oversized for page change |
| C. Staging → straight to prod | Site-wide | Re-deploy blue | Low | Rejected — no real-traffic evaluation (S-08) |

### 12.3 Dark-theme handling (K-1 resolved by owner + evidence)

Owner approved dark bid-17 theme. Evidence (S-09, S-10, S-20) says positive
polarity wins for older eyes — but bid-17 is already a **hybrid**: dark
hero/CTA bands + light (#f5f3ee paper) content sections. Mitigations adopted
as ACs rather than re-litigating the decision:

- Body copy sections stay on light paper background (already in the mock).
- Dark-band text ≥ large-scale (18pt+/bold) where possible → 3:1 applies;
  body-size text on charcoal must hit 4.5:1 measured, no rounding (S-14).
- Small text on dark at night is the worst cell (S-10) → minimum 16px body,
  prefer 18px, in dark sections.
- Resolve the two axe-incomplete gradient contrast regions manually (GAP-010).

### 12.4 Token strategy

| Option | Governance | Verdict |
|--------|-----------|---------|
| A. ADR extending marketing token set (charcoal/teal/gold/paper as named tokens) | AF-10 compliant, auditable | **SELECTED** |
| B. Inline hex | AF-10 auto-fail | Rejected |
| C. New CSS var block ungoverned | Bypasses ADR trail | Rejected |

**Confidence: High** on 12.1–12.4 — each selected option is the only one
that survives the codebase's own constraints (G-1..G-12) and owner decisions.

## 13. R4 — top-30 edge-case / remediation matrix (triple-checked vs codebase)

Selected from the 100-register by likelihood×impact; each remediation
verified against existing code/handlers/tests.

| # | Edge case (register ref) | Remediation — verified against codebase |
|---|--------------------------|------------------------------------------|
| 1 | Wrong Retell agent id (#2) | Env names asserted in unit test + canary AC-001 DOM check |
| 2 | Widget no-op on green host (#3) | Retell dashboard allowlist step in RUNBOOK (PF-06) — manual, pre-canary |
| 3 | CRM hostname map miss (#7) | Add green host row to `sites` map in same commit (RUNBOOK proc) |
| 4 | Missing Origin header on ingest (#8) | Keep `file_help_contact` path untouched; verify POST in canary probe |
| 5 | Webhook sig off if RETELL_API_KEY unset (#10) | Deploy-checklist env assertion; treat as Phase-1 hardening fix (fail closed) |
| 6 | Resend-only no DB fallback (#15) | Phase-1: log inquiry to DB table before Resend call — new capability, small |
| 7 | Worker absent → grants nothing (#13) | Staging gate: purchase→entitlement e2e on staging before canary |
| 8 | Idempotency-Key dropped (#14) | Keep `billing.ts` fetch verbatim; byte-diff checkout path |
| 9 | Footer silent fallback (#15→#15 reg) | Canary metric: footer label diff vs `/api/site/footer` response |
| 10 | Shim sunset time-bomb (#16) | Normalize all calls to `/api/v1` in Phase-1; grep for `/api/` literals |
| 11 | `/c/:slug` 404 live (#17) | Phase-1 fix: correct PartnerPage path or add route — owner confirms intended slug set |
| 12 | Whitepaper `_redirects` break (#18) | Keep `public/_redirects`; link-check in e2e |
| 13 | Asset path regression (#19) | `hero-mynaani.jpg`, logo SVG pinned in unit test |
| 14 | `data-gift-entry` renamed (#21) | Attribute names pinned in unit test (already pinned — keep) |
| 15 | Staged telemetry dead (#23) | Decide: absolute URL via `VITE_API_BASE_URL` or prod-only — Phase-1 decision in intake |
| 16 | Page-key rename drops events (#24) | Keys pinned: `marketing.scroll_depth` + page strings unchanged |
| 17 | Env no-op design (#25) | Env-matrix checklist per deploy target (AC-012) |
| 18 | Staging≠prod parity (#26) | Parity diff script on env vars before Phase 2 |
| 19 | CORS allowlist blocks green (#28) | RUNBOOK proc + `curl OPTIONS` gate (AC-004) |
| 20 | Edge `/api/*` proxy loss (#29) | Codify edge config in repo (Workers script or terraform) — Phase-1 task |
| 21 | Stale edge cache post-flip (#31) | Purge step in ROLLBACK.md (added) |
| 22 | Facility register on caregiver (#37) | Register lint list (NOI/occupancy/LOS terms) in CI grep |
| 23 | Gift pricing on B2B (#38) | Reverse lint + rubric AF-4 pass |
| 24 | Wrong whitepaper set (#39) | 7-vs-7 href pin in unit test (already pinned — keep) |
| 25 | CTA to wrong journey (#40) | e2e pins on `/gift` and `/partners` links (already pinned — keep) |
| 26 | Off-token hex (#52) | Token ADR + grep gate for `#[0-9a-fA-F]{6}` outside token file |
| 27 | Logo variant/size (#53-54) | `mynaani-icon-linework-dark.svg` both pages; icon <80px rule in audit |
| 28 | Focus ring lost (#58) | axe + manual keyboard walkthrough AC-005 |
| 29 | Dark contrast fails (#63) | §12.3 mitigation set + AC-006 manual gradient pass |
| 30 | Unsourced claims (#73) | senior-living rubric evidence-link requirement; 25-source table is the pool |

## 14. R4 adversarial review (Hermes on completed memo) — dispositions

12 findings returned ($0.006). Triaged against the memo — 8 already covered
(the review digest was truncated), 4 genuinely additive, adopted below:

| Finding | Disposition |
|---------|-------------|
| Backend contracts under redesigned UI | Covered — REQ-001 API freeze; form POST paths pinned (§13 #4/#8) |
| Retell-specific rollback | **ADOPTED:** widget failure during canary = edge-rule flip (same mechanism); agent-id check is AC-001. No separate path needed — recorded |
| Perf monitoring during rollout | Covered — §10.1 LCP metric + §10.4 probes |
| K-1 unresolved | Resolved — owner approved dark theme 2026-09-19 (ep-047); mitigations §12.3 |
| API load-pattern drift | Covered — API contract frozen; identical endpoints/payloads required (AC-002/007) |
| Edge-rule security review | **ADOPTED:** routing rule change reviewed as infra change — config in repo, owner sign-off before enable (added to intake ACs) |
| Manual integration checks | Covered — PF-03 Playwright probes automate the mount/marker checks |
| Mobile/responsive validation | **ADOPTED:** mobile QA pass added — 860px breakpoint, ≥40px targets, no sticky overlays (register #60-61) → AC list |
| Retell volume increase | Covered — PF-07 OPEN (owner dashboard pull); abort trigger armed |
| CRM attribution under canary | Covered — AC-002 + §10.1 inquiry metric |
| Session consistency blue/green | **ADOPTED:** same domain → same cookies by construction; probe added to §10.4 daily checklist (log in on blue, refresh through canary route, verify session) |
| Contrast audit on dark theme | Covered — AC-006 + GAP-010 + §12.3 |

**Verdict:** no unsupported claim survived review; 4 adopted into ACs/monitoring.
Memo is intake-ready.


## Appendix — full integration workflow chains (verified 2026-09-20, prod + staging)

1. **Tracker chain (lead capture):** page load → index.html inline
   hostname map → `crm.js` loader → `/t/{site}.js` → view/click/
   form_submit events → `sendBeacon`/`fetch` → POST `{CRM_API_URL}/api/t/e`
   → CRM Contact/Task → n8n → RocketChat `#crm-alerts`.
   Form capture is automatic — every `<form>` submit with named fields
   (skips password/hidden/file). Honeypot `website` field IS captured
   (type=text, visually hidden) — bot spam lands in CRM too.
2. **Form notification chain (email):** submit → POST
   `/api/v1/site/{contact,partner}-inquiry` → honeypot → synthetic
   receipt : background `_send_inquiry_with_retry` → Resend API →
   inbox (staging: EMAIL_OVERRIDE_TO; prod: NO KEY — dead, PS-016).
3. **Retell chat chain:** `retell-widget-v2.js` + public_key + agent_id
   → chat → transcript → agent webhook → CRM `/api/retell/webhook`
   → contact+task → RC alert. NOTE: staging chat agents webhook to
   PROD CRM (PS-013).
4. **Retell callback chain:** callback request → `file_help_contact`
   → CRM `/api/t/e` (form_submit, path=/curriculum/help) +
   `RETELL_CALLBACK_AGENT_ID` outbound call → webhook → CRM.
5. **Retell voice chain:** toll-free `+18774094144` → **no inbound
   agent bound in Retell** (PS-014) — termination path unverified.
6. **Stripe chain:** `/gift` → checkout → `POST /billing/stripe-webhook`
   → `process_stripe_webhook.delay()` → worker (staging: live; prod:
   MISSING — PS-017).
7. **Telemetry chain:** scroll milestones → POST
   `/api/v1/telemetry/marketing` (absolute URL) → DB append-only.
8. **Site chrome:** `GET /api/v1/site/footer` → backend-served nav/
   legal/socials; frontend fallback mirrors.
9. **Auth:** Magic — `AUTH_PROVIDER=mock` on both envs (dormant).
