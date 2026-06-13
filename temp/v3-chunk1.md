# The Process — Full-Stack Agent Harness v3

> A transferable, project-agnostic orchestration layer for AI agent coding sessions.
> Covers static front-end, full-stack API development, database design, auth, CI/CD, and infrastructure.
> Adapt the project-specific sections (paths, stack, colors), then adopt the full pipeline.
>
> **Capability:** Static sites → Full-stack applications with real auth, databases, APIs, and automated deployment.
> **v3 additions:** Triage Decision Matrix, Agent Contract Layer, Production Feedback Loop, Documentation Agent heuristics, Performance Baseline Init, tiered Core vs Extended pipeline, and formal parallel agent coordination protocol.

---

## 1. Process Flowchart (ASCII)

```
┌──────────────────────────────────────────────────────────────┐
│                      USER REQUEST                            │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  0a. SESSION STATE AGENT (open)                              │
│     • Load prior ARCHITECTURE.md, lessons learned           │
│     • Load active task graph and environment status         │
│     • Load .ai/sessions/production_signals.md (if exists)   │
│       → inject real error rates, regressions, slow queries  │
│     • Inject full context into all downstream agents        │
│     • Output: Hydrated session context                      │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  0b. TRIAGE / CLASSIFIER AGENT                               │
│     • Score request using Decision Matrix (Section 3)       │
│     • Assign tier: CORE or EXTENDED                         │
│     • Decide: GATED or AUTONOMOUS (see Section 3)           │
│     • Decompose into parallel sub-tasks if applicable       │
│     • If parallel: generate Agent Contract (Section 5)      │
│     • Route to correct agent(s)                             │
│     • Output: Tier + routing decision + task graph          │
│               + Agent Contract (if parallel agents needed)  │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  1. RESEARCH AGENT                                           │
│     • If UI/UX: consult Baymard, Material Design,           │
│       Airbnb, Zillow, Zumper, TurboTenant, WCAG             │
│     • If data question: search 3+ sources, cite with dates  │
│     • If backend: research API patterns, auth strategies,   │
│       database schemas, caching strategies                  │
│     • If production signals present: incorporate error      │
│       patterns and regressions from prod into research      │
│     • Output: Research summary with sources                  │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  2. DESIGN AGENT                                             │
│     • Present design plan with:                              │
│       - Files to change                                      │
│       - Section-by-section breakdown                         │
│       - Data model changes (if any)                         │
│       - API contract changes (if any)                       │
│       - ASCII preview of layout (when applicable)            │
│     • If parallel agents needed: produce Agent Contract     │
│       defining interface boundaries (see Section 5)         │
│     • WAIT for explicit user approval before coding          │
│       (skip wait if Triage routed as AUTONOMOUS)             │
│     • Output: Approved design plan + Agent Contract          │
└────────────────────┬─────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┬──────────────┐
         │           │           │              │
         ▼           ▼           ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ 3a. CODE     │ │ 3b.      │ │ 3c.      │ │ 3d. AUTH     │
│ AGENT        │ │ BACKEND  │ │ DATABASE │ │ AGENT        │
│ React/TSX    │ │ AGENT    │ │ AGENT    │ │ JWT/OAuth    │
│ Tailwind CSS │ │ API +    │ │ Schema + │ │ RBAC +       │
│ Shared UI    │ │ handlers │ │ migrate  │ │ middleware   │
│              │ │          │ │          │ │              │
│ ↓ output     │ │ ↓ output │ │ ↓ output │ │ ↓ output     │
│ vs Contract  │ │ vs Cont. │ │ vs Cont. │ │ vs Cont.     │
└──────┬───────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
       │              │            │               │
       └──────────────┴────────────┴───────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  3e. CONTRACT VALIDATION AGENT                               │
│     • Compare all agent outputs against Agent Contract       │
│     • Verify: API shapes match, schema diffs align,          │
│       auth interfaces consistent, no undeclared deps         │
│     • Block 4a if any agent violated the contract            │
│     • Output: Contract validation report (pass/fail)        │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  3f. INTEGRATION AGENT (if external services needed)        │
│     • Third-party APIs, webhooks, MCP, payments             │
│     • Output: Typed API clients + webhook handlers          │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  4a. DOCUMENTATION AGENT                                     │
│     • Run heuristic checklist against diffs (Section 9)     │
│     • Deterministically route each change type to           │
│       correct .md file                                      │
│     • Append with timestamp + agent name; never delete       │
│     • Flag stale docs vs code                               │
│     • Output: Updated .md files with timestamps             │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  4b. TEST AGENT                                              │
│     • Unit tests: `npm test`                                 │
│     • Integration tests: `npm run test:integration`        │
│     • E2E tests: `npm run test:e2e` (if configured)        │
│     • Output: Test report (pass/fail count)                  │
└──────────────────┬───────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
    pass │                    │ fail
         ▼                    ▼
┌─────────────────┐  ┌─────────────────────────────────────────┐
│ 5. AUDIT AGENT  │  │ RECOVERY AGENT                          │
│ Build, lint,    │  │ • Classify failure (load error-taxonomy)│
│ typecheck,      │  │ • AUTO-FIX: type errors, lint,          │
│ security        │  │   unused imports (no approval)          │
│                 │  │ • ESCALATE: test failures, security,    │
└────────┬────────┘  │   perf regressions, scope changes       │
         │           │ • ROLLBACK: if fix fails 3×             │
         │           │ • Output: Fix or escalation report      │
         │           └──────────────┬──────────────────────────┘
         │                          │ retry (max 3)
         │                          └──────────► (back to 4b)
         ▼
┌──────────────────────────────────────────────────────────────┐
│  5. AUDIT AGENT                                              │
│     • Build: `npm run build`                                 │
│     • Lint: `npx eslint . --ext .ts,.tsx`                  │
│     • Typecheck: `npx tsc --noEmit`                          │
│     • Security: `npm audit` + auth flow review               │
│     • Zero warnings tolerated                                │
│     • Output: Clean build report                             │
└──────────────┬───────────────────────────────────────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
┌───────────────┐  ┌─────────────────────────────────────────┐
│ 5a.           │  │ 5b. PERFORMANCE AGENT                   │
│ AUDIT AGENT   │  │ • Compare vs baselines in               │
│ (continued)   │  │   docs/06-performance.md                │
│               │  │ • Core Web Vitals, bundle delta,        │
│               │  │   Lighthouse score, slow query log      │
│               │  │ • Block deploy if threshold breach      │
│               │  │ • Output: Perf report + pass/fail       │
└───────┬───────┘  └──────────────────┬──────────────────────┘
        └──────────────────┬──────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  6. DEPLOY AGENT                                             │
│     • CI/CD: GitHub Actions / automated pipeline            │
│     • Manual: `npx wrangler pages deploy dist`              │
│     • Automated rollback trigger on deploy failure          │
│     • Share deployment URL with user                        │
│     • Output: Live URL + environment status                  │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  7. INFRASTRUCTURE AGENT (EXTENDED tier only)               │
│     • Terraform, IaC, CI/CD, environment config             │
│     • Always preview first: `terraform plan` / dry-run      │
│     • Output: `.github/workflows/`, `wrangler.toml`         │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  8. OBSERVABILITY AGENT (EXTENDED tier only)                │
│     • Structured logging, monitoring, tracing, alerts       │
│     • Configure Sentry/DataDog or Cloudflare Tail Workers   │
│     • Write production signal summary to                    │
│       .ai/sessions/production_signals.md                    │
│     • Output: Structured logs + dashboard config            │
│               + production_signals.md for next session      │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  0c. SESSION STATE AGENT (close)                            │
│     • Serialize: decisions made, files changed, failures    │
│     • Append new Lessons Learned entries                    │
│     • Update task graph (completed / blocked / next)        │
│     • Update docs/06-performance.md with latest baselines   │
│     • Write checkpoint to .ai/sessions/YYYY-MM-DD_topic.md  │
│     • Output: Session artifact + updated memory             │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline Tiers

> **v3 change:** The pipeline is split into CORE (always) and EXTENDED (conditional). This eliminates unnecessary agent activation on simple changes without reducing rigor on complex ones.

### CORE Pipeline (mandatory for every change)

| Step | Agent | Always Required |
|------|-------|----------------|
| 0a | Session State (open) | Yes |
| 0b | Triage / Classifier | Yes |
| 1 | Research | Yes |
| 2 | Design | Yes |
| 3a | Code (front-end) | Yes — even if no UI changes; validates no regressions |
| 4a | Documentation | Yes |
| 4b | Test | Yes |
| 5 | Audit | Yes |
| 6 | Deploy | Yes |
| 0c | Session State (close) | Yes — even on failure |

### EXTENDED Pipeline (activate when triggered)

| Step | Agent | Trigger |
|------|-------|---------|
| 3b | Backend | Any API route, handler, or middleware change |
| 3c | Database | Any schema, migration, or ORM change |
| 3d | Auth | Any authentication, authorization, or session change |
| 3e | Contract Validation | Any session where 2+ parallel agents ran |
| 3f | Integration | Any third-party API, webhook, or payment change |
| 5b | Performance | Any change touching bundle output or rendering path |
| 7 | Infrastructure | Any environment, IaC, or CI/CD config change |
| 8 | Observability | Any production deployment; always after initial deploy |

**Triage decides which EXTENDED agents activate.** If uncertain, activate and skip (a skipped agent that finds nothing is cheaper than a missed regression).

---

## 3. Triage Decision Matrix

> **v3 change:** Replaces the previous prose classification with a formal scoring rubric. Triage Agent loads the `task-decomposition` skill and scores every incoming request before routing.

### Step 1 — Score the request

| Dimension | Score 1 | Score 2 | Score 3 |
|-----------|---------|---------|---------|
| **Files touched** | 1–3 files | 4–10 files | 11+ files |
| **Security surface** | No auth/secrets change | Auth config change | New auth flow or role |
| **User-visible change** | Internal only | Existing UI modified | New UI surface |
| **Reversibility** | One-command rollback | Migration required | Schema + migration |
| **External dependency** | None | Existing service | New third-party service |

**Total score → pipeline mode:**

| Score | Mode | Pipeline tier |
|-------|------|---------------|
| 5–7 | **AUTONOMOUS** | CORE only |
| 8–11 | **GATED** | CORE + relevant EXTENDED |
| 12–15 | **GATED + ESCALATE** | CORE + all relevant EXTENDED + user review before deploy |

### Step 2 — Classify request type

| Type | Examples | Default mode |
|------|---------|-------------|
| Hotfix | Lint fix, broken import, missing semicolon | AUTONOMOUS (score override to 5) |
| Refactor (internal) | Rename variable, extract function, reorganize imports | AUTONOMOUS if score ≤7 |
| Test addition | New unit or integration test file | AUTONOMOUS |
| Doc update | .md file change, comment update | AUTONOMOUS |
| Dependency patch | Minor/patch version bump, `npm audit fix` | GATED — always check breaking changes |
| New feature | New component, route, API endpoint | GATED |
| UI change | Any visible layout, color, or interaction change | GATED |
| Auth change | Any authentication or authorization modification | GATED + ESCALATE |
| Schema change | Any database migration | GATED + ESCALATE |
| Scope expansion | Adds capability not in the current design | GATED + ESCALATE |

### Step 3 — Decompose if parallel

If the request scores 8+ AND touches multiple independent layers (UI + API + DB), decompose into parallel sub-tasks and generate an **Agent Contract** (see Section 5).

### Triage rules
1. **When in doubt, score higher.** Autonomous is an optimization, not a default.
2. **A classification is irreversible mid-run.** If autonomous routing was wrong, stop and escalate; do not try to re-classify.
3. **Score the actual change, not the stated intent.** "Just a small UI tweak" that touches auth middleware scores as auth change.

---

## 4. Agent Definitions

### Core Pipeline Agents

| # | Agent | Responsibility | Trigger | Output |
|---|-------|---------------|---------|--------|
| 0a | **Session State (open)** | Load prior context, task graph, env status, production signals | Start of every session | Hydrated session context |
| 0b | **Triage / Classifier** | Score request via Decision Matrix, assign tier, route | After session open | Score + tier + routing decision + task graph |
| 1 | **Research** | Search expert sources, incorporate production signals | Any UI/UX, data, or backend question | Research summary with citations |
| 2 | **Design** | Create section-by-section plan, produce Agent Contract if parallel, await approval | After research, before any code | Approved design plan + Agent Contract |
| 3a | **Code (Front-end)** | React/TSX, Tailwind, shared UI components | After design approval | Clean, typed, minimal UI code |
| 4a | **Documentation** | Heuristic diff analysis, deterministic .md routing, flag stale docs | After contract validation (or after 3a if CORE only) | Updated .md files with timestamps |
| 4b | **Test** | Unit, integration, and E2E tests | After documentation pass | Test report (pass/fail) |
| 5 | **Audit** | Build, lint, typecheck, security review | After tests pass | Clean build + security report |
| 6 | **Deploy** | Deploy to hosting platform, automated rollback on failure | After clean build + perf pass | Live URL + environment status |
| 0c | **Session State (close)** | Serialize session, update task graph, update performance baselines, append lessons learned | End of every session — including failures | Session artifact + updated memory |

### Extended Pipeline Agents

| # | Agent | Responsibility | Trigger | Output |
|---|-------|---------------|---------|--------|
| 3b | **Backend** | API routes, handlers, middleware, caching | Design includes data/API changes | Working REST/GraphQL API layer |
| 3c | **Database** | Schema design, migrations, CRUD, indexing | Backend requires persistence | Migration files + typed ORM models |
| 3d | **Auth** | JWT sessions, OAuth, password hashing, RBAC | User accounts or protected routes | Auth middleware + login/register flows |
| 3e | **Contract Validation** | Validate all parallel agent outputs against Agent Contract | Any session with 2+ parallel agents | Contract validation report (pass/fail) |
| 3f | **Integration** | Third-party APIs, webhooks, MCP, payments | External service needed | Typed API clients + webhook handlers |
| 5b | **Performance** | Web Vitals, bundle delta, slow queries, Lighthouse regression | Any bundle-affecting change | Perf report + pass/fail |
| 7 | **Infrastructure** | Terraform, IaC, CI/CD, environment config | New environment or service | `.github/workflows/`, infra code |
| 8 | **Observability** | Logging, monitoring, tracing, alerts; write production signals | Production deployment | Structured logs + dashboard config + `production_signals.md` |

### Autonomous-Run Agents

| # | Agent | Autonomous Authority |
|---|-------|---------------------|
| 0a/c | **Session State** | Full — no approval needed |
| 0b | **Triage / Classifier** | Full — routing decision is autonomous |
| 3e | **Contract Validation** | Full — block or pass, no approval needed |
| 4a | **Documentation** | Full — doc updates never need approval |
| Recovery | **Recovery** | Auto-fix: lint, type, unused imports only. Escalate all else. |
| 5b | **Performance** | Can block deploys autonomously |

