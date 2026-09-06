# Intake — v9.51 Ontology / Knowledge Graph Rebuild + Chat-to-Work-Item Assignment

**Date:** 2026-08-29  
**Requester:** Process / Engineering  
**Process:** v9.51  
**Scope:** Design (do not activate yet) a rebuilt requirements knowledge graph that complies with `PROCESS_V9.51_SPEC.md` §19, corrects the stale graph in this repo, and adds a chat-initiated work-item assignment capability so a person can be assigned a GitHub work item directly from this conversation.  

---

## Motivation

The existing `.ai/process/KNOWLEDGE_GRAPH.md` and `.ai/process/KNOWLEDGE_GRAPH.json` were produced on 2026-08-27 against an old repo path (`/home/hazbyn/Mynaani`). They predate the v9.51 §19 corrections and do not include the newly required entities (`Persona`, `Journey`, `BudgetProfile`, `CostEvent`, `RoutingDecision`) or relationships (`serves_persona`, `part_of_journey`, `funded_by`, `routed_by`, `served`). They also lack mandatory `confidence` / `extraction_method` provenance fields and the canonical `.ai/nelson/` artifact layout. Meanwhile, the team is doing more work through chat and needs a way to turn a chat message into an assigned GitHub issue, linked to a person and (optionally) the knowledge graph.

This intake only creates the design and path. **No skill, script, or graph build is activated yet.**

---

## Current state (what already exists)

| Artifact | Path | Problems relative to v9.51 |
|---|---|---|
| Knowledge graph (Markdown) | `.ai/process/KNOWLEDGE_GRAPH.md` | 140 nodes / 159 edges; no `Persona`, `Journey`, tokenomics entities; no `confidence`/`extraction_method`; references wrong repo path `smiles70/Mynaani` |
| Knowledge graph (JSON) | `.ai/process/KNOWLEDGE_GRAPH.json` | Same gaps; 151 nodes / 172 edges; lacks canonical `.ai/nelson/` location; entity list does not match §19.1 |
| Codebase context | `.ai/context/codebase-map.json` | Useful but not a requirements graph; not linked to `Requirement`/`Capability` nodes |
| Skills | `.devin/skills/` | Does not exist; v9.51 expects reusable skills under this path for ontology procedures |

---

## Target ontology (from PROCESS_V9.51_SPEC.md §19)

### Entities (canonical v9.51 set)

```text
SourceArtifact, Requirement, Capability, Epic, UserStory, AcceptanceCriterion,
Test, Evidence, Owner, Decision, Dependency, Gap, Conflict, Assumption,
Persona, Journey,
BudgetProfile, CostEvent, RoutingDecision
```

### Relationships (canonical v9.51 set)

```text
defined_by, refines, implements, partially_implements, verified_by, evidenced_by,
planned_by, owned_by, depends_on, blocked_by, conflicts_with, supersedes,
derived_from, invalidated_by,
serves_persona, part_of_journey,
funded_by, routed_by, served
```

### Mandatory provenance fields

Every `Requirement`, `AcceptanceCriterion`, and `Capability` node must carry:
- `confidence` (0.0–1.0)
- `extraction_method`: `structured_source` | `rule_based` | `llm_inferred` | `human_confirmed`

---

## Batched requirements

### Batch 1 — Stabilize the graph storage and naming

| # | Item | Evidence |
|---|---|---|
| 1 | Move canonical graph artifacts from `.ai/process/` to the v9.51 location `.ai/nelson/`. | New directory exists with schema, graph, conflicts, orphans, drift report, traceability report. |
| 2 | Correct the repo reference from `smiles70/Mynaani` to `smiles70/Noni` in all metadata. | Graph metadata matches `git remote -v`. |
| 3 | Create `requirements-graph-schema.json` that validates every node and edge against §19.1 and §19.2. | Schema file committed. |

### Batch 2 — Enrich the ontology

| # | Item | Evidence |
|---|---|---|
| 4 | Add `Persona` and `Journey` entity nodes derived from geragogy docs and ADRs. | At least one `Persona` node and one `Journey` node exist and are referenced by `serves_persona` / `part_of_journey` edges. |
| 5 | Add `BudgetProfile`, `CostEvent`, `RoutingDecision` tokenomics entities as placeholders (shadow mode). | Entities defined in schema; zero or more instances allowed. |
| 6 | Add `confidence` and `extraction_method` to every `Requirement`, `AcceptanceCriterion`, and `Capability` node. | A validation script can load the graph and confirm all required fields are present. |
| 7 | Add the new relationships: `serves_persona`, `part_of_journey`, `funded_by`, `routed_by`, `served`. | Schema allows these edges; at least one sample edge of each kind in the graph. |

### Batch 3 — Rebuild procedures and skills

| # | Item | Evidence |
|---|---|---|
| 8 | Create `.devin/skills/knowledge-graph-extraction/SKILL.md` describing how to extract entities from intakes, ADRs, and code. | Skill file present, not yet registered. |
| 9 | Create `.devin/skills/knowledge-graph-validation/SKILL.md` describing graph QA, conflict detection, orphan detection, and drift checks. | Skill file present, not yet registered. |
| 10 | Design the refresh pipeline: diff-scoped on new intake / ADR / PR, full-corpus on nightly. | Documented in the preflight or a `docs/process/knowledge-graph-refresh.md` file. |

### Batch 4 — Chat-to-work-item assignment capability

| # | Item | Evidence |
|---|---|---|
| 11 | Design the chat command surface. Example: `@assign <github-username> [title]` or a natural-language intent such as "assign the Stripe price decision to @hazbyn". | Documented interface in intake. |
| 12 | Choose the GitHub API path: `gh issue create` + `gh project item-add` + `gh issue edit --assignee`. | Confirmation that the repository has Issues and a Project board enabled. |
| 13 | Design the link back to the knowledge graph: the created issue should reference the relevant `Requirement`, `Gap`, or `Decision` node by ID in its body. | Example issue body template. |
| 14 | Determine identity mapping: how does a chat mention map to a GitHub handle? Options: exact match, a local `.ai/people.yaml` roster, or explicit `@github:username` syntax. | Decision recorded. |
| 15 | Create a `.devin/skills/work-item-assignment/SKILL.md` with the procedure and required env vars (`GITHUB_TOKEN` or `GH_TOKEN`). | Skill file present, not yet registered or activated. |

---

## Chat-to-work-item design (not activated)

### Proposed chat surface

The user in this chat can say something like:

```text
assign the Stripe price decision to @hazbyn
```

or

```text
create a work item: decide final gift pricing (modules_4_5) and assign to @hazbyn
```

### Proposed response from the assistant

1. Confirm the title, assignee, and linked knowledge-graph node (if any).
2. Call `gh issue create` with the body formatted as:

```markdown
---
**Created from chat:** 2026-08-29
**Knowledge-graph node:** DEC-0021-pricing
**Batch:** A
**Related intake:** .ai/intake/2026-08-29-stripe-live-readiness-intake.md
---

## Task
decide final gift pricing (modules_4_5)

## Context
ADR 0021 says $39 self / $59 gift, but `scripts/seed_products.py` and `docs/stripe-setup.md` say $49. Gift sales are also blocked by defect D1/D2. This decision is the Batch A pre-flight blocker P7.
```

3. Optionally add the issue to the GitHub project board via `gh project item-add`.
4. Return the issue number and URL to the chat.

### GitHub commands it would run

```bash
gh issue create \
  --repo smiles70/Noni \
  --title "Decide final gift pricing (modules_4_5)" \
  --body-file /tmp/issue-body.md \
  --assignee hazbyn \
  --label "pricing,batch-a"

gh project item-add 1 \
  --owner smiles70 \
  --url https://github.com/smiles70/Noni/issues/NNN
```

### Required setup (not done yet)

- Repository must have Issues enabled.
- Repository must have a GitHub Project (board) with a known project number.
- The chat environment must have `gh` installed and authenticated, or a GitHub MCP server configured.
- A mapping from chat names to GitHub handles must be available.

---

## Explicit non-goals

- Do not rebuild or overwrite the existing graph in this session.
- Do not install or register the new skills yet.
- Do not create, edit, or push any workflow file that performs the chat assignment.
- Do not create a GitHub issue or project item now.
- Do not turn on graph-driven blocking gates — they start in shadow mode per §19.6.

---

## Success criteria

1. A complete intake and preflight document exists for the knowledge-graph rebuild.
2. The target schema matches `PROCESS_V9.51_SPEC.md` §19.1–§19.3.
3. The chat-to-work-item flow is documented and can be reviewed before activation.
4. No canonical graph is overwritten until the preflight is approved and the rebuild skill is explicitly invoked.

---

## Open questions

1. Should the graph build be stored as JSON, SQLite, or a graph database (e.g. Neo4j, networkx pickle)?
2. Is there an existing GitHub Project board for `smiles70/Noni`, or does one need to be created?
3. Does the chat environment already have `gh` authenticated, or should we use a GitHub MCP server?
4. Which human is the default owner for process/ontology work (for `Owner` nodes)?
5. Should the chat assignment skill support direct assignment to a knowledge-graph `Owner` node, or only to GitHub usernames?
6. What is the budget (token / cost) guard for the graph rebuild agent per `PROCESS_V9.51_SPEC.md` Part C?

---

## Implementation path (rebuild only after approval)

1. Approve this intake and its companion preflight.
2. Create the `.devin/skills/` directory and the three skill files described in Batch 3 and Batch 4.
3. Run the `knowledge-graph-extraction` skill in shadow mode against the repo to produce a new `.ai/nelson/requirements-knowledge-graph.json`.
4. Run the `knowledge-graph-validation` skill against the new graph and review the conflict/orphan/drift reports.
5. If validation passes, replace the legacy `.ai/process/KNOWLEDGE_GRAPH.*` files with deprecation notices pointing to `.ai/nelson/`.
6. Register the `work-item-assignment` skill and test it with a non-real issue in a test repo or `workflow_dispatch` before using it here.
