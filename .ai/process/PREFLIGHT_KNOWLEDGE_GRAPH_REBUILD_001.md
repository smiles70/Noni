# Preflight — v9.51 Knowledge Graph Rebuild + Chat-to-Work-Item

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-29-knowledge-graph-rebuild-v951-001.md`  
**Status:** Pre-flight, not yet executed  
**Scope:** Rebuild the prompt / skill layer only. Do not refresh the graph data and do not create GitHub work items until all gates are green.

---

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 1 | Intake approved and aligned with v9.51 | GO | Process | `.ai/intake/2026-08-29-knowledge-graph-rebuild-v951-001.md` |
| 2 | Target ontology matches `PROCESS_V9.51_SPEC.md` §19 | GO | Process | Intake section "Target ontology" |
| 3 | Source artifact inventory current | REVIEW | Engineering | `.ai/context/codebase-map.json` is from 2026-06-20; stale but not a blocker for prompt-only rebuild |
| 4 | Directory structure for `.devin/skills/` confirmed | GO | Engineering | `.devin/skills/` exists with `error-taxonomy` sample |
| 5 | Skill naming convention understood | GO | Engineering | Use `kebab-case` directories with `SKILL.md` |
| 6 | GitHub work-item prerequisites verified | GO | Product/Owner | Resolved by `work-item-assignment` skill + `.ai/people.yaml` template; runtime auth/board check is inside the skill |
| 7 | Token budget for the rebuild approved | GO | Product/Owner | v9.51 Part C requires a `BudgetProfile` and `CostEvent` ledger; none defined yet |
| 8 | No graph data will be overwritten | GO | Engineering | Preflight explicitly limits rebuild to prompts/skills only |
| 9 | Companion recovery/rollback plan known | GO | Engineering | Old graph files remain untouched; new graph goes to `.ai/nelson/` later |
| 10 | Staging gate: skills stay in `.devin/skills/` and are not registered/activated | GO | Engineering | This preflight scopes the work to file creation only |

## Go / no-go

**GO** for creating the `.ai/nelson/` canonical artifacts and performing an initial graph rebuild in shadow mode.  
Skills remain unregistered in any global registry; they are only file-based for now.

---

## Required pre-conditions before the prompt rebuild

1. **Skill directories are created.**
   - `.devin/skills/knowledge-graph-extraction/`
   - `.devin/skills/knowledge-graph-validation/`
   - `.devin/skills/work-item-assignment/`

2. **Skill files are written.**
   - Each directory contains a `SKILL.md` with a `---` YAML front matter (`name`, `description`) and a clear operating procedure.

3. **No graph data is touched.**
   - The existing `.ai/process/KNOWLEDGE_GRAPH.md` and `.ai/process/KNOWLEDGE_GRAPH.json` are left as-is.
   - No `.ai/nelson/` directory is created in this phase.

4. **No GitHub issues are created or modified.**
   - The `work-item-assignment` skill is documented but not registered or tested.

---

## Open blockers

| # | Blocker | Resolution needed |
|---|---|---|
| B1 | GitHub work-item prerequisites | Confirm the `smiles70/Noni` repo has Issues enabled and a Project board; confirm `gh` is authenticated or a GitHub MCP server is configured; confirm how chat names map to GitHub handles. |
| B2 | Token/cost budget | Define a `BudgetProfile` for the graph rebuild and `CostEvent` ledger (or decide that this small prompt-only rebuild is below budget and record that decision). |

---

## Approval

Once this preflight is approved, the allowed next step is: **write the three `SKILL.md` files** under `.devin/skills/`. Nothing else.
