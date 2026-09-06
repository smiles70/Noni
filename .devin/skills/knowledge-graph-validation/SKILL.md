---
name: knowledge-graph-validation
description: Validate the v9.51 requirements knowledge graph for orphans, conflicts, drift, and traceability gaps
---

# Knowledge Graph Validation (v9.51)

## Purpose
Run the graph QA, security, and traceability checks required by `PROCESS_V9.51_SPEC.md` §19.4 and §19.7a. Starts in **shadow mode**: it reports findings, does not block work.

## Inputs

- `.ai/nelson/requirements-knowledge-graph.json`
- `.ai/nelson/requirements-graph-schema.json`
- `.ai/nelson/graph-hash.txt` (optional, for drift detection)
- Existing code and tests for cross-checking

## When to use

1. After `knowledge-graph-extraction` finishes.
2. Before a release or certification.
3. Nightly, alongside a full-corpus refresh.
4. On demand: a human says "validate the knowledge graph".

## Procedure

### Step 1 — Schema validation
1. Load `requirements-graph-schema.json`.
2. Validate every node has a `kind`, `id`, `name`, and required provenance fields if it is a `Requirement`, `AcceptanceCriterion`, or `Capability`.
3. Validate every edge has `from`, `relation`, `to` from the allowed relationship list.
4. Log validation errors to `.ai/nelson/requirements-conflicts.json`.

### Step 2 — Orphan detection
For each node, confirm at least one of the following is true:

- `SourceArtifact` is referenced by at least one `Requirement` or `Decision`.
- `Requirement` has at least one `Capability` that `implements` it or is linked to an `Epic`/`UserStory`.
- `Capability` is `implemented_by` a code module or `verified_by` a `Test`.
- `Test` is `evidenced_by` an actual test file or CI run.
- `Owner` `owns` at least one `Capability` or `Decision`.
- `Gap` has an `Owner` and a `next_action`.

Log orphans to `.ai/nelson/requirements-orphans.json`.

### Step 3 — Conflict detection
Detect and log conflicts:

- Two `Requirement` nodes with the same `id` but different `name` or `path`.
- A `Requirement` that `conflicts_with` another without a resolution.
- A `Decision` that `supersedes` another but the old `Decision` is still marked active.
- A `Capability` `blocked_by` a `Gap` that has no owner.
- `Persona`/`Journey` referenced but not defined.

Log to `.ai/nelson/requirements-conflicts.json`.

### Step 4 — Traceability gate (advisory, not blocking)
For every material `Requirement`:

- Is it linked to an authoritative `SourceArtifact`?
- Does it have an `Owner`?
- Is there at least one `Capability` or `Decision` linked?
- Is there at least one `Test` or `Evidence`?

If the answer to any is "no", create a `Gap` node and a report entry. Do not block certification unless promoted by a human.

### Step 5 — Drift detection
1. Read the previous graph hash from `.ai/nelson/graph-hash.txt` if it exists.
2. Hash the current graph using the same deterministic method.
3. If the hash changed, write a diff summary to `.ai/nelson/requirements-drift-report.json`.

### Step 6 — Security validation
1. Confirm no secret values, API keys, or tokens are stored in graph nodes (only stable IDs, paths, and descriptions).
2. Confirm `SourceArtifact` paths are relative and do not expose absolute filesystem paths (e.g., no `/home/hazbyn/...`).

## Reports

- `.ai/nelson/requirements-conflicts.json`
- `.ai/nelson/requirements-orphans.json`
- `.ai/nelson/requirements-drift-report.json`
- `.ai/nelson/requirements-traceability-report.md`

## Gate mode

This skill operates in **shadow mode** by default. It does not cap scores or block work until a human explicitly promotes it to **advisory** or **blocking**.
