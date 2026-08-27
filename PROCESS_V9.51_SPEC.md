# The Process v9.51 — Complete Operating Specification

## Full-Stack Agent Harness with MLDC Alignment, Nelson Repo Hygiene, Tokenomics Governance, and Cross-Cutting Reliability Programs

**Version:** v9.51
**Status:** Current-state complete specification — single authoritative document.

---

## 1. Executive Summary

The Process v9.51 is a governed AI-assisted software delivery operating model combining:

- full-stack delivery orchestration,
- MLDC-aligned front-end generation and validation,
- repository survivability scoring,
- token/cost governance for AI-assisted work,
- canonical artifact generation and a requirements knowledge graph,
- and a set of cross-cutting reliability programs that make every score, cap, and gate in this document consistent, calibrated, and accountable to its own accuracy.

**Core operating claim:** The Process v9.51 makes repositories self-describing, self-scoring, cost-accountable, and continuously refreshed — and makes its own scoring and gating mechanisms subject to the same evidence discipline they impose on everything else.

---

## 2. Process v9.51 Operating Model

Three integrated delivery layers:

1. **MLDC Alignment Layer** — UI development constrained to approved design-system components and patterns.
2. **Nelson Repo Hygiene and Canonical Knowledge Layer** — repository quality, current-state truth, and requirements traceability as measurable gates.
3. **Tokenomics Governance Layer** — AI token/cost spend as a measured, policy-bounded, evidence-backed gate.

Two cross-cutting programs apply to all three layers rather than being restated inside each one (Part D):

- **Score Composition, Calibration, and Grader Accuracy Program** — one rule for how caps compose, one process for validating that scores predict real outcomes, one mechanism for checking that scoring agents are themselves accurate.
- **Process Self-Governance** — the framework governs itself with the same artifacts, ownership discipline, and version hygiene it requires of every repository it touches.

---

# Part A — MLDC Alignment Layer

## 3. MLDC Alignment Layer

Turns MetLife Design Components from a reference library into an active development constraint for UI work. If MLDC has an approved pattern, generation uses it before creating custom UI. If no approved pattern exists, a documented exception or MLDC contribution candidate is created.

## 4. Required MLDC Agents

| Agent | Function |
|---|---|
| Component Discovery Agent | Scans UI for MLDC usage, custom components, wrappers, and replacement candidates. |
| Pattern Recommendation Agent | Maps UI requirements to approved MLDC components, Storybook examples, CTAs, inputs, feedback, navigation, icons, theming. |
| Code Generation Guardrail Agent | Constrains generated React code to MLDC imports and approved composition unless a documented exception exists. |
| Accessibility and Responsive Validation Agent | Validates accessibility and responsive behavior against MLDC/Storybook expectations. |
| Theme Compliance Agent | Detects hardcoded styling, incorrect Theme Provider usage, brand drift. |
| Design Consistency Agent | Compares implemented UI against MLDC style guide and best practices. |
| Contribution Readiness Agent | Identifies components that should become MLDC contribution candidates rather than local one-offs. |
| Package and Version Alignment Agent | Checks MLDC package versions, peer dependencies, React compatibility, Artifactory readiness. |
| CI/CD Readiness Agent | Checks MLDC-related changes are buildable, scannable, pipeline-safe, and release-ready. |
| Adoption Metrics Agent | Tracks component reuse, custom-component reduction, drift, exceptions over time. |
| PR Evidence Agent | Adds MLDC usage/exception/validation evidence into PR summaries. |
| Certification Agent | Writes MLDC alignment verdicts into certification, repo trust, PR gates, session close, and executive HTML reports. |

## 5. Required MLDC Skills

| Skill | Description |
|---|---|
| `mldc-component-discovery-skill` | Finds MLDC imports, custom components, wrappers, duplicate UI patterns, and candidate replacements. |
| `mldc-storybook-mapping-skill` | Maps requirements to Storybook components, usage examples, props, and code snippets. |
| `mldc-pattern-recommendation-skill` | Recommends MLDC CTA, user input, feedback, navigation, theming, icons, and UX utility patterns. |
| `mldc-code-generation-guardrail-skill` | Prevents unnecessary custom UI generation and steers implementation to approved MLDC patterns. |
| `mldc-accessibility-validation-skill` | Validates accessibility expectations aligned to MLDC and Storybook guidance. |
| `mldc-responsive-validation-skill` | Checks responsive behavior across target screen sizes. |
| `mldc-theme-compliance-skill` | Detects hardcoded styles, theme bypasses, incorrect Theme Provider usage, and style drift. |
| `mldc-design-consistency-skill` | Scores consistency with MLDC style guide, React standards, usage guide, and best practices. |
| `mldc-contribution-readiness-skill` | Creates component contribution candidates when MLDC has a gap. |
| `mldc-version-package-alignment-skill` | Checks MLDC package versions, peer dependencies, React compatibility, and Artifactory consumption. |
| `mldc-cicd-readiness-skill` | Validates build, scan, package, and pipeline readiness for MLDC-related changes. |
| `mldc-adoption-scorecard-skill` | Calculates MLDC adoption, reuse, custom component reduction, exception rates, and design-system drift. |

## 6. Required MLDC Reports

| Report | Description |
|---|---|
| MLDC Alignment Report | Summary of MLDC adoption, custom component debt, replacement opportunities, and alignment verdict. |
| Component Usage Map | Inventory of approved MLDC components, wrappers, custom components, and replacement candidates. |
| Pattern Plan | Recommended MLDC implementation plan for each UI requirement or page. |
| Accessibility and Responsive Report | Accessibility and responsive validation evidence for changed or generated UI. |
| Theme Compliance Report | Theme Provider usage, hardcoded style findings, theme drift, and remediation recommendations. |
| Contribution Candidate Report | Reusable component candidates that should be contributed to MLDC instead of remaining local. |
| Package Alignment Report | React compatibility, package version, peer dependency, and Artifactory consumption readiness. |
| Adoption Dashboard | Reusable HTML report showing reuse score, drift, exceptions, and adoption trend. |
| PR Evidence Report | PR-ready evidence block showing MLDC use, exceptions, validation, and release readiness. |

## 7. MLDC Alignment Score

| Domain | Weight | Evidence Focus |
|---|---:|---|
| Component Reuse | 20 | Approved MLDC components used where applicable. |
| Custom Component Reduction | 15 | Custom UI replaced or justified. |
| Pattern Alignment | 15 | CTA, input, feedback, navigation, theming, icon patterns match MLDC guidance. |
| Accessibility Readiness | 15 | Accessibility evidence exists for changed UI. |
| Responsive Readiness | 10 | Responsive behavior validated across target screen sizes. |
| Theme Compliance | 10 | Theme Provider/token usage correct; hardcoded styles minimized. |
| Package Alignment | 10 | Version, peer dependencies, React compatibility, package consumption clean. |
| Contribution Hygiene | 5 | Missing reusable components proposed for MLDC contribution. |

Score composition and cap application for this table follow the single unified rule in §27.1 — not a locally-restated rule.

### 7.1 MLDC Gate Meaning

| Score | Status | Gate Meaning |
|---|---|---|
| 90-100 | MLDC aligned | Proceed with strong design-system confidence. |
| 80-89 | Controlled | Proceed with documented exceptions or minor remediation. |
| 70-79 | Review required | Reuse, theming, accessibility, or responsive gaps require review. |
| <70 | Block major UI change | Must be corrected before merge or release. |

### 7.2 MLDC Development Impact (restored)

v9.51 changes what gets created:

- Creates MLDC component plans before UI code.
- Creates UI with approved components before custom components.
- Creates theme-compliant code instead of hardcoded styling.
- Creates accessibility and responsive validation evidence.
- Creates PR evidence showing MLDC usage and exceptions.
- Creates contribution candidates when MLDC has a reusable gap.
- Creates adoption reporting showing reuse, drift, and custom UI debt.

---

# Part B — Nelson Repo Hygiene and Canonical Knowledge Layer

## 8. Nelson Repo Hygiene and Canonical Knowledge Layer

Turns repository quality from a subjective documentation concern into a measurable delivery quality gate. Nelson scores and persists repository knowledge produced by existing Process flows; it does not replace discovery, design, build, test, audit, or certification.

## 9. Why Nelson Exists (restored)

v9.4 embedded MLDC alignment into UI delivery. v9.5 extends the same evidence-first approach to repository hygiene.

Most enterprise repositories fail in one of four ways:

- Orientation exists but is incomplete.
- Architecture exists but is stale.
- Operational knowledge exists outside the repo.
- Current state lives in chat, meetings, or individual memory.

Nelson addresses those gaps through scorecards, gates, report generation, and canonical artifact updates.

## 10. Nelson Persona

> A repository is not a code container. It is the operating memory of the application.

Nelson asks: Can a new engineer understand the repo in 15 minutes? Can it be run, tested, deployed, and supported without tribal knowledge? Are architecture and decisions current, owned, and discoverable? Does the repo show what exists, what is incomplete, what is blocked, what comes next? Does Process-generated knowledge persist back into the repo?

## 11. Required Nelson Agents

| Agent | Function |
|---|---|
| Nelson Research Agent | Maintains external best-practice baseline; distinguishes source-backed standards from local preference. |
| Repo Artifact Fingerprint Agent | Scans for required hygiene artifacts; verifies presence, location, freshness, ownership, completeness. |
| Bootstrap Knowledge Analyzer | Compares discovered repo reality against existing docs; identifies drift, gaps, stale decisions, missing runbooks, and undocumented dependencies. |
| Canonical Artifact Generator | Creates/updates canonical repo artifacts from Process findings. |
| Nelson Scorecard Agent | Computes the Nelson score per the unified composition rule (§27.1); writes output into repo trust, PR, session close, certification. |
| Pixel / Layout QA Agent | Reviews generated HTML/PDF reports for clipping, overlap, density, layout defects before delivery. |
| Grader Sampling Agent *(new)* | Feeds a rolling sample of Nelson's own scoring decisions into the Grader Accuracy Program (§27.3) for human-reviewed agreement checking. |

## 12. Required Nelson Skills

| Skill | Description |
|---|---|
| `repo-hygiene-rubric-skill` | Applies the Nelson scoring rubric consistently across repos. |
| `artifact-detection-skill` | Detects required artifacts, missing artifacts, stale artifacts, and non-canonical duplicates. |
| `current-state-synthesis-skill` | Converts Process scan findings into `docs/CURRENT_STATE.md`. |
| `architecture-doc-generator-skill` | Generates or updates `ARCHITECTURE.md` from discovered repo evidence. |
| `runbook-generation-skill` | Generates or updates `RUNBOOK.md`, including failure modes, rollback, support, and recovery guidance. |
| `repo-report-html-skill` | Creates executive and developer-friendly Nelson reports in HTML. |
| `canonical-artifact-sync-skill` | Writes generated artifacts back into the repo structure and records provenance. |
| `repo-drift-detection-skill` | Compares generated truth against existing documentation and flags drift. |
| `onboarding-pack-generation-skill` | Creates or updates onboarding, local setup, first task, and common failure-mode guidance. |
| `repo-scorecard-rollup-skill` | Aggregates Nelson scores across repos, teams, portfolios, and initiatives. |

## 13. Required Nelson Reports

```text
/.ai/nelson/nelson-scorecard.json
/.ai/nelson/nelson-scorecard.html
/.ai/nelson/artifact-inventory.json
docs/CURRENT_STATE.md
docs/ARCHITECTURE.md
docs/adr/ADR-candidates.md
docs/RUNBOOK.md
docs/ROLLBACK.md
docs/ONBOARDING.md
/.ai/nelson/repo-hygiene-dashboard.html
/.ai/nelson/pr-evidence.md
```

## 14. Nelson Score Model

Total: 100 points.

| Domain | Weight | Evidence Focus |
|---|---:|---|
| Repository Orientation | 10 | README, purpose, quick start, build/test/deploy summary. |
| Architecture | 15 | System context, dependencies, boundaries, data flow. |
| Decision Records | 10 | ADRs, tradeoffs, consequences, decision ownership. |
| Operational Readiness | 15 | Runbooks, rollback, recovery, monitoring, support. |
| Knowledge Transfer | 15 | Onboarding, environment setup, local run, developer guide. |
| Ownership | 10 | CODEOWNERS, SME path, escalation, support contacts. |
| Delivery Governance | 10 | CONTRIBUTING, PR policy, DOD, DOR, branch rules. |
| Security and Compliance | 5 | SECURITY.md, secrets, vulnerability process, threat model — **additive weight is deliberately low because this domain is cap-governed, not weight-governed; see §14.3.** |
| Testability | 10 | Test strategy, coverage expectations, test data, validation approach. |

### 14.1 Current-State Visibility
Not a separate point bucket. Applies score caps across other domains when the repo cannot accurately explain its current condition, per the unified composition rule (§27.1).

### 14.2 Original Nelson cap rules (restored — these are unchanged from v9.5)

- Missing README caps score at 90.
- Missing architecture documentation caps score at 85.
- Missing runbook or rollback for production systems caps score at 80.
- Missing ownership or escalation path caps score at 80.
- Missing current-state artifact caps score at 85.
- Documentation that conflicts with discovered repo evidence caps the relevant domain at 60.
- No evidence means no full score.

### 14.3 Security cap rule (new in v9.51 — closes the "security is underweighted" gap)

Security's low additive weight (§14) is intentional, not an oversight — severe security failures are tail-risk events that a linear weight cannot represent correctly (a 5-point deduction understates a hardcoded production secret). In addition to the cap rules above, any of the following caps the **overall** Nelson score at 50, independent of the domain weighting table:

- A confirmed hardcoded secret or credential in the repository.
- A known critical/high CVE in a direct dependency with no documented remediation plan.
- No threat model or SECURITY.md for a production system handling sensitive data.

### 14.4 Nelson Score Bands and Gates

| Score | Status | Process Gate Action |
|---|---|---|
| 95-100 | Industry Leading | Proceed. |
| 85-94 | Enterprise Mature | Proceed with minor artifact cleanup. |
| 70-84 | Managed Risk | Proceed only if critical gaps are acknowledged and tracked. |
| <70 | Operational Risk | Block major work until corrected. |

## 15. Canonical Repo Structure

```text
<repo>/
  README.md
  CONTRIBUTING.md
  SECURITY.md
  CODEOWNERS
  CHANGELOG.md
  docs/
    ARCHITECTURE.md
    CURRENT_STATE.md
    ONBOARDING.md
    RUNBOOK.md
    ROLLBACK.md
    TEST_STRATEGY.md
    adr/
  .ai/
    nelson/
      artifact-inventory.json
      nelson-scorecard.json
      nelson-scorecard.html
      repo-hygiene-dashboard.html
      pr-evidence.md
      grader-accuracy-log.json
    tokenomics/
      cost-baseline-gap-report.md
      budget-profiles.json
      cost-ledger.json
      tokenomics-scorecard.json
      tokenomics-scorecard.html
      tokenomics-pr-evidence.md
    process/
      PROCESS_CURRENT_STATE.md
      PROCESS_ROLLBACK.md
      PROCESS_CHANGELOG.md
    intake/
    repo-landscape/
    production-readiness/
```

## 16. Nelson Bootstrap Flow (restored)

```text
Process initializes repo
  -> Repo Artifact Fingerprint Agent scans artifacts
  -> Bootstrap Knowledge Analyzer compares repo docs to discovered reality
  -> Nelson Scorecard Agent applies 100-point rubric and score caps (§14, unified composition rule §27.1)
  -> Canonical Artifact Generator writes missing or refreshed artifacts
  -> Pixel / Layout QA Agent verifies generated HTML/PDF outputs
  -> Certification and PR gates consume Nelson score
```

## 17. Process Integration Points (restored — includes the only references to Rick, OSS+, and FSAS)

### 17.1 Universal Intake
Nelson consumes intake outputs to identify missing requirements, undocumented assumptions, and artifact gaps.

### 17.2 Repo Landscape
Nelson consumes repo map, package map, path inventory, CI/CD inventory, and dependency evidence.

### 17.3 Production Readiness Assessment
Nelson consumes PRA findings and maps them into operational readiness, runbook, rollback, and support artifacts.

### 17.4 Rick
Rick continues to score delivery readiness. Nelson scores repo survivability. Both write evidence-backed outputs and use cap rules.

### 17.5 OSS+
OSS+ findings feed Nelson security, dependency, and supply-chain documentation requirements.

### 17.6 FSAS
FSAS findings feed Nelson architecture and dependency documentation requirements.

### 17.7 MLDC
MLDC findings feed Nelson UI pattern documentation, design-system alignment, and front-end contribution hygiene.

### 17.8 Tokenomics
Tokenomics findings (Part C) feed Nelson's requirements graph directly via `BudgetProfile`, `CostEvent`, and `RoutingDecision` nodes (§19.1) — not a separate integration path, since these are first-class graph entities rather than external findings being mapped in.

## 18. v9.51 Slash Commands

```text
/nelson-score          Computes Nelson Repo Score.
/nelson-artifacts       Lists required, missing, stale, duplicate artifacts.
/nelson-current-state   Generates/refreshes docs/CURRENT_STATE.md.
/nelson-docs-sync       Creates/updates canonical artifacts from Process findings.
/nelson-report          Generates HTML report pack.
/nelson-gate            Returns proceed / proceed-with-warning / managed-risk / block.
/nelson-rollup          Aggregates scores across a repo set or portfolio.
/tokenomics-score       Computes Tokenomics Score (Part C).
/tokenomics-gate        Returns tokenomics gate verdict.
/grader-audit           Runs a Grader Accuracy Program sampling pass (§27.3).
/process-self-check     Runs Nelson's own rubric against this Process specification (§14).
```

---

## 19. Requirements Ontology and Knowledge-Graph Layer

Cross-cutting; consumes evidence from discovery, design, build, test, audit, certification, and tokenomics agents and connects it to canonical requirements. Does not replace those agents.

### 19.1 Canonical ontology

```text
SourceArtifact, Requirement, Capability, Epic, UserStory, AcceptanceCriterion,
Test, Evidence, Owner, Decision, Dependency, Gap, Conflict, Assumption,
Persona, Journey,                      ← added: closes the §20 decomposition-chain gap
BudgetProfile, CostEvent, RoutingDecision   ← added: Tokenomics entities (Part C)
```

Every `Requirement`, `AcceptanceCriterion`, and `Capability` node carries mandatory `confidence` (0.0–1.0) and `extraction_method` (`structured_source` | `rule_based` | `llm_inferred` | `human_confirmed`) fields — **closes the no-provenance gap.** A node with `extraction_method: llm_inferred` and `confidence` below a defined threshold cannot, on its own, satisfy a blocking gate (§19.6); it must be corroborated by a second extraction pass or human confirmation first.

### 19.2 Required relationships

```text
defined_by, refines, implements, partially_implements, verified_by, evidenced_by,
planned_by, owned_by, depends_on, blocked_by, conflicts_with, supersedes,
derived_from, invalidated_by,
serves_persona, part_of_journey,        ← added
funded_by, routed_by, served            ← added: Tokenomics (Part C, §26)
```

### 19.3 Canonical graph artifacts

```text
.ai/nelson/requirements-knowledge-graph.json
.ai/nelson/requirements-graph-schema.json
.ai/nelson/requirements-conflicts.json
.ai/nelson/requirements-orphans.json
.ai/nelson/requirements-drift-report.json
.ai/nelson/requirements-traceability-report.md
```

### 19.4 Requirements Knowledge Steward

Orchestrated, non-duplicating capabilities: requirements discovery, ontology modeling, entity extraction, graph construction, traceability auditing, conflict detection, orphan detection, change-impact analysis, evidence verification, drift detection, canonical synchronization, graph QA and security validation.

Reusable repository skills under `.devin/skills/` provide the operating procedures for ontology extraction, graph construction, conflict/orphan/drift detection, impact analysis, evidence gates, synchronization, and closeout. (Restored — this implementation-location reference was dropped from the prior revision.)

### 19.5 Identity assignment (closes the identity-resolution tension)

Stable node identity is assigned in this priority order:

1. **Structured source ID**, where the originating BRD/PRD/spec assigns one at authoring time. This is the preferred and only high-confidence path, and authoring standards should require it for material requirements going forward.
2. **Canonical key derived from source, entity type, and a stable extracted field** (per §20.4's original rule), used only where no structured ID exists — nodes assigned identity this way carry `extraction_method: rule_based` or lower and are treated as lower-confidence per §19.1.
3. Fuzzy similarity and embeddings may **flag** a probable match for human review. They never assign identity, merge nodes, delete a requirement, or mark work complete — unchanged from the original rule, now explicitly reconciled with the fact that most real source documents lack native IDs.

### 19.6 Graph-driven scoring and caps, staged by maturity (closes the overconfidence gap)

Not every graph-driven check is blocking from day one. Checks are staged:

- **Shadow mode (default for any new check):** the check runs, logs its result, and is visible in reporting — it does not cap or block anything. Required minimum period before promotion: a defined number of scoring cycles with precision/recall measured against a human-labeled sample (fed through the Grader Accuracy Program, §27.3).
- **Advisory:** the check appears in review-required gate output and must be acknowledged, but does not block.
- **Blocking:** the check can cap a score or block certification.

At initial v9.51 adoption: **conflict detection and orphan detection start in shadow mode.** Unsupported-completion-claim detection (structured, higher-confidence) may start in advisory mode. None of these start blocking on day one — promotion happens only after the measured precision/recall from the Grader Accuracy Program clears a defined bar.

Once a check is promoted past shadow mode, it applies the following specific mappings (restored from v9.5):

- Missing critical traceability caps Testability and Delivery Governance.
- Unresolved material conflict caps Architecture and Delivery Governance.
- Orphan critical requirement caps Ownership and Testability.
- Unsupported completion claim blocks certification.
- Graph drift requires remediation before release.

### 19.7a Permanent Graph Gates (restored)

For requirements-heavy work, session closeout must verify:

- Every material requirement has an authoritative source.
- Every implementable requirement maps to an epic or explicit deferment.
- Every claimed capability maps to code or an explicit research artifact.
- Every completed capability maps to a test or evidence record.
- Every critical gap has an owner and next action.
- Every material conflict is resolved, accepted, or escalated.
- The graph matches current repository evidence.
- Current-state and PR evidence artifacts are synchronized.

Per the staging rule above, these gates apply in full once the relevant underlying check has been promoted past shadow mode; while a check remains in shadow mode, its corresponding closeout verification is logged as advisory rather than blocking.

### 19.8 Refresh triggers and incremental scope (closes the scale gap)

- **Incremental, diff-scoped refresh** on: new intake, BRD/FRD/PRD changes, technical or operational specification changes, pull-request creation and merge, new/changed epic, new acceptance criterion, code capability change, test change, ADR change. Only the changed subgraph and its direct dependents are recomputed. (This restores three trigger types — new intake, BRD/FRD/PRD changes, technical/operational spec changes — that were dropped from this list in the prior revision.)
- **Full-corpus refresh** on a separate, slower cadence (nightly or release-gated release-or-scheduled-scan), not on every PR.
- This distinction did not exist in the prior specification, which implied full recomputation on every trigger — a real cost and latency risk at scale that is now explicitly bounded.

---

## 20. Deep Requirements Decomposition Gate

Every material requirement decomposes beyond a feature label:

```text
Source requirement → persona need → journey entry/exit → user-observable behavior
  → domain capability → API/data contract → code module → automated test
  → runtime/evidence record → owner → failure state → recovery state → operational gate
```

This chain now resolves against real graph nodes (`Persona`, `Journey`, §19.1) rather than referencing entity types the ontology didn't define.

### 20.1 Required decomposition questions
What does the user see? What does the user understand? What can the user do next? What happens if the system is wrong? What happens if the user stops? What happens if the network fails? What happens if content is incomplete? What evidence proves the behavior?

### 20.2 Anti-miss rule
Sample fixtures, static screens, contracts, and passing build checks cannot satisfy a complete user-outcome requirement unless the real-data path is also mapped and evidenced.

### 20.3 Geragogy decomposition
For a geragogy-based requirement: orientation, key-information extraction, deadline extraction, action extraction and prioritization, plain-language transformation, progressive disclosure, reassurance and non-shaming feedback, help escalation, original-source verification. Missing decomposition applies the graph evidence cap (§19.6, once promoted past shadow mode) and prevents a `COMPLETE` verdict.

### 20.4 Idempotent decomposition requirements

Repeated decomposition of identical sources with identical versions produces the same nodes, edges, statuses, and graph hash. Required controls: stable IDs from canonical source/entity type/canonical key (§19.5); upsert semantics, never append-only; stable edge keys (`from::relation::to`); deterministic node/edge ordering; source/parser/ontology/decomposition version hashes; explicit source-removal state before deletion; graph integrity validation before closeout; deterministic decomposition diff before accepting changes. Fuzzy similarity and embeddings may prioritize review but never independently assign identity, delete requirements, or mark work complete.

---

# Part C — Tokenomics Governance Layer

## 21. Tokenomics Governance Layer

AI token/cost spend as a measured, policy-bounded, evidence-backed gate — the same operating pattern as MLDC and Nelson, not a separate paradigm.

### 21.1 Operating Principle

Cost-governance decisions are pre-authorized by human-defined policy and executed autonomously within those bounds at runtime. A human sets the budget, routing policy, and escalation thresholds; agents execute without per-call approval, but no agent may silently exceed, redefine, or bypass a human-set boundary. A decision that would exceed policy bounds halts to a defined escalation state rather than acting outside its mandate. Autonomy inside a bound, never autonomy over the bound.

### 21.2 Bootstrap and Backfill Flow (retrofitting onto an existing repo)

```text
Process initializes tokenomics on an existing repo
  → Cost Surface Fingerprint Agent scans for LLM/agent call sites, prompt templates,
    and any existing usage-logging or billing-export artifacts already in the repo
  → External Usage Import (optional) ingests provider billing exports or usage logs,
    if such data exists and is made available — this is an explicit import step,
    not automatic discovery
  → Bootstrap Knowledge Analyzer (tokenomics variant) reconciles what is importable
    against what is unrecoverable
  → Cost Baseline Gap Report is generated, stating explicitly what historical spend
    IS known (from imported data) and IS NOT known (everything before instrumentation
    or import)
  → BudgetProfile and ledger initialize forward from the bootstrap date
  → Tokenomics Scorecard Agent computes scores from the bootstrap date forward only
```

**Hard rule, stated explicitly because it's easy to get wrong:** a repository scan can identify *where* token-consuming code exists — call sites, prompt templates, agent invocation points — producing a cost-generating-surface inventory. It cannot determine *how much was actually spent historically* unless that data was already logged somewhere and is explicitly imported. Static analysis of code does not reveal runtime token counts; those live in the LLM provider's billing/usage system or in application logs, not in the repository itself. The Cost Baseline Gap Report must state unknown historical spend as unknown — never as an estimate presented with the confidence of a measurement. This is the same "no evidence means no full score" discipline Nelson already applies (§14), extended to cost data rather than treated as an exception to it.

A repo with no prior usage logging and no importable billing export bootstraps with a **complete historical gap**, explicitly labeled as such, and a clean ledger starting from the bootstrap date. That is the honest and correct outcome for that repo — not a reason to estimate a number to fill the gap.

## 22. Required Tokenomics Agents

| Agent | Function |
|---|---|
| Cost Surface Fingerprint Agent | Scans existing code for LLM/agent call sites, prompt templates, and any existing usage-logging or billing-export artifacts; produces the Cost Baseline Gap Report (§21.2) distinguishing known from unrecoverable historical spend. |
| Guardrail Agent | Pre-flight token estimation and context optimization, excluding protected content (§25.2). |
| Router Agent | Selects a model from a maintained, versioned registry (§25.4) using a defined complexity score (§19, complexity fields) and budget-runway state. |
| FinOps Auditor Agent | Post-flight cost measurement, idempotent ledger deduction (§25.1), threshold monitoring, safe-stop circuit-breaking (§25.3). |
| Routing Quality Validator Agent | Samples Router decisions on a rolling basis; compares selected-model output against a higher-tier model or human judgment; tracks routing-quality agreement rate; feeds the Grader Accuracy Program (§27.3). |

## 23. Required Tokenomics Skills

| Skill | Description |
|---|---|
| `token-preflight-estimation-skill` | Estimates token cost of a payload before submission. |
| `protected-content-aware-compression-skill` | Performs semantic truncation and recursive summarization, with a hard exclusion list pulled from the Requirements Knowledge-Graph's `Requirement`, `AcceptanceCriterion`, `Evidence`, and `Decision` node types — these may never be silently compressed. |
| `model-registry-maintenance-skill` | Maintains the versioned model registry: tracks available models, deprecation dates, and capability/cost tiers, and flags routing-table entries referencing a deprecated or unavailable model version. |
| `complexity-scoring-skill` | Computes the task-complexity input to routing from defined, evidenced signals rather than an unexplained label. |
| `ledger-idempotency-skill` | Applies idempotency keys to every budget-deduction operation. |
| `circuit-breaker-safe-stop-skill` | Implements the safe-stop protocol in place of an unconditional process kill. |
| `routing-quality-sampling-skill` | Supports the Routing Quality Validator Agent's sampling and comparison workflow. |
| `tokenomics-scorecard-skill` | Computes the Tokenomics Score and applies its caps. |

## 24. Tokenomics Score

| Domain | Weight | Evidence Focus |
|---|---:|---|
| Budget Adherence | 20 | Spend tracked against policy budgets at project/epic/sprint/user-story level; no unauthorized overage. |
| Routing Quality | 20 | Sampling shows routing maintains acceptable output quality, not just lower cost. |
| Protected-Content Integrity | 20 | Zero instances of protected content altered or dropped by compression. |
| Ledger Integrity | 15 | Deduction operations idempotent and reconciled; no double-deduction or drift vs. actual provider billing. |
| Model Registry Currency | 10 | No routing-table entry references a deprecated or unavailable model version. |
| Circuit-Breaker Safety | 10 | Circuit-break events follow the safe-stop protocol; no mid-operation data loss from an unconditional kill. |
| Escalation Hygiene | 5 | Policy-boundary escalations logged, owned, resolved — never silently overridden or ignored. |

Composition and cap application follow §27's unified rule below.

### 24.1 Tokenomics-specific caps
- Any Protected-Content Integrity violation caps the overall score at 60 — same severe-tail-risk treatment as Nelson's security cap (§14.3).
- A confirmed double-deduction caps Ledger Integrity at 0 for that period.
- A circuit-break that skipped the safe-stop protocol caps Circuit-Breaker Safety at 0 for that event.

### 24.2 Tokenomics Gate Meaning

| Score | Status | Gate Meaning |
|---|---|---|
| 90-100 | Tokenomics aligned | Proceed with strong cost-governance confidence. |
| 80-89 | Controlled | Proceed with documented exceptions or minor remediation. |
| 70-79 | Review required | Gaps require review before continued autonomous operation. |
| <70 | Block autonomous execution | Fall back to human-approved routing/budget decisions until corrected. |

## 25. Safety and Integrity Requirements

### 25.1 Ledger idempotency
Every budget-deduction operation carries a deterministic idempotency key derived from the request, so a retried or duplicated call reconciles to the same ledger state rather than double-deducting.

### 25.2 Protected-content exclusion from compression
The Guardrail Agent's compression operations may never operate on content sourced from a `Requirement`, `AcceptanceCriterion`, `Evidence`, or `Decision` node (§19.1). Where a payload exceeds budget and contains protected content, the system escalates for a policy decision rather than silently compressing it away.

### 25.3 Circuit-breaker safe-stop protocol
A circuit-break signals the in-flight agent to reach its nearest defined checkpoint, persist partial state, and halt there — logged distinctly from clean completion. Unconditional kill remains available only as an explicit, separately-authorized emergency override.

### 25.4 Model registry currency
Routing configuration references a maintained, versioned model registry, not hardcoded model-version strings. The registry tracks deprecation status; stale entries are flagged before they cause a runtime failure.

## 26. Integration Points

- **Intake/Project Plan:** `BudgetProfile` established at project scope, owned, persisted as a graph node.
- **Epic:** `BudgetProfile` cascades via `funded_by`; cost-to-value review uses actual prior `CostEvent` history where available.
- **Sprint:** Tokenomics Score computed per sprint; below-threshold blocks further autonomous routing until reviewed.
- **User Story/Execution:** `CostEvent` and `RoutingDecision` generated per execution, feeding the ledger and the Routing Quality Validator's sampling pool.

---

# Part D — Cross-Cutting Governance Programs

## 27. Score Composition, Calibration, and Grader Accuracy Program

This section is the single source of truth for how every score in this document (MLDC, Nelson, Tokenomics) composes, is validated, and is checked for grading accuracy. No layer restates or redefines these rules locally.

### 27.1 Unified score composition rule (closes the cap-ambiguity gap)

```text
final_score = min(
  weighted_domain_total,
  every applicable overall-score cap,
  every applicable domain-specific cap (applied to that domain before the weighted total is computed)
)
```

All caps are evaluated independently against the same evidence pass; the lowest resulting value wins. Domain-specific caps (e.g., a documentation-conflict cap on one Nelson domain) are applied to that domain's contribution before the weighted sum runs; overall-score caps (e.g., missing README, the security cap, the protected-content-integrity cap) are applied to the final weighted result. This is the one and only composition path — every scorecard agent (MLDC, Nelson, Tokenomics) implements this rule rather than its own variant.

### 27.2 Score Calibration and Outcome Validation (closes the no-calibration-story gap)

No score's weights are treated as permanently correct. On a defined recurring cadence:

- Correlate historical scores against measured downstream outcomes — onboarding time-to-first-merged-PR and incident rate for Nelson; defect/rework rate and design-review cycle time for MLDC; actual cost-per-outcome and quality-agreement rate for Tokenomics.
- Where a domain's weight does not predict its associated outcome, flag it for review rather than treating the original weighting as self-evidently correct.
- Every weight/threshold change is versioned (`PROCESS_CHANGELOG.md`, §29) with the outcome data that motivated it.

### 27.3 Grader Accuracy Program (closes the ungraded-graders gap)

Applies uniformly to MLDC, Nelson, and Tokenomics scoring agents:

- A defined percentage of agent-assigned scores/decisions is sampled on a rolling basis for human review.
- Agreement rate between agent and human reviewer is tracked as its own metric, per scoring domain, and reported alongside the scores themselves (`/.ai/nelson/grader-accuracy-log.json`).
- A sustained drop in agreement rate for a given domain triggers review of that domain's scoring agent, not just the repos it's scoring.
- This program is what the Routing Quality Validator Agent (§22) and Grader Sampling Agent (§11) feed.

## 28. Maturity Staging and Shadow-Mode Promotion Policy

Applies to any newly introduced check across all three layers, not only the knowledge-graph layer where it was first identified as missing:

```text
shadow mode → advisory → blocking
```

A check is promoted from shadow to advisory, and advisory to blocking, only after a defined number of scoring cycles with measured precision/recall (via §27.3) clearing a defined bar. New checks default to shadow mode. This governs, at minimum: conflict detection, orphan detection, and unsupported-completion-claim detection (§19.6); any newly introduced Tokenomics routing-quality heuristic; any newly introduced MLDC pattern-matching rule.

## 29. Process Self-Governance (closes the meta-governance and version-hygiene gaps)

The Process framework governs itself with the same artifacts it requires of every repository:

```text
.ai/process/PROCESS_CURRENT_STATE.md   — what exists, what's incomplete, what's deferred, in this Process itself
.ai/process/PROCESS_ROLLBACK.md        — how to roll back an agent, skill, or scoring-rubric change that misbehaves
.ai/process/PROCESS_CHANGELOG.md       — versioned record of every weight, cap, and threshold change, with the calibration evidence that motivated it
```

### 29.1 Process self-check
`/process-self-check` runs Nelson's own rubric (§14) against this specification document. A future revision of this document that reintroduces version residue, undefined variables, or unstated cap-composition logic — the specific defects identified in the prior revision — should fail its own hygiene check. This document, as issued, is a single current-state specification with no reference to a prior version's language, satisfying that check as of this revision.

### 29.2 Non-Duplication Policy Statement (original text, restored) and Agent ownership table (new enforcement mechanism)

Process v9.51 does not create agent sprawl.

If an existing Process agent already owns discovery, design, testing, auditing, security, or certification, Nelson consumes that evidence and scores or persists it. Nelson adds repo-hygiene scoring, canonical artifact generation, drift detection, and report quality assurance.

The statement above was, in v9.5, a policy declaration with no enforcement mechanism behind it. The table below turns it into one:

| Agent | Sole owner of |
|---|---|
| MLDC agents (§4) | UI component/pattern/theme/accessibility evidence |
| Nelson agents (§11) | Repo artifact presence, freshness, current-state truth |
| Requirements Knowledge Steward (§19.4) | Graph construction, traceability, conflict/orphan/drift detection |
| Tokenomics agents (§22) | Budget, routing, ledger, circuit-breaking |
| Nelson Research Agent (§11) | External best-practice baseline only — does not perform graph construction or scoring itself |

An automated ownership-conflict check fails the build if two agents write to the same artifact or claim the same evidence domain — the policy statement above states the intent; this table and check are what actually enforce it.

---

## 30. Combined Gate Model

| Gate Area | Score / Output | Purpose |
|---|---|---|
| MLDC Alignment | MLDC Alignment Score | UI follows approved design-system patterns. |
| Nelson Repo Hygiene | Nelson Repo Score | Repo is understandable, operable, owned, supportable, current. |
| Tokenomics Governance | Tokenomics Score | AI cost spend is measured, policy-bounded, and quality-preserving. |
| Grader Accuracy | Agreement rate per domain (§27.3) | Scoring agents themselves remain trustworthy. |
| PR Evidence | MLDC + Nelson + Tokenomics evidence | Reviewers see UI, repo, and cost findings together. |
| Certification | MLDC + Nelson + Tokenomics verdicts | Proceed, proceed-with-cleanup, managed-risk, or block. |
| Session Close | All findings + Process self-check | Generated knowledge, including the Process's own state, survives beyond the session. |

---

## 31. Definition of Done for v9.51 Bootstrap

- MLDC findings and Alignment Score generated for applicable UI work; PR Evidence exists.
- Nelson Repo Score generated with the unified composition rule (§27.1) applied; required artifacts inventoried; missing critical artifacts created or documented as gaps.
- Tokenomics Score generated; `BudgetProfile` owned and ceilinged; ledger reconciled with no unresolved double-deduction; no stale model-registry entries; any circuit-break followed the safe-stop protocol or is logged as an authorized emergency override.
- `docs/CURRENT_STATE.md`, `ARCHITECTURE.md`, `RUNBOOK.md`, and rollback guidance exist or are explicitly blocked.
- Ownership and escalation documented; agent ownership table (§29.2) has no unresolved conflicts.
- Graph checks operating at their current maturity stage (§28) — none promoted to blocking without evidence.
- Grader Accuracy sampling active for every scoring domain in use.
- Generated reports pass layout QA.
- `/process-self-check` passes against this specification.

---

## 32. Final Operating Statement

The Process v9.51 turns UI alignment, repository hygiene, cost governance, and requirements traceability into measurable, enforceable, continuously refreshed delivery quality systems — and holds its own scoring and gating mechanisms to the same standard. Caps compose one way, everywhere. Scores are checked against real outcomes, not assumed correct. New checks earn blocking authority through evidence, not by default. Agents have exclusive, non-overlapping ownership, enforced automatically rather than declared by policy. And the Process specification itself is subject to the same current-state, self-describing discipline it requires of every repository it governs.
