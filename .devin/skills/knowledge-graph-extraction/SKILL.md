---
name: knowledge-graph-extraction
description: Extract v9.51 ontology entities from intakes, ADRs, code, and tests for the Mynaani/Noni repo
---

# Knowledge Graph Extraction (v9.51)

## Purpose
Build and incrementally refresh a requirements knowledge graph for the Noni repository that conforms to `PROCESS_V9.51_SPEC.md` §19. Only operates when explicitly invoked. It does **not** auto-refresh on every chat.

## Target ontology

Entities: `SourceArtifact`, `Requirement`, `Capability`, `Epic`, `UserStory`, `AcceptanceCriterion`, `Test`, `Evidence`, `Owner`, `Decision`, `Dependency`, `Gap`, `Conflict`, `Assumption`, `Persona`, `Journey`, `BudgetProfile`, `CostEvent`, `RoutingDecision`.

Relationships: `defined_by`, `refines`, `implements`, `partially_implements`, `verified_by`, `evidenced_by`, `planned_by`, `owned_by`, `depends_on`, `blocked_by`, `conflicts_with`, `supersedes`, `derived_from`, `invalidated_by`, `serves_persona`, `part_of_journey`, `funded_by`, `routed_by`, `served`.

Provenance: every `Requirement`, `AcceptanceCriterion`, and `Capability` node must carry `confidence` (0.0–1.0) and `extraction_method` (`structured_source` | `rule_based` | `llm_inferred` | `human_confirmed`).

## When to use

1. A new intake, ADR, PRD/FRD/BRD, or operational spec is added.
2. A new code capability, test, or epic is merged.
3. A nightly full-corpus refresh is scheduled.
4. A human explicitly says: "refresh the knowledge graph" or "update the graph for <scope>".

## Procedure

### Step 1 — Check budget (do not skip)
1. Read `.ai/budgets/knowledge-graph-rebuild-001.yaml`.
2. If `consumed_usd >= max_usd` or `state != active`, stop and ask the user for a budget increase.
3. Estimate the cost of the requested scope using `per_call_usd * expected_calls`. If the estimate exceeds `remaining_usd`, stop and ask.

### Step 2 — Determine scope

| Trigger | Scope |
|---|---|
| New/updated intake | Intake + linked ADRs + affected `Capability` nodes |
| New ADR | ADR + superseded decisions + downstream requirements |
| New code module | Module + touched `Capability`/`Test`/`Evidence` nodes |
| Nightly or `full` command | Entire `docs/`, `.ai/intake/`, `backend/`, `frontend/` |

### Step 3 — Extract source artifacts
Read the following canonical sources in scope order:

1. `README.md`, `ARCHITECTURE.md`, `CONTRACT.md` (if present).
2. `docs/decisions/*.md` (ADR).
3. `docs/ops/*.md`, `docs/design/*.md`.
4. `.ai/intake/*.md`.
5. Code: `backend/app/main.py`, `backend/api/routes/*.py`, `frontend/src/components/*.tsx`.
6. Tests: `backend/tests/test_*.py`, `frontend/src/api/__tests__/*.ts`, `frontend/e2e/*.ts`.

For each, create a `SourceArtifact` node:
```json
{
  "kind": "SourceArtifact",
  "id": "SRC-<basename>",
  "name": "<file name>",
  "path": "<relative repo path>",
  "authority": "primary | decision | secondary | assessment"
}
```

### Step 4 — Extract requirements, capabilities, and tests
For each structured requirement or acceptance criterion found:

1. If the source already has an ID (e.g., `REQ-013`), use it.
2. If not, derive a stable key from source + entity type + a canonical phrase: `REQ-<adr-suffix>-<kebab-title>`.
3. Set `extraction_method` and `confidence`:
   - Explicit, enumerated, and human-written → `structured_source`, confidence `0.95`.
   - Inferred from headings and body → `rule_based`, confidence `0.75`.
   - Inferred by the assistant from context → `llm_inferred`, confidence `0.60`.
   - User explicitly confirms during chat → `human_confirmed`, confidence `0.95`.

### Step 5 — Link personas and journeys
For every geragogy or user-flow requirement, create or reuse `Persona` and `Journey` nodes and add `serves_persona` / `part_of_journey` edges.

### Step 6 — Update graph file
- Read `.ai/nelson/requirements-knowledge-graph.json` if it exists; otherwise start from the existing `.ai/process/KNOWLEDGE_GRAPH.json` as a seed.
- Use **upsert** semantics: stable IDs; never append-only duplicates.
- Keep deterministic ordering (sorted by `id`).
- Compute and store a deterministic graph hash in `.ai/nelson/graph-hash.txt`.

### Step 7 — Incremental logging
Append a `CostEvent` to `.ai/budgets/knowledge-graph-rebuild-001.yaml`:
```yaml
cost_events:
  - event_id: <uuid>
    date: <iso-8601>
    scope: <path or command>
    estimated_usd: <float>
    actual_usd: <float>
    model: <model name>
    tool_calls: <int>
```

### Step 8 — Validation handoff
Run `knowledge-graph-validation` skill (or ask user to run it) before treating the graph as authoritative.

## Output artifacts

- `.ai/nelson/requirements-knowledge-graph.json`
- `.ai/nelson/requirements-traceability-report.md`
- `.ai/nelson/graph-hash.txt`
- Updated `.ai/budgets/knowledge-graph-rebuild-001.yaml`

## Safety rules

- Do not overwrite the legacy `.ai/process/KNOWLEDGE_GRAPH.*` files. Deprecate them with a notice instead.
- Do not delete a node unless the source is explicitly removed and a human confirms.
- Do not run in shadow/advisory mode until `knowledge-graph-validation` has reported no critical orphans or conflicts.
- If a source artifact is missing or the repo state has drifted, log a `Gap` node and continue.
