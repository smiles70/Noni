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

