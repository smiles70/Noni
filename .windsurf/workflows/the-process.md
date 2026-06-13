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

---

## 5. Agent Contract Layer

> **v3 addition:** When 2 or more parallel agents run (any combination of 3a–3f), the Design Agent must produce an Agent Contract before implementation begins. The Contract Validation Agent (3e) enforces it before Documentation runs.

### What an Agent Contract specifies

```markdown
## Agent Contract — [Feature Name]
Generated by: Design Agent
Session: YYYY-MM-DD_topic
Approved: [timestamp]

### API Endpoints
| Method | Path | Request shape | Response shape | Owner agent |
|--------|------|--------------|----------------|-------------|
| POST   | /api/users | `{ email: string, password: string }` | `{ id: string, token: string }` | 3b Backend |
| GET    | /api/users/:id | — | `{ id: string, email: string, role: string }` | 3b Backend |

### Database Schema Diffs
| Table | Change | Owner agent |
|-------|--------|-------------|
| users | ADD COLUMN `role` TEXT DEFAULT 'viewer' | 3c Database |
| sessions | CREATE TABLE with columns: id, user_id, token, expires_at | 3c Database |

### Auth Interfaces
| Middleware | Route pattern | Expected header | Owner agent |
|-----------|--------------|-----------------|-------------|
| `requireAuth` | /api/* (except /api/auth/*) | `Authorization: Bearer <jwt>` | 3d Auth |
| `requireRole('admin')` | /api/admin/* | same + role claim in JWT | 3d Auth |

### Front-End Expectations
| Component | Data it consumes | Source |
|-----------|-----------------|--------|
| `LoginForm` | POST /api/auth/login → token | 3b Backend |
| `UserProfile` | GET /api/users/:id → user object | 3b Backend |

### Undeclared Dependency Rule
Any agent that needs to consume output from another agent not listed above
must flag it before implementing. Undeclared dependencies are contract violations.
```

### Contract Validation Agent (3e) — what it checks

1. **API shape conformance** — does 3b's actual route handler match the Contract's request/response shapes? Use TypeScript types or JSDoc as ground truth.
2. **Schema alignment** — do 3c's migration files produce exactly the tables and columns the Contract specifies?
3. **Auth interface consistency** — does 3d's middleware match the Contract's expected header and claim structure?
4. **Front-end consumption** — does 3a's API call match the Contract's endpoint paths and shapes?
5. **Undeclared dependencies** — any `import` or `fetch` that references another agent's output without being in the Contract is a violation.

### Contract violation handling

| Severity | Condition | Action |
|----------|-----------|--------|
| **BLOCK** | API shape mismatch | Block 4a, escalate to user with diff |
| **BLOCK** | Schema doesn't match Contract | Block 4a, escalate — never auto-resolve schema conflicts |
| **WARN** | Minor response field added | Log warning, allow 4a to proceed |
| **BLOCK** | Undeclared dependency between agents | Block 4a, escalate |

---

## 6. Quality Gate Protocol (Exact Commands)

### Front-End Gates (CORE — Always Required)

```bash
# Gate 1: Unit Tests
npm test

# Gate 2: Build
npm run build

# Gate 3: Lint
npx eslint . --ext .ts,.tsx

# Gate 4: Typecheck
npx tsc --noEmit

# Gate 5: AI Slop Check
npx eslint . --ext .ts,.tsx --rule 'no-unused-vars: error'
```

### Full-Stack Gates (EXTENDED — Required when backend changes)

```bash
# Gate 6: Integration Tests
npm run test:integration

# Gate 7: Security Audit
npm audit
# + Review auth flows (no hardcoded secrets, proper JWT validation)
# + Check for SQL injection vectors in API routes
# + Verify CORS policies are restrictive

# Gate 8: Database Validation
npx prisma migrate status
# + Schema matches Contract
# + No pending migrations in production

# Gate 9: Infrastructure Validation
terraform plan -detailed-exitcode
# + No unintended resource changes
# + Environment variables documented
```

### Performance Gates (EXTENDED — Required when bundle output changes)

```bash
# Gate 10: Bundle Size Check
npx bundlesize
# Fails if any chunk exceeds threshold in package.json bundlesize config
# Thresholds set during Baseline Init (Section 10)

# Gate 11: Lighthouse CI
npx lhci autorun
# Requires .lighthouserc.json — fails if score drops >5 points vs baseline
# Baseline stored in docs/06-performance.md

# Gate 12: Slow Query Detection (full-stack only)
# Review query explain plans for any new ORM queries
# Flag any query without an index on a filtered column
```

**If ANY gate fails:** Recovery Agent activates. Do NOT commit or deploy until all gates pass. Security gate failures are BLOCKERS — never deploy with known vulnerabilities.

---

## 7. Production Feedback Loop

> **v3 addition:** Closes the gap between Observability (step 8) and the next session's Research and Design agents. Production signals from real traffic inform the next planning cycle.

### How it works

**At session close (or after Observability agent runs):**

The Observability Agent writes a structured summary to `.ai/sessions/production_signals.md`:

```markdown
## Production Signals — [timestamp]
Source: Sentry / DataDog / Cloudflare Tail Workers
Period: last 7 days

### Error rates
| Route | Error rate | Count | Top error |
|-------|-----------|-------|-----------|
| POST /api/auth/login | 2.3% | 847 | "Invalid JWT signature" |
| GET /api/users/:id | 0.1% | 12 | "User not found" |

### Performance regressions
| Page / Route | P75 before | P75 after | Delta |
|-------------|-----------|---------|-------|
| /dashboard | 1.2s | 2.8s | +133% |

### Slow queries
| Query | Avg duration | Missing index |
|-------|-------------|--------------|
| SELECT * FROM sessions WHERE user_id = ? | 340ms | Yes — user_id |

### Bundle changes
| Chunk | Before | After | Delta |
|-------|--------|-------|-------|
| main.js | 142kb | 198kb | +39% |
```

**At session open (0a):**

Session State Agent reads `production_signals.md` and injects into context:
- Research Agent uses error patterns to direct investigation
- Design Agent uses regressions to prioritize fixes
- Performance Agent uses slow query log to flag missing indexes

**Signal freshness:**
- If `production_signals.md` is older than 7 days, Session State Agent flags it as stale and prompts user to run `/observability` before proceeding.
- If no `production_signals.md` exists (new project or no prod deploy yet), skip silently.

---

## 8. Slash Commands

| Command | Agent | What It Does | Exact Script |
|---------|-------|--------------|------------|
| `/triage` | Triage | Score request via Decision Matrix, assign tier, output task graph | Score → classify → tier → route → decompose |
| `/session-open` | Session State | Load prior context + production signals into active session | Read `.ai/sessions/` + ARCHITECTURE.md + lessons + production_signals.md |
| `/session-close` | Session State | Serialize session, update baselines, write production signals | Write `.ai/sessions/YYYY-MM-DD_topic.md` + update `docs/06-performance.md` |
| `/design-audit` | Design | Review visual hierarchy, color psychology, CTA placement, WCAG compliance | Research → analyze current UI → suggest improvements |
| `/contract` | Design + Contract Validation | Generate or validate Agent Contract for current session | Read design plan → produce contract → run 3e validation |
| `/code-check` | Audit | Run lint + typecheck + slop audit in one command | `npm run build && npm test && npx eslint . --ext .ts,.tsx && npx tsc --noEmit` |
| `/security` | Audit | Full security audit: dependencies, secrets, XSS vectors | `npm audit` + scan for `dangerouslySetInnerHTML`, inline handlers, missing `rel="noopener noreferrer"` |
| `/ai-slop` | Audit | Detect AI-generated code smells: duplicates, unused vars, placeholders | `npx eslint . --ext .ts,.tsx --rule 'no-unused-vars: error' && grep -r "Lorem ipsum\|Click here\|TODO\|FIXME" .` |
| `/perf` | Performance | Run full performance gate vs stored baselines | `npx bundlesize && npx lhci autorun` |
| `/perf-baseline` | Performance | Initialize or reset performance baselines | Run gates 10–11, write results to `docs/06-performance.md` + `.lighthouserc.json` |
| `/recover` | Recovery | Diagnose latest gate failure and attempt fix | Classify failure → apply fix → re-run failed gate |
| `/rollback` | Recovery | Roll back to last clean state | `git revert HEAD` or platform rollback command |
| `/docs-sync` | Documentation | Sync all .md files against current codebase via heuristic checklist | Diff code → apply Section 9 heuristics → update .md files |
| `/production-signals` | Observability | Pull latest signals from Sentry/DataDog and write to production_signals.md | Fetch errors, perf, slow queries → write `.ai/sessions/production_signals.md` |
| `/optimize-hero` | Design + Code | Run conversion optimization on hero/landing section | Research CRO best practices → redesign hero → implement → test |
| `/add-test` | Test | Scaffold test file for current component | Create `__tests__/{component}.test.tsx` with React Testing Library boilerplate |
| `/sprint-report` | Docs | Update epic markdown with progress | Append to `.cursor/epics/*.md` with timestamp and changes |
| `/full-gate` | All | Run complete CORE quality gate suite | Execute gates 1–5 sequentially |
| `/fullstack-gate` | All | Run complete CORE + EXTENDED quality gate suite | Execute gates 1–9 sequentially |
| `/perf-gate` | Performance | Run performance gate suite vs baselines | Execute gates 10–12 sequentially |
| `/backend-scaffold` | Backend | Scaffold API routes, middleware, error handling | Create `app/api/` structure with typed handlers |
| `/db-migrate` | Database | Generate and apply database migration | `npx prisma migrate dev --name {name}` (or equivalent) |
| `/auth-setup` | Auth | Configure JWT/OAuth auth with protected routes | Add auth middleware, login/register endpoints |
| `/infra-plan` | Infrastructure | Preview infrastructure changes before deploy | `terraform plan` or `wrangler deploy --dry-run` |
| `/observability` | Observability | Add structured logging and error tracking | Configure Sentry/DataDog or Cloudflare Tail Workers |

---

## 9. Documentation Agent Heuristics

> **v3 addition:** Replaces vague "read diffs" instruction with a deterministic routing checklist. The Documentation Agent runs this checklist on every diff before writing a single .md file.

### Heuristic Checklist (run in order)

```
FOR EACH changed file in the diff:

  IF new exported function or method added:
    → Append to docs/04-tech.md under "API / Functions"
    → Include: signature, purpose, usage example

  IF existing exported function removed or signature changed:
    → Update docs/04-tech.md
    → Flag in docs/03-system.md as "Breaking change — [date]"

  IF new database table or collection created:
    → Append to docs/03-system.md under "Data Layer"
    → Include: table name, columns, purpose, relations

  IF existing database table modified (column add/remove/rename):
    → Update docs/03-system.md table entry
    → Append migration note with date and direction (up/down)

  IF new API route created (REST endpoint or GraphQL mutation/query):
    → Append to docs/04-tech.md under "API Contracts"
    → Append to docs/ARCHITECTURE.md under "API Layer"
    → Include: method, path, request shape, response shape, auth required

  IF existing API route removed or path changed:
    → Update docs/04-tech.md + ARCHITECTURE.md
    → Flag as "Deprecated / Removed — [date]"

  IF new auth middleware or role created:
    → Append to docs/05-security.md under "Auth Flows"
    → Include: middleware name, route pattern, token requirements

  IF auth configuration changed (provider, session strategy, JWT config):
    → Update docs/05-security.md
    → Flag in docs/ARCHITECTURE.md as "Auth change — [date]"

  IF new third-party service integrated:
    → Append to docs/03-system.md under "Integrations"
    → Append to docs/04-tech.md under "Dependencies"
    → Include: service name, purpose, credentials required

  IF new environment variable required:
    → Append to docs/04-tech.md under "Environment Variables"
    → Append to .env.example with placeholder value and comment

  IF new npm package installed (not devDependency):
    → Append to docs/04-tech.md under "Dependencies"
    → Include: package name, version, purpose

  IF new React component created at src/components/:
    → Append to docs/03-system.md under "Component Map"
    → Include: component name, props summary, usage context

  IF existing component deleted:
    → Update docs/03-system.md — mark as removed, date

  IF CI/CD pipeline or GitHub Actions workflow changed:
    → Update docs/ARCHITECTURE.md under "CI/CD & Deployment"

  IF infra changed (wrangler.toml, terraform, platform config):
    → Update docs/ARCHITECTURE.md under "Infrastructure"

  IF nothing above matches:
    → No .md update required; log "no documentation change triggered"
```

### Documentation Agent rules
1. **Never rewrite from scratch.** Append and update only. Use `## [Section] — updated [date]` headers for major updates.
2. **Timestamp every entry.** Format: `<!-- updated: YYYY-MM-DD by DocumentationAgent -->` at end of changed section.
3. **Never delete historical context.** Removed features are marked "Removed — [date]", not deleted.
4. **One pass per session.** Run the full checklist once after all code agents complete, not incrementally.
5. **Flag stale docs.** If a .md file references a component or route that no longer exists, add a `⚠️ STALE — verify [date]` marker.

---

## 10. Performance Baseline Init

> **v3 addition:** Ensures the Performance Agent always has a valid baseline to compare against. Run this once per project before the first deploy that activates Gate 10 or 11.

### When to run

- **New project:** After the first working build, before the first production deploy.
- **Inherited project:** Before the first session that includes a performance gate.
- **After a major refactor:** If the app's core architecture changed, reset baselines.
- **Slash command:** `/perf-baseline` 

### Baseline Init procedure

```bash
# Step 1: Build a clean reference build
npm run build

# Step 2: Run Lighthouse against the built output
# (serve locally first if Lighthouse requires a running server)
npx serve dist &
npx lhci collect --url=http://localhost:3000
npx lhci upload --target=filesystem --outputDir=.lighthouseci

# Step 3: Read the scores from the report
# Record: Performance, Accessibility, Best Practices, SEO scores

# Step 4: Write .lighthouserc.json with floor thresholds
# Floor = (actual score) - 5 points (acceptable drift)
```

**Generated `.lighthouserc.json`:**

```json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.75 }],
        "categories:accessibility": ["error", { "minScore": 0.90 }],
        "categories:best-practices": ["error", { "minScore": 0.85 }],
        "categories:seo": ["warn", { "minScore": 0.80 }],
        "first-contentful-paint": ["warn", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 3000 }],
        "total-blocking-time": ["error", { "maxNumericValue": 300 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
      }
    },
    "collect": {
      "numberOfRuns": 3,
      "url": ["http://localhost:3000"]
    }
  }
}
```

**Generated `docs/06-performance.md` baseline entry:**

```markdown
## Performance Baseline — [date]
Initialized by: Performance Agent / /perf-baseline
Build: [git sha]

### Lighthouse Scores
| Metric | Score | Floor (−5pts) |
|--------|-------|---------------|
| Performance | 82 | 77 |
| Accessibility | 96 | 91 |
| Best Practices | 92 | 87 |
| SEO | 88 | 83 |

### Core Web Vitals
| Metric | Value | Threshold |
|--------|-------|-----------|
| FCP | 1.4s | 2.0s |
| LCP | 2.1s | 3.0s |
| TBT | 180ms | 300ms |
| CLS | 0.04 | 0.1 |

### Bundle Sizes
| Chunk | Size | Budget |
|-------|------|--------|
| main.js | 142kb | 200kb |
| vendor.js | 380kb | 450kb |

### Notes
[Any known issues or planned improvements at time of baseline]
```

### Baseline update rules
1. **Never lower thresholds without user approval.** If a legitimate architectural change causes a regression (e.g., adding a rich text editor), the user must explicitly approve the new baseline.
2. **Update baselines at every session close** (0c) with the latest passing scores. Do not reset — append a new dated entry.
3. **If no baseline exists,** the Performance Agent skips the comparison check and warns: "No baseline found — run `/perf-baseline` before next deploy."

---

## 11. Recovery Agent Playbook

### Activation

Recovery Agent activates automatically when any gate (1–12) fails. The failing agent does not retry itself.

### Decision Tree

```
Gate failure detected
        │
        ▼
Classify failure (load error-taxonomy skill)
        │
        ├── lint / type error / unused import
        │       → Auto-fix, re-run gate, no approval
        │
        ├── test failure (unit or integration)
        │       → Write diagnosis to .ai/recovery/
        │       → Escalate to user with fix options
        │
        ├── contract violation (from 3e)
        │       → Hard stop
        │       → Write diff between actual and Contract
        │       → Escalate — never auto-resolve contract conflicts
        │
        ├── security block
        │       → Hard stop immediately
        │       → Escalate with CVE details
        │       → Never auto-fix
        │
        ├── performance regression
        │       → Block deploy
        │       → Escalate with before/after scores from docs/06-performance.md
        │       → Never auto-fix
        │
        ├── migration conflict
        │       → Hard stop
        │       → Escalate — never auto-resolve schema conflicts
        │
        └── infra drift
                → Run `terraform plan` output for user review
                → Never auto-apply
```

### Attempt Ceiling
- Max 3 auto-fix attempts per failure
- After 3 attempts: write `.ai/recovery/YYYY-MM-DD_failure.md` with full diagnosis and stop
- Session State Agent checkpoints the failure before exit

---

## 12. Skills Inventory

| Skill | Use For |
|-------|---------|
| `agents-sdk` | Build AI agents on Cloudflare Workers, stateful agents, durable workflows |
| `cloudflare` | Workers, Pages, KV, D1, R2, AI, Vectorize, networking, security |
| `cloudflare-email-service` | Send/receive transactional emails, SPF/DKIM/DMARC |
| `durable-objects` | Stateful coordination: chat rooms, multiplayer, booking systems |
| `sandbox-sdk` | Secure code execution, AI code interpreters |
| `turnstile-spin` | Bot protection, CAPTCHA alternative |
| `web-perf` | Core Web Vitals audit, Lighthouse scores, render-blocking |
| `workers-best-practices` | Production Worker patterns, streaming, secrets, observability |
| `wrangler` | Deploy Workers, KV, R2, D1, Pages |
| `mcp` | Model Context Protocol — connect AI to databases, APIs, file systems |
| `prisma` | Database ORM, schema design, migrations, type-safe queries |
| `nextjs-api` | Next.js API routes, server actions, middleware, caching |
| `auth-js` | NextAuth.js, OAuth providers, JWT sessions, RBAC |
| `stripe` | Payment processing, subscriptions, webhooks |
| `terraform` | Infrastructure as Code, cloud resource management |
| `task-decomposition` | Triage Decision Matrix scoring, parallel task decomposition |
| `rollback-patterns` | Git revert, DB migration rollbacks, platform rollback commands |
| `error-taxonomy` | Classify failures; standard remediation playbook per type |
| `agent-contract` | Contract template generation, contract validation rules |
| `performance-baseline` | Baseline init procedure, `.lighthouserc.json` generation |
| `production-signals` | Signal schema, Sentry/DataDog query patterns, staleness rules |

---

## 13. Lessons Learned & Gotchas

| # | Lesson | Root Cause | Fix |
|---|--------|-----------|-----|
| 1 | **Never skip Design Agent approval** — even for "small" changes | Implemented single-column change without approval → had to revert | Always present plan, wait for explicit user approval |
| 2 | **Red for neutral policies is psychologically wrong** | Used `bg-red-500` + `Ban` icon for "No Pets" | `bg-slate-100 text-slate-700` + factual icons |
| 3 | **Single column in a wide card creates "dead zones"** | Attempted `grid-cols-1` to fix height mismatch | Balance column content instead of removing columns |
| 4 | **Always reference the user's model** | Created generic `Ban` prohibition instead of paw print | Recreated icons matching user's TurboTenant reference |
| 5 | **Research before designing** — never guess UI solutions | Guessed single-column solution without checking guidance | Consult Baymard, Material Design, Airbnb, Zillow first |
| 6 | **30% rule for rent is gross (pre-tax) income** | User asked about net vs gross income estimate | Cited SoFi, AmEx, HUD; explained 1969 Brooke Amendment |
| 7 | **No unauthorized scope decisions** | User enforced after pricing card incident | Always ask before expanding scope |
| 8 | **Always check actual filenames** | User said "alaini" but files were "alaina" | Listed public folder before implementing download |
| 9 | **Never persist tenant auth in localStorage** | PIN screen was being skipped on reload | Remove localStorage, always show PIN first |
| 10 | **Base64 encoding does not obfuscate PINs** | PIN was visible in localStorage | Used state-only, no persistence |
| 11 | **Recovery Agent has a 3-attempt ceiling** — never loop forever | Infinite retry on broken test stalled the pipeline | After 3 failed attempts, write diagnosis and escalate |
| 12 | **Triage classification is irreversible mid-run** | Autonomous routing on a UI change caused a revert | When in doubt, Triage defaults to GATED |
| 13 | **Session State close is mandatory even on failure** | Interrupted session lost all context | Session State Agent writes checkpoint on exit regardless |
| 14 | **Performance gate failures block deploy as firmly as security failures** | A passing build with a 40% Lighthouse regression shipped | Add perf thresholds at project setup via `/perf-baseline` |
| 15 | **Documentation Agent runs before Test, not after** | Tests passed but ARCHITECTURE.md was 2 sprints out of date | Doc Agent diffs code and updates .md files before test suite |
| 16 | **Parallel agents can silently diverge from each other** | Backend assumed a different auth header than Auth agent produced | Agent Contract (Section 5) prevents divergence before it happens |
| 17 | **Performance baselines without initialization are meaningless** | First deploy failed Gate 11 with no baseline to compare against | Run `/perf-baseline` before first performance-gated deploy |
| 18 | **Production errors invisible to planning without a feedback loop** | Auth bug recurred across 3 sessions; none knew about the 2.3% error rate | Observability Agent writes production_signals.md; Session Open loads it |
| 19 | **"Minor" dependency bumps can break contract shapes** | A patch version of a UI library changed a prop type; no gate caught it | Dependency updates score as GATED in the Triage Decision Matrix |

---

## 14. Process Enforcement Rules

1. **Full pipeline for ANY change:** Session Open → Triage → Research → Design → Code → Docs → Test → Audit → (Perf if EXTENDED) → Deploy → Session Close
2. **CORE tier is always active.** EXTENDED agents activate per Triage Decision Matrix.
3. **Design Agent plan must be approved by user** before coding — unless Triage scored AUTONOMOUS.
4. **If 2+ parallel agents run, an Agent Contract is required** before any implementation begins.
5. **Contract Validation (3e) must pass before Documentation (4a) runs.**
6. **Zero warnings tolerated** in build — fix all lint/type errors before deploy.
7. **No unauthorized scope decisions** — user approval required before any implementation.
8. **Research before designing** — never guess UI or API solutions.
9. **Reference the user's model** — match screenshots, icons, layouts, and API contracts precisely.
10. **Always run the full gate for the active tier** — never skip Test, Audit, or Perf to save time.
11. **Security gate failures are BLOCKERS** — never deploy with known vulnerabilities.
12. **Database migrations must be reversible** — always generate `down` migration.
13. **Auth changes require security review** — Auth Agent must pass Audit Agent before deploy.
14. **Infrastructure changes must be previewed** — `terraform plan` or dry-run before apply.
15. **Recovery Agent activates on any gate failure** — the failing agent never retries itself.
16. **Recovery Agent auto-fix authority is bounded** — lint, type errors, unused imports only.
17. **Recovery Agent 3-attempt ceiling** — after 3 failed attempts, write diagnosis and stop.
18. **Session State checkpoint after every agent** — not just end of session.
19. **Session State close is mandatory on failure** — always checkpoint before exit.
20. **Triage defaults to GATED when uncertain** — AUTONOMOUS is an optimization, not a shortcut.
21. **Performance regressions block deploy** — thresholds set at baseline init, never lowered without user approval.
22. **Documentation Agent runs before Test** — docs must reflect code before tests validate it.
23. **Observability Agent writes production signals after every prod deploy.**
24. **Session Open loads production signals** — Research and Design agents must incorporate them.
25. **No baseline, no perf gate** — if `docs/06-performance.md` has no baseline, run `/perf-baseline` first.

---

## 15. UI/UX Conventions (Adapt Per Project)

| Convention | Value | Usage |
|------------|-------|-------|
| Primary color | `#1e3a5f` (navy) | Headers, borders, active states |
| Success color | `#4caf50` (green) | Completed steps, positive values, badges |
| Warning color | `#f59e0b` (amber) | Medium credit scores, caution states |
| Danger color | `#ef4444` (red) | ONLY for actual errors/negatives, never neutral policies |
| Neutral color | `#64748b` (slate) | Neutral policies, placeholders |
| Border radius | `rounded-2xl` (1rem) | Cards, containers |
| Card border | `border-2 border-navy-200` | Consistent card styling |
| Icon library | Shared `Icon` component, never inline SVG | `components/ui/icon.tsx` |
| Focus states | `focus-visible`, never `focus:outline-none` | Accessibility compliance |
| Completed timeline | Green filled dots + navy connecting lines | Visual consistency |

---

## 16. File System Documentation

### Universal Folder Structure

```
project-root/
│
├── .ai/                              # AI WORKSPACE
│   ├── process/
│   │   └── the-process.md           # This file
│   ├── sessions/                     # Session State Agent checkpoints
│   │   ├── YYYY-MM-DD_topic.md
│   │   ├── active_checkpoint.md     # Overwritten after every agent
│   │   └── production_signals.md    # Written by Observability, read by Session Open
│   ├── contracts/                    # Agent Contracts per session
│   │   └── YYYY-MM-DD_topic_contract.md
│   ├── recovery/                     # Recovery Agent logs
│   │   └── YYYY-MM-DD_failure.md
│   └── skills/
│       └── [skill-name]/
│           ├── SKILL.md
│           └── [detailed-guide].md
│
├── docs/                             # PROJECT DOCUMENTATION
│   ├── 01-instruction.md
│   ├── 02-product.md
│   ├── 03-system.md
│   ├── 04-tech.md
│   ├── 05-security.md
│   └── 06-performance.md            # Baselines updated by Performance Agent at session close
│       └── ARCHITECTURE.md
│
├── .github/
│   └── workflows/
│       ├── gate.yml
│       └── deploy.yml
│
├── scripts/
│   ├── full-gate.sh
│   ├── ai-slop-check.sh
│   └── rollback.sh
│
├── .lighthouserc.json               # Generated by /perf-baseline
├── .env.example
└── src/ or app/
```

### Documentation File Ownership

| File | Owner Agent | Update trigger |
|------|------------|----------------|
| `03-system.md` | Documentation Agent | New component, table, integration, infra |
| `04-tech.md` | Documentation Agent | New function, API route, dependency, env var |
| `05-security.md` | Audit Agent | Auth change, new vulnerability, security config |
| `06-performance.md` | Performance Agent | Every passing deploy; baseline init |
| `ARCHITECTURE.md` | Documentation Agent | Stack changes, new integrations, CI/CD changes |

---

## 17. Adaptation Checklist (For New Projects)

### Front-End Setup
- [ ] Update project name and stack in Section 15
- [ ] Update file paths in agent definitions
- [ ] Update color palette in UI/UX Conventions
- [ ] Update deploy command in Deploy Agent
- [ ] Verify test command exists (`npm test` or equivalent)
- [ ] Verify build command exists (`npm run build` or equivalent)

### Full-Stack Setup
- [ ] Choose stack from Section 20 (Cloudflare / Vercel / Supabase)
- [ ] Set up database and ORM (Prisma / Drizzle / Supabase)
- [ ] Configure auth provider (NextAuth / JWT / Supabase Auth)
- [ ] Add API routes or server functions structure
- [ ] Create integration tests (`npm run test:integration`)
- [ ] Set up CI/CD pipeline (GitHub Actions from Section 18)
- [ ] Configure environment variables and secrets

### Performance Baseline Setup (NEW — required before first perf gate)
- [ ] Run `/perf-baseline` after first working build
- [ ] Verify `.lighthouserc.json` was generated with sensible thresholds
- [ ] Verify `docs/06-performance.md` baseline entry was written
- [ ] Set bundle size budgets in `package.json` under `"bundlesize"` key

### Production Signals Setup (NEW — required before first production deploy)
- [ ] Configure Sentry / DataDog / Cloudflare Tail Workers
- [ ] Verify Observability Agent can write to `.ai/sessions/production_signals.md` 
- [ ] Set signal freshness threshold (default: 7 days)
- [ ] Define escalation contacts for Recovery Agent

### Autonomous-Run Setup
- [ ] Configure Triage Decision Matrix scoring for this project
  - [ ] Adjust score thresholds if project has unusual risk profile
  - [ ] Add project-specific hotfix patterns to AUTONOMOUS override list
- [ ] Initialize `.ai/sessions/` directory
- [ ] Initialize `.ai/contracts/` directory
- [ ] Add `rollback-patterns` skill with platform-specific rollback commands
- [ ] Define Recovery Agent escalation contacts

### Universal Setup
- [ ] Add project-specific skills to Skills Inventory
- [ ] Review Lessons Learned — remove irrelevant entries, add project-specific ones
- [ ] Create or update workflow file (`.windsurf/workflows/` or `.cursor/rules/`)
- [ ] Initialize `.cursor/` documentation directory with 6 core `.md` files

---

## 18. CI/CD & Automation

### GitHub Actions Pipeline

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build
      - run: npx eslint . --ext .ts,.tsx
      - run: npx tsc --noEmit
      - run: npm audit --audit-level=moderate
      - run: npx bundlesize
      - name: Lighthouse CI
        run: npx lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
  deploy:
    needs: gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      - run: npx wrangler pages deploy dist --project-name=${{ vars.CF_PROJECT_NAME }}
      - name: Rollback on failure
        if: failure()
        run: npx wrangler pages deployments rollback --project-name=${{ vars.CF_PROJECT_NAME }}
```

---

## 19. Session State Agent Specification

### Open Protocol
1. Read `.ai/sessions/` — load most recent session artifact
2. Read `ARCHITECTURE.md` — inject current architecture context
3. Read `docs/06-performance.md` — inject current baselines
4. Read `.ai/sessions/production_signals.md` — inject production error rates, regressions, slow queries
   - If file is older than 7 days, flag as stale
   - If file does not exist, skip silently
5. Read last 3 Lessons Learned entries
6. Output: structured context block injected into all downstream agents

### Checkpoint Protocol (after every agent)
Write to `.ai/sessions/active_checkpoint.md`:
- Which agent just completed
- Files changed
- Decisions made
- Contract status (if applicable)
- Next agent in queue
- Any flags or warnings

### Close Protocol
1. Rename `active_checkpoint.md` → `YYYY-MM-DD_HH-MM_topic.md` 
2. Update `docs/06-performance.md` with latest Lighthouse scores and bundle sizes (if performance gate ran)
3. Append new Lessons Learned entries (if any)
4. Update task graph: mark completed, flag blocked, list next
5. Write summary to memory via `create_memory` 
6. Execute on pipeline SUCCESS and FAILURE — this step is never skipped

---

## 20. Recommended Full-Stack Stacks

### Stack A: Cloudflare Edge

| Layer | Technology |
|-------|-----------|
| Front-end | Next.js 15 (static export) |
| API | Cloudflare Workers |
| Database | Cloudflare D1 (SQLite) |
| Cache | Cloudflare KV |
| Auth | Cloudflare Access / JWT |
| Deploy | Cloudflare Pages + Wrangler |

### Stack B: Vercel + PostgreSQL

| Layer | Technology |
|-------|-----------|
| Front-end | Next.js 15 (App Router) |
| API | Next.js API Routes / Server Actions |
| Database | PostgreSQL + Prisma ORM |
| Auth | NextAuth.js + OAuth |
| Deploy | Vercel CLI / GitHub Integration |

### Stack C: Supabase

| Layer | Technology |
|-------|-----------|
| Front-end | Next.js 15 / React |
| API | Supabase Edge Functions |
| Database | PostgreSQL (Supabase managed) |
| Auth | Supabase Auth (OAuth, Magic Link) |
| Deploy | Vercel + Supabase |

---

## 21. Security Checklist (Auth Agent)

Before any auth feature ships:

- [ ] Passwords hashed with bcrypt/argon2 (never plaintext)
- [ ] JWTs use `HttpOnly`, `Secure`, `SameSite=Strict` cookies
- [ ] CSRF tokens on state-changing requests
- [ ] Rate limiting on login/register endpoints
- [ ] Input validation on all API routes (Zod/Joi)
- [ ] CORS restricted to known origins
- [ ] No secrets in client-side code
- [ ] Environment variables documented in `tech.md` 
- [ ] SQL injection prevented (parameterized queries / ORM)
- [ ] XSS prevented (output encoding, CSP headers)
- [ ] Auth changes validated against Agent Contract (if applicable)

---

## 22. Codebase Assessment Prompt (New Repo Onboarding)

```
I am entering a new codebase. Before writing or modifying any code, I will produce
a comprehensive architecture assessment and write it to ARCHITECTURE.md.

Assessment areas:
1. File system inventory (top-level structure, entry points)
2. Tech stack (framework, runtime, language version, package manager)
3. Architecture pattern (MVC, layered, hexagonal, serverless, monolith)
4. Data layer (ORM, database type, migration strategy)
5. API layer (REST vs GraphQL, route structure, middleware, auth guards)
6. Auth patterns (session vs JWT, OAuth, RBAC, password handling)
7. Front-end (routing, state management, component library, styling)
8. Testing setup (test runner, coverage, mocking, E2E tools)
9. CI/CD (GitHub Actions, Vercel, Cloudflare, manual deploy scripts)
10. Dependencies (outdated packages, known vulnerabilities)
11. Environment configuration (.env files, secrets management)
12. Documentation status (README completeness, API docs)
13. Performance baselines (existing Lighthouse scores, bundle sizes) → docs/06-performance.md
14. Existing .ai/sessions/ checkpoints (resume prior context if found)
15. Existing production_signals.md (inject if found and fresh)

I will not write any code until this assessment is complete and saved to ARCHITECTURE.md.
```

---

*v3: Added Triage Decision Matrix (Section 3), Agent Contract Layer (Section 5), Contract Validation Agent (3e), Production Feedback Loop (Section 7), Documentation Agent Heuristics (Section 9), Performance Baseline Init (Section 10), and Core/Extended pipeline tiers (Section 2).*
*Generated from 60 Walker St Household Portal sessions + v2 analysis.*
*Drop into `.windsurf/workflows/the-process.md` or `.cursor/rules/the-process.md` in any project.*
