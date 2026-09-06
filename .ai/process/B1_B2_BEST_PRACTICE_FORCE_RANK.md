# B1 + B2 Best-Practice Research and Force Rank

**Date:** 2026-08-29  
**Context:** Resolve preflight blockers B1 (GitHub work-item prerequisites) and B2 (token/cost budget) for the v9.51 knowledge graph rebuild.

---

## B1 — GitHub work-item assignment from chat

### Top 3 best-in-class patterns

| Rank | Pattern | Source | Strengths | Weaknesses |
|---|---|---|---|---|
| 1 | **Native `gh` CLI + GitHub Projects v2** | `ghpm`, `github-kanban-agents`, GitHub CLI docs | No extra dependencies, works in any terminal, supports `gh issue create`, `gh issue edit --assignee`, `gh project item-add` | Requires `gh` auth and a known project number; no natural-language parsing |
| 2 | **Claude-gh-task-manager pattern** | `kburson/claude-gh-task-manager` | Always self-assigns, tracks estimate/size, records session time and context length for cost visibility | Heavy process, opinionated, assumes continuous Claude Code use |
| 3 | **Orchestrated YAML bulk tool (OrcAI)** | `dburriss/orca` | Declarative YAML, idempotent, bulk issue creation across repos, auto board + nudge | Overkill for a single repo, requires config file, not chat-native |

### Adaptation for this repo

**Chosen pattern:** #1 — native `gh` CLI wrapped in a Devin skill.

- The skill lives at `.devin/skills/work-item-assignment/SKILL.md`.
- It uses `gh issue create` with `--repo smiles70/Noni`, `--assignee`, and `--body-file`.
- It uses `gh project item-add <number> --owner smiles70 --url <issue-url>` for board linkage.
- It keeps a `.ai/people.yaml` mapping for chat-name → GitHub handle.
- If `gh` is not authenticated, it prints the exact command set for the user to run instead of failing silently.

---

## B2 — Token / cost budget for AI-assisted work

### Top 3 best-in-class patterns

| Rank | Pattern | Source | Strengths | Weaknesses |
|---|---|---|---|---|
| 1 | **Record actual spend, cap before each call** | `agent.mue.app`, AgentBudget whitepaper | Uses provider-reported usage, not estimates; hard circuit-break on budget exhausted | Requires provider API to report usage per call; Devin does not expose this yet |
| 2 | **Per-run ledger with dimensional counters** | Solana Garden / Harbor Support | Append-only `CostEvent` with `run_id`, `event_type`, `model`, `cost_usd`, `tenant_id`, `product`, `environment` | Manual ledger if API usage is not available; requires discipline |
| 3 | **Kernel-owned token budget tracker** | Microsoft agent-governance-toolkit | Kernel owns budget, agents request allocations, `ContextScheduler` enforces 90/10 lookup/reasoning split | Too heavy for a single repo; needs a runtime kernel |

### Adaptation for this repo

**Chosen pattern:** #2 — manual per-run ledger with a simple cap.

- Budget file: `.ai/budgets/knowledge-graph-rebuild-001.yaml`.
- Fields: `max_usd`, `consumed_usd`, `per_call_usd`, `cost_events`.
- Each skill that uses model/tool calls appends a `CostEvent` with estimated and actual USD.
- Before any expensive run, the skill checks `consumed_usd < max_usd` and stops if the cap is reached.
- This is a manual ledger because Devin does not expose real-time token/cost APIs. Once those are available, the skill can be upgraded to pattern #1.

---

## Resolution

Both blockers are now resolved by **documentation and skill design**, not by requiring infrastructure that does not yet exist:

- **B1 resolved:** `work-item-assignment` skill + `.ai/people.yaml` template.
- **B2 resolved:** `BudgetProfile` / `CostEvent` ledger in `.ai/budgets/knowledge-graph-rebuild-001.yaml`.
