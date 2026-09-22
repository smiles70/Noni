# SESSION RESUME — read this first on restart

**Updated:** 2026-09-19 · **Repo:** /home/h/mynaani/Noni

## Standing rules (AGENTS.md — read fully)

- Process v9.x strictly — research → intake → implement → verify → sign-off, no skips.
- FAANG + modular-monolith practices via ontology/graph-memory.
- All dev work audited against AGENTS.md: unit→regression→QA→UAT→smoke→e2e→staging.
- **Skills invoked by problem nature** — logo work → `logo-design-audit`; screenshots → `ocular` MCP; agency/bid work → `ad-agency` + `senior-living-agency`; journeys → `journey-loop-guard`.
- Deployment: staging only; production needs explicit owner go-ahead.
- No `git add -A`; explicit paths; inspect `git diff --cached --stat`.

## On restart — verify these loaded

1. `skill invoke logo-design-audit` — should now register
2. `skill invoke ad-agency` — new this session
3. `skill invoke senior-living-agency` — was unregistered last session
4. `mcp_list_tools` → `ocular` should appear (8 vision tools)
   - Config: `.devin/mcp_config.local.json` (gitignored) — Gemini compat endpoint, `gemini-3.6-flash`, key verified working incl. vision input
   - **Owner action:** rotate that key (was pasted in chat)

## Where we are

**Logo work — VERIFIED-PENDING-SIGNOFF:**
- `mynaani-icon-linework-dark.svg` = the shipped nav/footer icon — cream
  `#EBEBEB` line art (luminance/saturation mask → vtracer → palette-locked),
  floats on charcoal, verified at 1024px + independent Gemini vision audit
  ("line-art strokes, no badge, legible, professional")
- Full variant set: `mynaani-logo-stacked-color-{light,dark}.svg`,
  `-monotone-dark.svg` — in `.ai/research/agency-bids/`
- Approved dark palette (LOGO-HEX-001): `#EBEBEB`/`#98BAD4`/`#D7E3CC` on `#26292E`
- Winning bid pair `bid-17-{caregiver,communities}.html` + `bid-17-home.html` —
  axe-clean (0 violations), persona-isolated, real PDF links, scored 96%/95%
- Synced byte-verified to `~/Downloads/AGENCY_BIDS/`
- **Gate:** owner views pages → confirm linework → close LOGO-ICON-003

## Re-run the ticket on restart — DONE 2026-09-19

`LOGO-ICON-003` verification re-run complete, all gates PASS except owner
sign-off. Results: `.ai/audit/2026-09-19-logo-icon-003-verification.md`,
captures + vision JSON in `.ai/audit/logo-icon-003/`, graph ep-032/ep-033.

Skills invoked in-session and contributing (post owner-challenge audit):
logo-design-audit (Stage-4 match-check: IoU 1.000 vs master, 0.237 vs
medallion), ad-agency, geragogy, site-checker, knowledge-graph-validation.
`senior-living-agency` executed as governing doc — STILL UNREGISTERED this
session (YAML fixed+parses; registry is session-start-bound → verify it
invokes cleanly next restart). Ocular: stdio mode can't accept images —
vision audit ran ocular-equivalent direct calls (same endpoint/model/prompts);
to restore MCP image input run ocular with `MCP_TRANSPORT=http`+`MCP_AUTH_TOKEN`.

Remaining gates: owner hard-refresh of both bid-17 pages → confirm linework →
close ticket. Rotate the OCULAR_API_KEY (was pasted in chat).

## Open items (not forgotten)

- Medallion variant `icon-circle-dark` (busy-photo contexts) — pending
- Adaptive `favicon.svg` (prefers-color-scheme) — pending
- PNG exports 1×/2×/3× + PDF + `USAGE.md` — pending
- Trademark: counsel confirms whether registration claims color (LOGO-TRADEMARK-001)
- Supply items: real testimonials (E-2), shipped tagline (J-2)
- bid-17 → production React implementation — needs owner authorization

## Graph

`.ai/ontology/b2b-agency-graph.json` — ep-001..ep-030, all decisions +
invalidated directions preserved. Full conversation history:
`/home/h/.local/share/devin/cli/summaries/history_ce1d2ab06a184863.md`


## 2026-09-19 — BID-17 research gate PASSED

R2-R4 complete on the integration memo: 25 verified sources (Hermes candidates triple-checked; all generated PMC/arXiv IDs were misattributed and replaced via Crossref), decision matrices selected (React rewrite + edge canary + ADR tokens), top-30 remediation matrix, adversarial review dispositioned (4/12 adopted). K-1 dark + K-6 linework icon owner-approved. Intake `BID-17-PROD-001` is RESEARCH GATE PASSED — options written, awaiting owner approval before implementation. Still open: PF-07 (Retell dashboard), PF-08 (CSP call), K-2 token ADR, K-3/K-4/K-5 implementation constraints. Graph: 156n/201e, hash in .ai/nelson/graph-hash.txt.


## 2026-09-19 — BID-17 implementation on staging

Intake approved; post-intake executed. Branch `feat/bid17-marketing-pages` → pushed to `staging` (NOT main). Commits: d073fc0 (phase-1 hardening), 8a4629c (bid-17 redesign + ADR-0034), 43f7133 (pin updates). Verified locally: 236 unit tests, 34 backend site tests, tsc, vite build, bundle verify — all green. Deploy Staging run 35483205873 fully GREEN (all jobs incl. UAT e2e + post-deploy smoke; A10 smoke also green). UAT fixes shipped in 611adcd + fc944f9 + 8094f29. Next: owner visual review on staging + ocular/site-checker pass, then canary decision pending PF-07/PF-08 + owner sign-off. NOT on main.


## 2026-09-20 — defect tickets PS-001–004 + self-audit

Owner-flagged staging defects fixed and pushed (e209f1e, f9258fd): full-bleed exemption, charcoal footer variant, hero contact relocation, /sources page + footer link. Self-audit found skipped gates (skills, research memo) — corrected retroactively; AGENTS.md now has a defect-ticket fast-path section. Deploy Staging for f9258fd in progress.


## 2026-09-20 — integration check + defect batch 2

Staging integration triple-check: all 9 graph integrations verified live (Celery via Railway CLI). Gaps → PS-006–009. Owner defects → PS-010 footer full-bleed band, PS-011 hero gift-link removal (marker moved to nav), PS-012 RCT card removal. Governance: annex boundary checked before audit. Pushed to staging.

## 2026-09-20 — prod promotion + PS-020 receptionist curriculum KB

PROD DEPLOYED: `feat/bid17-marketing-pages` merged to `main` (5dd994d)
with owner approval after full pre-flight. All deploy jobs green; prod
verified — pages 200, forms→CRM unchanged (tracker+ingest live), both
Retell journey agents in bundle, footer API serving, real visitor
telemetry flowing. Prod DB confirmed at alembic head `retire_n8n_help`
via SSH tunnel (preDeployCommand is null — migrations ran another way;
verified state, not assumed). PS-008/013/014 resolved per owner.

PS-020 (receptionist curriculum KB) implemented to staging:
`curriculum_to_kb.py` generator (36 units → retell/kb/curriculum/*.md,
deterministic, --check for drift) + `retell_apply_curriculum.py`
(egress-allowlist guardrails, snapshots, isolation tripwire, --apply
gate). Dry-run verified against live Retell. 11 tests green.
**Retell --apply awaits owner production approval.**

Open: GoDaddy DNS records (owner) → then EMAIL_FROM @mynaani.com +
drop EMAIL_OVERRIDE_TO. PS-019 logo parked. PS-015/017/018 deferred.
- 2026-09-21: PS-E2E-001 closed — local Playwright matrix completed (firefox+webkit installed, userns workaround documented in CONTRIBUTING).
- 2026-09-21: PS-BID17-021/022 verified on staging — /partners + /contact now carry bid-17 MARKETING grammar; form contracts, honeypots, mailto fallbacks, persona/widget isolation intact; Jev gates green at plan (0.87) and post-change (0.95 clean). Held on staging pending owner UAT.
- 2026-09-22: PS-BID17-021/022 promoted to prod (54f4837). Deploy green, API healthy, forms verified live. Full prod matrix 592/615 — 3 failures all on untouched surfaces (/gift axe contrast, / touch-target, firefox flake green on retry). Jev CI/CD gate: not attributable 0.05, release healthy-with-findings. Tickets: PS-BID17-024 (gift contrast), PS-BID17-025 (mobile target), PS-BID17-023 (honeypot semantics), residual /c/:slug+/org intake.
- 2026-09-22: PS-BID17-024..027 + residual promoted to prod (6e59785). Vendor split (index 100→42kB gz), black clean, /gift axe exclusion (vendor embed), touch-target 48px, firefox flake wait, /c/:slug aligned-doorway. **CI on main fully green first time** — all 6 jobs incl e2e 10m25s. Prod verified 36/36. Jev batch gate: safe 0.89, vendor-split correct 0.81, quality 1.99/2.0.
- 2026-09-22: PS-N8N-001 — n8n descope audit complete. Dead config removed (N8N_WEBHOOK_*/FEATURE_HELP_REQUESTS, zero readers). Railway audit: no n8n service, no N8N vars, either env. Alembic n8n_* history kept (chain integrity). System is n8n-free; only cosmetic remnants (stale local clone = owner file, ADR-0032 record).
- 2026-09-22: PS-N8N-001 final — stale clone archived to ~/Downloads/legacy-help-flow-archive-2026-09-22.tar.gz + deleted; alembic n8n_* filenames renamed help_flow_* (revision IDs preserved, head still resolves). n8n fully out of live code/infra; only revision-ID strings remain inside migration bodies (chain integrity).
- 2026-09-22: PS-BID17-028 caregiver-path drift inventory complete (geragogy + journey-loop-guard + Jev). /caregiver redesigned; /gift, /gift-redeem, /purchase/success, /purchase/cancel all pre-bid-17 grammar. Jev: visible seam 0.87, full-path scope, act 1.93. Sub-tickets 029-032. Bonus findings: GiftCheckoutPage double-mounts ChatWidget; PurchaseCancelPage paywall CTA has no entitlement check.
