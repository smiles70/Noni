# Research memo — E2E/browser-compat coverage of deployed environments (staging + production)

**Date:** 2026-09-15
**Intake:** `.ai/intake/2026-09-15-p2-e2e-deployed-coverage.md`
**Research question:** What is the best-in-class way to run
Playwright/browser-compat checks against the deployed staging and
production sites — without breaking the existing local-dev suite — and
how should it integrate with the Deploy workflow?

---

## 1. Facts established from the codebase

- `frontend/playwright.config.ts:13` — `baseURL: "http://127.0.0.1:5173"`
  literal; **no env override**.
- `:17-26` — unconditional `webServer` block boots
  `npm run dev` with `VITE_API_BASE_URL=https://noni-api-production.up.railway.app`.
  Even local E2E runs "local frontend → **production** backend".
- 5 projects: chromium, firefox, webkit, mobile-pixel, mobile-iphone.
- `npm run test:e2e` is the local gate; CI `e2e` job (`.github/workflows/ci.yml`)
  runs the same suite; Deploy workflow has staging UAT/E2E jobs that also
  run the local-dev-server topology — **no job ever points a browser at
  `staging.noni-web.pages.dev` or `www.mynaani.com`**.
- Deployed verification today = manual `curl` status/size/hash checks
  (caught the stale `gifting-ai-learning.pdf` asset — the class of bug
  this intake targets).
- axe-core is already wired into the E2E specs — reusable for deployed
  smoke (read-only accessibility checks are safe against prod).
- Some specs exercise purchase/gift/paywall flows → **journey-loop
  guard applies**; deployed smoke must be read-only/unauthenticated so
  it cannot create real Stripe checkouts or mutate prod state.

## 2. Source table

| # | Source | Author/Org | Date | Type | Verified |
|---|--------|-----------|------|------|----------|
| S-01 | playwright.dev/docs/ci — "On deployment" section: `deployment_status` trigger + `PLAYWRIGHT_TEST_BASE_URL` env pattern | Microsoft/Playwright | current | FAANG/official | webfetch |
| S-02 | playwright.dev/docs/test-use-options — `baseURL` is a `use` option, per-file override supported | Microsoft/Playwright | current | FAANG/official | search |
| S-03 | playwright.dev/docs/test-annotations — `@tag` + `--grep`/`--grep-invert`/`testConfig.grep` | Microsoft/Playwright | current | FAANG/official | search |
| S-04 | github.com/microsoft/playwright issue #10553 — maintainer: inject `BASE_URL` env or use parametrized projects | Playwright maintainers | 2022 | FAANG/official | search |
| S-05 | github.com/opengovsg/isomer PR #2668 — `playwright.smoke.config.ts` requiring `PLAYWRIGHT_TEST_BASE_URL`, reusable `smoke.yml` post-deploy, unauthenticated read-only checks | Open Government Products (SG gov) | 2026-07 | Primary/enterprise impl | webfetch |
| S-06 | sre.google/sre-book/testing-reliability — ch.17: production tests "essential to running a reliable production service"; smoke tests short-circuit expensive testing | Google SRE | 2016+ | FAANG (Google) | webfetch |
| S-07 | sre.google/workbook/canarying-releases — ch.16 canarying: partial time-limited deploy + evaluation before rollout | Google SRE | 2018+ | FAANG (Google) | search |
| S-08 | sre.google/sre-book/reliable-product-launches — gradual rollouts with verification steps | Google SRE | 2016+ | FAANG (Google) | search |
| S-09 | netflixtechblog.com — Automated Canary Analysis at Netflix with Kayenta | Netflix | 2018 | FAANG (Netflix) | search |
| S-10 | cloud.google.com/blog — Kayenta: open automated canary analysis (Google+Netflix) | Google Cloud | 2018 | FAANG (Google) | search |
| S-11 | learn.microsoft.com/archive — Testing in Production (TiP): methodologies incl. ramped deployment, examples FB/Amazon/Google/MSFT | Microsoft (Seth Eliot) | 2012 | FAANG (MSFT) | search |
| S-12 | csrc.nist.gov/pubs/sp/800/218/final — SSDF v1.1, PW.8: test executable code, incorporate regression tests for previously reported vulns | NIST | 2022-02 | Standards | webfetch |
| S-13 | nvlpubs.nist.gov/.../NIST.SP.800-218.pdf — PW.8/PS.2 release verification practices | NIST | 2022-02 | Standards | search |
| S-14 | cybersecurity.cd.foundation — SSDF PW.8 post-deployment tooling guidance | CD Foundation | current | Industry | search |
| S-15 | auditbuffet.com/patterns/ab-000990 — post-deploy smoke: cites NIST SA-11, SSDF PW.8, ISO 25010; 3-min critical-journey smoke | AuditBuffet | current | Industry/ops | search |
| S-16 | becomeqa.com — Playwright env config: `BASE_URL` env + per-env config files + `--grep @smoke` for prod | BecomeQA | current | Discussion/howto | search |
| S-17 | scrolltest.com — typed multi-env `TEST_ENV` profile lookup, fails loud on typo | ScrollTest | current | Discussion/howto | search |
| S-18 | dev.to/playwright — staging/prod via `process.env` in `baseURL` + dotenv | Playwright team (dev.to) | 2023 | Discussion/howto | search |
| S-19 | mfyz.com — post-deployment Playwright tests via `workflow_run` trigger + auto-rollback on failure | mfyz | current | Discussion/howto | search |
| S-20 | getautonoma.com — three CI levels: localhost → static staging → dynamic preview URL; `BASE_URL` from secrets | Autonoma | current | Discussion/howto | search |
| S-21 | spinnaker.io/docs — canary judge: baseline-vs-canary metric comparison, pass/fail/marginal | Spinnaker (Netflix-orig) | current | Industry/docs | search |
| S-22 | browserstack.com/guide/playwright-tags — tag-based suite slicing (@smoke/@regression) | BrowserStack | current | Industry/vendor | search |
| S-23 | microsoft.com/research — Online Experimentation at Microsoft (controlled-experiment infrastructure as production testing) | Microsoft Research | 2017+ | Academic/corp research | search |
| S-24 | stigviewer.com — SSDF PW.8.1/PW.8.2 control text: scope, design, document deployed-code tests | STIG Viewer (DISA mirror) | current | Standards | search |
| S-25 | Shu/Gu/Enck CODASPY'17 — deployed-artifact security debt propagates downstream (context for scanning deployed artifacts, ties to Trivy memo) | NCSU | 2017 | Academic | webfetch (prior memo) |

Balance: FAANG/top-tier ≥5 (S-01..S-04, S-06..S-11, S-23), academic
≥3 primary + corp-research (S-23, S-25; fewer academic papers exist for
this operational topic — flagged as a gap), industry/standards ≥5
(S-12..S-15, S-21, S-22, S-24), discussion ≤5 (S-16..S-20).

## 3. Synthesis

**The official Playwright answer already exists and is narrow:**
`PLAYWRIGHT_TEST_BASE_URL` is the documented env override (S-01),
maintainers recommend env-injection or parametrized projects (S-04),
and tags + `--grep` are the documented subset mechanism (S-03). The
`webServer` block is config-level and can be made conditional on the
same env var.

**The production-grade shape is proven in the wild:** opengovsg/isomer
(S-05) implemented exactly this — a dedicated `playwright.smoke.config.ts`
that *requires* `PLAYWRIGHT_TEST_BASE_URL`, skips local global setup,
runs an **unauthenticated read-only** smoke suite against the deployed
URL from a reusable workflow invoked post-deploy on staging, UAT, and
prod. That is the reference implementation for our stack.

**Enterprise framing (SRE/SSDF):** Google SRE calls production tests
"essential" and positions smoke tests as the cheap short-circuit layer
(S-06); NIST SSDF PW.8 requires testing deployed executables and
folding regression tests for past incidents into the suite (S-12, S-24)
— the stale-PDF incident is precisely a PW.8.2 regression-test
candidate. Canary/Kayenta (S-07, S-09, S-10, S-21) is the heavier
enterprise pattern — real, but disproportionate for a single-instance
Railway + Pages deploy today.

## 4. Decision matrix

| Option | Covers staging+prod | Effort | Risk to prod | Fit to stack | Verdict |
|---|---|---|---|---|---|
| **A. Env override on existing config** (`PLAYWRIGHT_TEST_BASE_URL` → baseURL + skip webServer) | Yes | Tiny | None (read-only specs only) | Official pattern | **Partial — include** |
| **B. Dedicated `playwright.deployed.config.ts` + `@smoke` tag subset + post-deploy CI job** | Yes | Small | Low — read-only, unauthenticated | Matches isomer impl (S-05) | **SELECT (with A)** |
| C. Parametrized projects per env (local/staging/prod as projects) | Yes | Medium | Same suite×env matrix; heavier maintenance | Over-engineered now | Reject — revisit if envs multiply |
| D. Canary analysis (Kayenta-style metric judgment) | Partial (metric, not DOM) | High | — | No traffic-splitting infra (Railway single service) | Reject — future |
| E. Synthetic monitoring SaaS (Datadog/Grafana checks) | Yes | Medium+vendor | Low | Adds vendor + cost; duplicates Playwright skills | Defer — follow-up |
| F. Keep manual curl smoke | No (no browser) | Zero | — | Status quo — insufficient | Reject |

**Selected: A+B hybrid — confidence High.**

1. `playwright.config.ts`: `baseURL: process.env.PLAYWRIGHT_TEST_BASE_URL ?? "http://127.0.0.1:5173"`;
   `webServer` only defined when `PLAYWRIGHT_TEST_BASE_URL` is unset
   (or a new `playwright.deployed.config.ts` extends base config with
   `webServer: undefined` — cleaner; matches S-05).
2. Tag a `@smoke` subset: landing renders, `/caregiver` renders, gift
   CTA links resolve, whitepaper PDFs return `application/pdf`, axe on
   the 2–3 calm pages. Read-only, unauthenticated.
3. `package.json`: `test:e2e:smoke` script =
   `playwright test --config playwright.deployed.config.ts --grep @smoke`.
4. Deploy workflow: post-deploy smoke step reusing the script against
   `$STAGING_URL` / `$PROD_URL` (workflow change → own commit,
   `ALLOW_WORKFLOW_CHANGES=1`).
5. PW.8.2 regression fold-in: add smoke assertions for the retired-PDF
   redirect (the incident class that motivated this intake).

## 5. Edge-case / remediation matrix (top 30)

| # | Edge case | Impact | Remediation | Codebase check |
|---|---|---|---|---|
| 1 | Test writes to prod (form submit, checkout) | Compliance/UX | `@smoke` = read-only, unauthenticated (S-05 pattern); code-review checklist for tag | Purchase specs exist — **journey-loop guard**: exclude all purchase/paywall specs from `@smoke` |
| 2 | Spec assumes local-only routes/mocks (`VITE_AUTH_PROVIDER=mock`) | Functional | Audit each spec; deployed config runs only `@smoke`; auth-dependent specs stay local | Mock auth used in ci.yml site-checker |
| 3 | `webServer` still boots when env var set | Operational | Gate `webServer` on `!process.env.PLAYWRIGHT_TEST_BASE_URL` or separate config w/o block | Confirmed unconditional today |
| 4 | baseURL typo hits wrong env | Security/ops | Validate URL prefix allowlist in config; throw on non-https for deployed runs | scrolltest pattern (S-17) |
| 5 | Prod smoke flakes → blocks deploys | Operational | retries:2 + trace-on-failure for deployed config (S-05); smoke asserts status/headers not pixel-perfect | retries already CI=2 |
| 6 | Cloudflare bot/WAF challenges Playwright UA | Functional | Real-browser UA default; if challenged, allowlist runner IPs or use `X-` header bypass — verify at impl | Pages default: no WAF challenge expected |
| 7 | Mobile projects hit prod twice → duplicate load | Cost | 5 projects × ~10 smoke tests = trivial traffic | Fine |
| 8 | Tests need storageState/auth on prod | Security | Out of scope — no prod auth testing; if needed later, dedicated smoke account + secrets | — |
| 9 | Staging behind auth/robots gate | Functional | staging.noni-web.pages.dev is public today — verify; if gated, add bypass header | Verify at impl |
| 10 | Deploy workflow emits deployment_status events? | Integration | Cloudflare Pages action may not create GH Deployments → use `workflow_run`/job-step trigger instead (S-19) | Check deploy.yml uses wrangler/action |
| 11 | E2E job runtime doubles CI time | Performance | Only `@smoke` (~8-12 tests) runs post-deploy, not full suite | — |
| 12 | Prod API differs from staging API in spec assumptions | Functional | Smoke asserts frontend-rendered content only; API health via existing /health check | webServer env already points prod API |
| 13 | axe on prod flags same violations — noise | Signal | axe already part of suite; deployed run reuses same thresholds (WCAG 2.1 AA) | Existing axe integration |
| 14 | `_redirects` regression test hits CDN cache staleness | False-fail | `expect` status not body; allow 1 retry; cache-bust query param | Retired-PDF check planned |
| 15 | PDF assertions download 100KB+ per project | Performance | HEAD/range request or `request` fixture instead of page.goto | Use APIRequestContext |
| 16 | Playwright version drift local vs CI | Operational | Browsers already cached in CI; deployed config inherits | Cache step exists in ci.yml |
| 17 | Running full suite against staging leaks test data | Data | `@smoke` excludes mutating specs | — |
| 18 | prod baseURL hardcoded in workflow → drift on domain change | Operational | Repo `vars.PROD_URL`/`STAGING_URL`, not literals | vars pattern already used (`VITE_API_BASE_URL`) |
| 19 | Smoke runs before CDN propagates | False-fail | 30-60s settle delay or retry loop on first assertion | Deploy already waits for Pages |
| 20 | Secrets in smoke (none needed) | Security | Read-only suite needs no secrets — keep it that way | — |
| 21 | `--grep @smoke` matches unintended titles | Functional | Tag via details object `{ tag: '@smoke' }` not title text | S-03 |
| 22 | Local dev flow breaks for contributors | DX | No env vars → identical behavior to today | Verified pattern preserves default |
| 23 | WebKit on prod differs (service worker from Pages?) | Functional | Already covered by 5-project matrix; trace-on-failure captures | — |
| 24 | Deploy smoke failure → who is paged? | Observability | Job failure fails the Deploy run → visible; Slack notify optional later | isomer used Slack (S-05) |
| 25 | Rollback decision on smoke failure | Operational | Manual today; document "smoke red = rollback candidate" in runbook | — |
| 26 | Tags added but old specs untagged silently skipped | Coverage | Keep default suite unchanged; `@smoke` is additive | — |
| 27 | `PLAYWRIGHT_TEST_BASE_URL` set locally points dev runs at prod | Safety | Config warns: if baseURL is prod AND webServer absent, only `@smoke`-tagged allowed? (document; optional guard) | Follow isomer: separate config prevents accidental full-suite-on-prod |
| 28 | Workflow change blocked by husky guard | Process | `ALLOW_WORKFLOW_CHANGES=1` own commit | AGENTS.md rule |
| 29 | New env named `TEST_ENV` vs `PLAYWRIGHT_TEST_BASE_URL` inconsistency | DX | Use `PLAYWRIGHT_TEST_BASE_URL` — official convention (S-01) | — |
| 30 | Smoke test for retired PDF encodes a URL that later legitimately returns 410 | Maintenance | Assertion targets redirect-chain target, not status code alone | — |

## 6. Codebase conflict check

- **Journey-loop guard:** `@smoke` must exclude `purchase`, `gift`
  (checkout submits), `paywall`, `redeem` specs — or keep only their
  *render* tests. No guard violation as long as no spec mutates
  entitlements on prod.
- **Landing-page contract:** smoke asserts hero renders — read-only,
  no layout change. Safe.
- **Commit hygiene:** `playwright.config.ts` + spec tags + package.json
  script = one commit; workflow wiring = separate
  `ALLOW_WORKFLOW_CHANGES=1` commit.
- **Local suite unchanged:** default path (no env var) is byte-for-byte
  today's behavior.
- **Deploy gate:** staging-only rollout; prod smoke step activated only
  after user approves the workflow change.

## 7. Gaps / user input needed

1. Approve A+B approach (env override + dedicated deployed config +
   `@smoke` subset)?
2. Confirm deployed smoke is **read-only/unauthenticated** (no prod
   purchase/auth testing ever)?
3. Add smoke step to Deploy workflow post-deploy (staging first, then
   prod after proof)?
4. Include the retired-PDF redirect as the first PW.8.2 regression
   smoke test?

## 8. Related artifacts

- Intake: `.ai/intake/2026-09-15-p2-e2e-deployed-coverage.md`
- Motivating incident: `.ai/intake/2026-09-15-stale-gifting-pdf-assets.md`
- Config: `frontend/playwright.config.ts`
