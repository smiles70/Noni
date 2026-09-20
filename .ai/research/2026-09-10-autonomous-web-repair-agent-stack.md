# Research memo: replicating the Crawl → Map → Diagnose → Fix agent workflow

**Date:** 2026-09-10  
**Question:** How do we duplicate / cannibalize the technology in the four-phase workflow below so it can run inside the Noni / Mynaani codebase and stack?

| Phase | Original tool/agent | What it does |
|-------|---------------------|--------------|
| 1. Crawl & Test | Playwright + Google Agent | Walk the live SaaS app, capture console logs, network errors, dead links, screenshots. |
| 2. Map | Neo4j / Ontology Skill | Turn the discovered pages, flows and errors into a structured graph that links UI surfaces to frontend routes, backend endpoints and user journeys. |
| 3. Diagnose | Claude 3.5 Sonnet | Read the crawl evidence and the graph to localize the root cause of a crash or regression. |
| 4. Fix | Claude + MCP (Codebase Index) | Pull the right repo files, match the coding style, and emit a patch / code change. |

This memo follows the `AGENTS.md` research protocol: ≥20 external, verified sources, source triple-check, best-in-class selection, top-30 edge-case / remediation matrix, and codebase conflict check.

---

## 1. Source table (verified)

| # | Category | Source | Author / org | Title / description | Date | Relevance |
|---|----------|--------|--------------|---------------------|------|-----------|
| 1 | FAANG / official | [Microsoft Playwright best-practices docs](https://github.com/microsoft/playwright/blob/main/docs/src/best-practices-js.md) | Microsoft | Playwright testing best practices | 2026 (live) | Resilient locators, test isolation, network mocking — the crawl/test foundation. |
| 2 | FAANG / official | [Google, “Agents” whitepaper](https://storage.ghost.io/c/dc/a8/dca8ae32-7ed6-405a-b948-680b55c8f3dc/content/files/2025/01/Whitepaper-Agents---Google.pdf) | Google | Generative AI agent definition, reasoning, tools | 2025 | Defines the agent loop that ties crawl → act → observe. |
| 3 | FAANG / official | [Google AI — Computer use Interactions API](https://ai.google.dev/gemini-api/docs/computer-use) | Google | Gemini Computer Use API | 2026 | How a Google-style agent drives a browser with screenshots + UI actions. |
| 4 | FAANG / official | [Google Cloud — Gemini Computer Use](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/computer-use) | Google Cloud | Enterprise computer-use setup | 2026 | Production deployment pattern for browser-driving agents. |
| 5 | FAANG / official | [Anthropic — Developing a computer use model](https://www.anthropic.com/research/developing-computer-use) | Anthropic | Claude 3.5 Sonnet computer use research | 2024 | The diagnostic / action loop: screenshot → pixel-counting → click → retry. |
| 6 | FAANG / official | [Anthropic — Computer use tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) | Anthropic | Claude API computer use toolset | 2026 | 17 member tools (screenshot, left_click, type, zoom) and harness loop. |
| 7 | FAANG / official | [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2026-07-28/basic) | Anthropic | MCP base protocol | 2026 | JSON-RPC, stateless, capability negotiation for the fix-phase Codebase Index. |
| 8 | FAANG / official | [MCP architecture docs](https://modelcontextprotocol.io/specification/2024-11-05/architecture/index) | Anthropic | MCP client-host-server architecture | 2024 | How an MCP codebase server is wired into the agent. |
| 9 | FAANG / official | [Microsoft TechCommunity — Browser Automation Tool in Foundry](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-the-new-browser-automation-tool-with-toolboxes-in-foundry/4522790) | Microsoft | MCP-native browser automation with Playwright workspaces | 2026 | Microsoft’s canonical “Playwright as an MCP tool” pattern. |
| 10 | FAANG / thought leader blog | [Unprompted Mind — Observability for Production Claude Agents](https://www.unpromptedmind.com/claude-agent-observability-logging/) | Unprompted Mind | Logging, tracing, cost tracking for agent runs | 2025 | Run / span / event model for diagnosing the diagnosing agent. |
| 11 | Industry / security | [OWASP Top 10 for LLM & GenAI](https://genai.owasp.org/llm-top-10/) | OWASP | 2025 LLM risks incl. Excessive Agency, Unbounded Consumption | 2025 | Security / agency guardrails for the whole loop. |
| 12 | Industry / security | [OWASP — Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | OWASP | Excessive Agency risk and mitigations | 2025 | Why fix-phase tools must be scoped and approved. |
| 13 | Academic | [CUADebug: Diagnosing and Repairing Computer-Use Agent Failures](https://arxiv.org/html/2608.02643) | UIUC, Stanford, Yale | Root-cause analysis for computer-use agents | 2026 | ReAct-style debugger with before/after screenshots and structured RCA. |
| 14 | Academic | [The Dawn of GUI Agent: A Preliminary Case Study with Claude 3.5 Computer Use](https://arxiv.org/html/2411.10323) | National University of Singapore | Capabilities / limits of API-based GUI automation | 2024 | Planning, action, critic dimensions; error categories. |
| 15 | Academic | [OSWorld-Human: Benchmarking Efficiency of Computer-Use Agents](https://doi.org/10.48550/arxiv.2506.16042) | UCSD, Gens etc. | Efficiency benchmark for CUAs | 2025 | Real-world latency and failure distributions for agents. |
| 16 | Academic | [Fully Autonomous Programming with Large Language Models](https://arxiv.org/pdf/2304.10423) | GECCO ’23 | Synthesize, Execute, Debug (SED) loop | 2023 | Repair-focused vs replace-focused debugging strategies. |
| 17 | Academic | [Anchored Self-Play for Code Repair](https://arxiv.org/html/2607.03523) | arXiv | Self-play curriculum for bug generation/fixing | 2026 | Risk of distribution drift when agents train on their own bugs. |
| 18 | Academic | [ReCode: Improving LLM-based Code Repair with Fine-Grained RAG](https://doi.org/10.48550/arxiv.2509.02330) | arXiv | Retrieval-augmented code repair | 2025 | How to retrieve similar past fixes before generating a patch. |
| 19 | Academic | [Benchmarking LLMs for Autonomous Run-time Error Repair](https://www.es.mdu.se/pdf_publications/7185.pdf) | Mälardalen University | Runtime error repair benchmark across 10 models | 2025 | Empirical comparison of Claude 3.5 Sonnet, GPT-4o, etc. for repair. |
| 20 | Vendor / graph | [Neo4j — How to build a knowledge graph in 7 steps](https://neo4j.com/blog/knowledge-graph/how-to-build-knowledge-graph/) | Neo4j | Property graph vs triple store, 7-step methodology | 2025 | Why property graphs fit web-app ontologies better than RDF. |
| 21 | Vendor / graph | [Neo4j — Enterprise knowledge layer](https://neo4j.com/blog/agentic-ai/enterprise-knowledge-layer/) | Neo4j | Agentic AI knowledge layer (ontology, grounding, memory) | 2025 | Three-part substrate: ontology, enterprise data, decision traces. |
| 22 | Vendor / graph | [Neo4j — System Design for AI Knowledge Graphs](https://markaicode.com/architecture/neo4j-system-design-architecture-949/) | Markaicode | Production architecture for Neo4j (single-writer, read replicas) | 2026 | Scaling and HA implications of using Neo4j as the Map store. |
| 23 | Open source | [BugScout](https://github.com/mhmdtaha091/bugscout) | mhmdtaha091 | Autonomous web QA agent → Playwright regression suites | 2026 | Reference crawl/test architecture: explorer → flow map → bug detector. |
| 24 | Open source | [Ouroboros](https://github.com/Navneet-Scaler/Ouroboros) | Navneet-Scaler | Self-healing SaaS QA loop: find, fix, verify | 2026 | End-to-end find/triage/fix/re-verify loop with governance policy. |
| 25 | Open source | [mcp-codebase-index](https://github.com/mikerecognex/mcp-codebase-index) | MikeRecognex | Structural codebase indexer + MCP server | 2026 | 18 query tools over functions, classes, imports, call chains. |
| 26 | Open source | [code-intelligence-mcp](https://github.com/sscba/code-intelligence-mcp) | sscba | Tree-sitter + SQLite knowledge graph + 37 MCP tools | 2026 | Richer code intelligence: impact analysis, design-pattern detection. |
| 27 | Open source | [reference-mcp](https://github.com/mark-burg/reference-mcp) | mark-burg | Comprehension-first MCP server for Python | 2026 | Token-budgeted tools for repo overview, symbols, references, call graph. |
| 28 | Open source | [create-context-graph](https://github.com/neo4j-labs/create-context-graph) | Neo4j Labs | Generate full-stack agent apps from a YAML ontology | 2026 | Declarative ontology → FastAPI backend + Next.js frontend + Neo4j. |
| 29 | HN / practitioner | [mcp-agent HN thread](https://news.ycombinator.com/item?id=42867050) | lastmile-ai / HN | MCP-agent framework and patterns | 2025 | Augmented LLM, Router, Orchestrator-Worker, Evaluator-Optimizer. |
| 30 | HN / practitioner | [web-eval-agent HN thread](https://news.ycombinator.com/item?id=43822659) | Operative | MCP server between IDE agent and Playwright browser-use agent | 2025 | How a coding agent consumes browser-run evidence to self-correct. |
| 31 | HN / practitioner | [Playwright-MCP HN thread](https://news.ycombinator.com/item?id=48319131) | HN | Let AI agents run Playwright tests via MCP | 2026 | Community validation of Playwright-as-MCP-tool. |

All URLs above were fetched with `webfetch` or confirmed reachable during this research run. The Google whitepaper and Microsoft Foundry blog returned binary / 403 respectively, but are linked from official domains and corroborated by other sources.

---

## 2. Synthesis: what each phase really needs

### 2.1 Crawl & Test — Playwright + browser-driving agent

The “Google Agent” in the user’s workflow is a *computer-use agent* (CUA): an LLM that consumes screenshots and emits mouse/keyboard actions. Google’s and Anthropic’s implementations expose this as an API toolset with a tight loop:

1. Take screenshot / accessibility snapshot.  
2. LLM reasons and emits `click(x,y)`, `type(...)`, `scroll`, etc.  
3. Client executes the action and returns the new screenshot.  
4. Repeat until goal or max steps.

The best production pattern is to put **Playwright** underneath that loop because Playwright already handles cross-browser execution, auto-waiting, network interception, console/network capture, traces, and screenshots. Microsoft now ships this as an MCP tool (`npx playwright mcp`) and Azure Foundry exposes it as an MCP tool in toolboxes.

Key design points from Microsoft’s Playwright docs:

- Prefer **role + accessible name** locators (`getByRole`, `getByLabel`) over CSS/XPath.  
- Isolate every test in a fresh browser context.  
- Use `page.route()` to mock external dependencies.  
- Capture traces and screenshots for debugging.

### 2.2 Map — Neo4j / ontology / knowledge graph

A web app graph has three natural layers:

1. **UI surface nodes:** pages, components, CTAs, forms, routes.  
2. **Backend nodes:** API routes, services, models, jobs.  
3. **Journey/ontology nodes:** personas, stages, entitlements, anti-personas.

Neo4j’s property-graph model is a good fit because relationships are first-class and typed (e.g., `(:Page)-[:HAS_CTA]->(:Action)`, `(:Route)-[:CALLS]->(:API)`). The `create-context-graph` project demonstrates how a single YAML ontology can generate an entire FastAPI + Next.js + Neo4j application. For an existing codebase, the graph can be bootstrapped from:

- `frontend/src/App.tsx` route table.  
- React Router / file-based routes.  
- OpenAPI spec (`/openapi.json`).  
- Existing `.ai/ontology/user-journey-ontology.json` and `.ai/journeys/default/journey.yml`.

### 2.3 Diagnose — Claude 3.5 Sonnet + structured RCA

The diagnose phase is not just “ask Claude why it failed.” The best-in-class pattern from `CUADebug` is:

- Maintain a **trajectory** of (screenshot_before, action, screenshot_after, reasoning, status).  
- Let a ReAct debugger iteratively inspect suspicious steps.  
- Output a **structured RCA record**: causal step, taxonomy label, grounded evidence, correction strategy, confidence.  
- Use the graph to enrich the prompt: the failing page’s route, the API it calls, the user journey stage, and the entitlement rule.

This matches Anthropic’s Computer Use research: Claude counts pixels, self-corrects, and retries, but the root cause often precedes the visible failure, so trajectory inspection is required.

### 2.4 Fix — Claude + MCP codebase index

MCP servers let the LLM query the codebase without reading every file. The reference implementations (`mcp-codebase-index`, `code-intelligence-mcp`, `reference-mcp`) expose tools such as:

- `repo_overview`, `get_file_outline`, `find_symbol`, `find_references`.  
- `trace_call_graph`, `get_type_hierarchy`, `find_tests`.  
- Dependency graph and impact analysis.

The fix loop therefore becomes:

1. Diagnosis gives the suspect route/component/API.  
2. MCP tools pull the relevant file outlines, tests, and callers.  
3. Claude drafts a patch.  
4. Patch is applied to a git branch (or git worktree).  
5. Tests / E2E / lint run.  
6. If red, the failure trace is fed back; if green, the patch is proposed.

---

## 3. Decision matrix and selected architecture

### 3.1 Options evaluated

| Phase | Option A | Option B | Option C |
|-------|----------|----------|----------|
| Crawl engine | Playwright + own CUA loop | Playwright MCP + Claude Computer Use | Off-the-shelf agent (Browserbase / Stagehand) |
| Graph store | Neo4j property graph | SQLite knowledge graph (`code-intelligence-mcp`) | In-memory JSON / YAML only |
| Diagnosis | Claude 3.5 Sonnet with prompts | `CUADebug`-style ReAct RCA | Heuristic classifier + LLM summary |
| Fix tools | MCP codebase index | Direct filesystem MCP | Claude Code / `codemcp` |

### 3.2 Trade-offs

- **Crawl engine:** Off-the-shelf hosted agents are fastest to start but introduce a vendor dependency and may not integrate with the local staging environment. A Playwright MCP loop keeps everything in-repo and on Railway/Cloudflare Pages preview deployments.
- **Graph store:** Neo4j adds operational overhead but scales for multi-team ontology evolution. SQLite is lighter and already used by `code-intelligence-mcp`; it is sufficient if the graph is mostly read and updated by CI.
- **Diagnosis:** Pure prompt engineering is cheaper but hallucinates root causes. `CUADebug`-style structured RCA costs more tokens but produces auditable, replayable diagnoses.
- **Fix tools:** Direct filesystem MCP is simplest but has no impact analysis. `code-intelligence-mcp` adds graph-aware search and blast-radius checking.

### 3.3 Selected best-in-class architecture for Noni / Mynaani

| Phase | Selected technology | Why |
|-------|---------------------|-----|
| **Crawl & Test** | Playwright (already in repo) + a lightweight CUA loop using Claude Computer Use API or Google Gemini Computer Use API, surfaced through an MCP server | Reuses existing `frontend/e2e/` Playwright setup; works against local `npm run preview` and Railway preview deploys; captures console, network, accessibility tree, screenshots. |
| **Map** | **Hybrid:** keep the canonical ontology in `.ai/ontology/` and `.ai/journeys/` YAML/JSON, and mirror it into a **SQLite knowledge graph** (via `code-intelligence-mcp` pattern) for code-aware queries. Use Neo4j only if the graph grows beyond SQLite’s single-writer limits. | The repo already has hand-curated journey/ontology artifacts; SQLite is operationally simpler than Neo4j on Railway, but the property-graph model and Cypher can be promoted to Neo4j later. |
| **Diagnose** | Claude 3.5 Sonnet (or Sonnet 4.6) with a **structured RCA prompt** that consumes crawl trajectory, page graph context, and prior intakes/ADRs. | Matches `CUADebug` evidence; integrates with existing `.ai/intake/` documents; produces an auditable diagnosis. |
| **Fix** | **MCP codebase index** (`mcp-codebase-index` or `code-intelligence-mcp`) + AST-aware patch application (e.g., `ts-morph` for TS, `libcst` for Python) | Gives the LLM queryable code context without full-file reads; supports incremental re-indexing on git changes; keeps patches in git branches for review. |

The selected stack is **enterprise-grade but incremental**: it reuses the repo’s existing Playwright tests, FastAPI backend, YAML ontologies, and Devin skills, then layers an agentic loop on top.

---

## 4. Top 30 edge cases, problems, and remediations

| # | Edge case / problem | Trigger | Impact | Remediation | Codebase check (Noni) |
|---|---------------------|---------|--------|-------------|----------------------|
| 1 | Playwright crawl gets trapped in `RequireAuth` redirect loops | Unauthenticated agent hits `/paywall` or `/curriculum` | No meaningful surfaces discovered | Seed authenticated browser state; or run against a test account created via API | `frontend/src/components/RequireAuth.tsx` exists; tests already handle auth state |
| 2 | Console log flood from third-party widgets | Analytics, Stripe.js, Magic throw non-fatal warnings | Diagnostic noise, token bloat | Filter console by source / level; keep an allow-list of relevant domains | `frontend/src/lib/telemetry.ts`, Stripe/Magic integrations present |
| 3 | Dead-link checker follows external social / legal links | Footer contains `twitter.com`, `mozilla.org/privacy` | Flaky failures, outbound rate limits | Restrict crawl to same-origin + configured allow-list; skip `rel="nofollow"` external links | `LandingPage` footer has external links |
| 4 | Accessibility tree changes between renders | React hydration, lazy loading, auth state | CUA mis-clicks or stale locators | Wait for `aria-busy` removal / networkidle; prefer role+name locators | Components use `aria` roles; tests use `getByRole` |
| 5 | CUA mis-clicks dynamic overlays / modals | Toast, cookie banner, auth pending banner | Wrong action, stuck state | Implement “dismiss known overlays” pre-step; use accessibility snapshots | `AuthPendingBanner` is a dynamic overlay |
| 6 | LLM diagnosis hallucinates root cause | Sparse or ambiguous logs | Wrong fix, wasted tokens | Enforce structured RCA: causal step, taxonomy, evidence, confidence; require human approval below threshold | `AGENTS.md` already requires human approval for production |
| 7 | Graph mapping drifts as code changes | Route renamed, component moved | Stale links, wrong diagnosis | CI job re-indexes graph on every `main` merge; version ontology with code | `.ai/ontology/user-journey-ontology.json` versioned in git |
| 8 | Neo4j single-writer bottleneck | Many concurrent crawl agents write graph simultaneously | Write latency, lock contention | Batch writes; route reads to replicas; or use SQLite for writes and Neo4j for analytics | Current stack uses PostgreSQL, not Neo4j; SQLite easier |
| 9 | Graph schema explosion | Dynamic URLs with IDs (`/gift/abc123`) create infinite node types | Unbounded graph, slow queries | Normalize dynamic segments (`/gift/:token`); store instance data as properties, not labels | `frontend/src/App.tsx` uses static route definitions |
| 10 | MCP codebase index stale after agent edits | Agent changes files; index still references old symbol names | Wrong fix target, broken references | Incremental re-index on `git diff` after each edit; `mcp-codebase-index` supports this | Git-based re-index feasible |
| 11 | Generated fix breaks existing unit / E2E tests | Patch changes contract but not tests | Regression in CI | Run `npm run test:unit` and `npx playwright test` before accepting patch | `frontend/package.json` scripts exist |
| 12 | Generated fix introduces security issue | LLM adds unsanitized input or exposes endpoint | Vulnerability | Run `bandit`, `npm audit`, `ruff`, `trivy` in the fix-validation step | `.github/workflows/ci.yml` already runs these |
| 13 | Agent edits `AGENTS.md`, workflows, or security policies | Fix loop misidentifies target file | Governance drift | Block-list files by path; require explicit human approval for `.github/`, `AGENTS.md` | `AGENTS.md` already blocks workflow commits without `ALLOW_WORKFLOW_CHANGES=1` |
| 14 | Cost overrun from long CUA / diagnosis loops | Infinite retries, large screenshots, huge crawl scope | Runaway API spend | Set per-run token and step budgets; cache screenshots at WebP; cap max pages | No existing cost cap; must add |
| 15 | Prompt injection through web content | Crawled page contains hidden instructions in comments/DOM | Agent executes unintended actions | Sandagent in isolated browser context; validate LLM outputs before execution | No web-facing untrusted input in app, but user-uploaded content possible |
| 16 | Agent modifies production database or deploys to prod | Fix loop has live DB credentials | Data loss / outage | Agent only operates in staging / preview; CI gate prevents prod writes | `AGENTS.md` staging-only rule exists |
| 17 | Test environment differs from production | Railway DB vs local SQLite, mock payment provider | Green in CI, red in prod | Use containerized staging that mirrors prod; use mock provider only in CI | `VITE_AUTH_PROVIDER='mock'` used in CI; Railway `production` env separate |
| 18 | Network mocking mismatches real API contracts | `page.route` stubs wrong JSON | False positives / negatives | Pair with backend contract tests and OpenAPI validation | `backend/api/routes/` has FastAPI routes |
| 19 | Cross-device progress not captured by crawl | `localStorage`-only progress | Cannot reproduce user-reported bug | Force server-side progress or seed known `localStorage` state per test | `frontend/src/lib/progress.ts` uses `localStorage` |
| 20 | E2E tests flaky due to timing / animations | Hero fixed viewport, transitions | Non-deterministic results | Use web-first assertions, disable animations in test mode, use traces | `frontend/e2e/` already uses Playwright; hero fixed viewport is an `AGENTS.md` rule |
| 21 | Browser automation blocked by Cloudflare / bot detection | Production is behind Cloudflare Pages + Railway | Agent gets challenged | Target Railway preview URL directly or use test domains with bot protection disabled | `noni-api-production.up.railway.app` accessible; `noni-web.pages.dev` accessible |
| 22 | Agent loops on the same page | SPA route with no URL change | Infinite crawl, no progress | Maintain visited-state set keyed by `(URL, accessibility snapshot hash)`; max steps | `frontend/src/App.tsx` is an SPA |
| 23 | Generated code violates project conventions | LLM uses different import style, snake_case vs camelCase | Rejected by lint / review | Feed `AGENTS.md`, `biome.json`, `pyproject.toml` rules into fix prompt; run lint before commit | `frontend/` uses Prettier/ESLint; `backend/` uses Black/Ruff |
| 24 | Codebase index misses dynamic imports | `import()` inside `useEffect` or lazy routes | Incomplete call graph, wrong fix | Combine static tree-sitter analysis with runtime route table extraction | `frontend/src/App.tsx` has explicit route table |
| 25 | LLM generates deprecated APIs | Model training cutoff older than framework version | Build failure or deprecation warnings | Validate generated code against `package.json` versions; run `tsc --noEmit` | `frontend/package.json` pinned versions |
| 26 | Sensitive data logged in traces / screenshots | User PII, tokens, Stripe secrets | Compliance / secret leak | Redact `Authorization`, `Cookie`, card fields; mask screenshots | `AGENTS.md` and CI already run TruffleHog |
| 27 | Multi-tenant test data leaked across runs | Agent creates accounts in shared staging DB | Non-deterministic tests | Provision isolated tenant / DB per run; reset after test | `backend/models/billing.py` has `Account`; tenant isolation not explicit |
| 28 | Race conditions in parallel test contexts | Two agents edit same branch / DB | Merge conflicts, corrupted state | Use isolated git worktrees and DB schemas per run | Git branch-per-run feasible |
| 29 | Knowledge graph infers wrong route mapping | File-based route convention not matched | Diagnosis points to wrong component | Manual verification step for inferred mappings; allow human override | `.ai/journeys/default/journey.yml` is hand-curated |
| 30 | Fix agent overwrites unrelated code | Large diff to “fix” a narrow bug | Scope creep, regressions | Scope guard: only touch files in the blast radius returned by MCP; require diff review | `AGENTS.md` commit hygiene already forbids `git add -A` |

---

## 5. Codebase conflict check

The following Noni / Mynaani constraints affect the implementation of the four-phase agent:

| Constraint | Implication |
|------------|-------------|
| **Hero is fixed, non-scrolling single viewport** (`AGENTS.md`) | Crawl/test screenshots must not alter the hero layout. Any agent-generated DOM-change tests for hero area must preserve `position: fixed` / `100vh` behavior. |
| **Staging-only deployment gate** (`AGENTS.md`) | The autonomous fix agent must only propose branches and push to `staging` for verification. Production deploy requires explicit human permission. |
| **No `git add -A` / explicit staging** (`AGENTS.md`) | Agent patch application must stage files individually and run `git diff --cached --stat` before commit. |
| **Journey-loop-guard skill** (`AGENTS.md`) | Any generated fix touching curriculum, paywall, purchase success/cancel, gift redemption, or resume helpers must pass the journey-loop guard checklist. |
| **Auth provider is `mock` in CI** | CUA crawl in CI must run against the mock auth flow or seeded auth state; it cannot rely on Magic production. |
| **Existing Playwright E2E suite** | Generated specs should reuse project conventions in `frontend/e2e/` and `frontend/playwright.config.ts`. |
| **Existing ontology/journey artifacts** | The Map phase should import from `.ai/ontology/user-journey-ontology.json` and `.ai/journeys/default/journey.yml` rather than invent a new schema. |
| **Supabase/Railway Postgres DB** | If the graph is stored in PostgreSQL instead of Neo4j/SQLite, use recursive CTEs or `pg_graph` extension; existing Alembic migrations should own schema changes. |
| **FastAPI + SQLAlchemy backend** | Any new `/api/agent/...` endpoints follow the existing route/service/model pattern in `backend/api/routes/`. |

---

## 6. Recommended implementation plan

### Phase 0 — Instrumentation (no new infra)

1. Extend `frontend/e2e/` with a **crawl harness** (`frontend/e2e/agent-crawl.spec.ts`) that:
   - Navigates each route in `frontend/src/App.tsx`.
   - Captures console logs, network errors, accessibility tree snapshots, and screenshots.
   - Writes a JSON report under `.ai/research/crawl-reports/`.
2. Add a `scripts/build_app_graph.py` that reads `App.tsx`, `frontend/src/api/*.ts`, `backend/api/routes/*.py`, and the YAML/JSON ontology into a single SQLite graph.
3. Create a `.ai/research/diagnose-prompt.md` structured RCA template.
4. Wire an MCP server (`mcp-codebase-index` or `code-intelligence-mcp`) into the dev environment and add it to `CLAUDE.md` / Devin skills.

### Phase 1 — Closed-loop pilot

1. Pick one known bug class (e.g., post-purchase routing back to free curriculum).
2. Run crawl harness against the staging preview.
3. Run diagnosis prompt over the crawl output + graph.
4. Use MCP codebase tools to find relevant files (`PurchaseSuccessPage.tsx`, `App.tsx`).
5. Generate a patch on a feature branch; run `npm run test:unit`, `npx playwright test`, `ruff`, `black`, `tsc`.
6. Propose PR; require human review.

### Phase 2 — Automation

1. Wrap the closed-loop pilot in a GitHub Actions workflow triggered on `workflow_dispatch` or nightly against `staging`.
2. Add a governance policy: block edits to `AGENTS.md`, `.github/workflows/`, secrets/config, and any file outside the computed blast radius.
3. Promote the SQLite graph to Neo4j if query complexity or concurrent writers demand it.

---

## 7. Confidence and gaps

| Item | Confidence | Rationale |
|------|------------|-----------|
| Playwright + MCP as crawl engine | **High** | Microsoft’s own Playwright-MCP and Foundry Browser Automation Tool show the pattern is canonical; repo already uses Playwright. |
| SQLite knowledge graph for Map | **High** | `code-intelligence-mcp` proves the approach; repo has existing YAML/JSON ontology to import. |
| Claude 3.5 Sonnet for Diagnose | **High** | Anthropic computer use + `CUADebug` establish the trajectory-inspection / structured RCA pattern. |
| MCP codebase index for Fix | **High** | Multiple reference MCP servers exist; the challenge is scoping and test validation, not feasibility. |
| End-to-end autonomy without human review | **Low** | OWASP Excessive Agency, cost, and safety require human-in-the-loop for any production-affecting change. |

**Gaps requiring user / team input:**

1. Should the Map graph live in **SQLite**, **Neo4j**, or **PostgreSQL with recursive CTEs**?  
2. Which LLM provider / model is budgeted for the CUA loop and diagnosis?  
3. What is the acceptable blast radius for autonomous edits? (e.g., only `frontend/src/components/`, never `backend/models/`?)  
4. Should generated fixes be committed automatically to a branch, or only proposed as PR draft comments?

---

## 8. Link to related artifacts

- `.ai/ontology/user-journey-ontology.json` — existing domain ontology to seed the graph.  
- `.ai/journeys/default/journey.yml` — existing journey definitions.  
- `.devin/skills/journey-loop-guard/SKILL.md` — guardrails for any fix touching the user journey.  
- `AGENTS.md` — deployment gates and commit hygiene that the autonomous agent must obey.  
- `frontend/e2e/` — existing Playwright suite to extend.  
- `backend/api/routes/` — backend pattern for any new agent-facing endpoints.
