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
