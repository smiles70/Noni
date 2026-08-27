# Nelson Repo Hygiene Scorecard — Mynaani

**Assessment date:** 2026-08-26
**Process:** v9.51
**Score composition rule:** `final_score = min(weighted_domain_total, every applicable overall-score cap)`

## 1. Artifact Inventory

| Required Artifact | Present | Location / Status |
|---|---|---|
| README.md | PRESENT | repo root |
| CONTRIBUTING.md | PRESENT | repo root |
| SECURITY.md | MISSING | not at repo root |
| CODEOWNERS | MISSING | not at repo root or `.github/` |
| CHANGELOG.md | PRESENT | `docs/changelog.md` |
| docs/ARCHITECTURE.md | PRESENT | root `ARCHITECTURE.md`; `docs/architecture/` also present |
| docs/CURRENT_STATE.md | MISSING | no canonical current-state doc |
| docs/ONBOARDING.md | MISSING | no canonical onboarding doc |
| docs/RUNBOOK.md | MISSING | `docs/ops/` runbooks exist but no canonical `RUNBOOK.md` |
| docs/ROLLBACK.md | MISSING | `docs/ops/epic002-rollback-plan.md` exists but no canonical `ROLLBACK.md` |
| docs/TEST_STRATEGY.md | MISSING | no canonical test-strategy doc |
| docs/adr/ | PRESENT | `docs/decisions/` (27 ADRs) |
| .ai/process/PROCESS_CURRENT_STATE.md | PRESENT | v9.51 bootstrap |
| .ai/nelson/artifact-inventory.json | PRESENT | This assessment |

## 2. Domain Scores

| Domain | Weight | Raw Evidence | Domain Score |
|---|---|---|---|
| Repository Orientation | 10 | README, purpose, stack, build/deploy summary in README | 9 / 10 |
| Architecture | 15 | `ARCHITECTURE.md`, `docs/architecture/`, data-flow, schema, vendors | 13 / 15 |
| Decision Records | 10 | 27 ADRs in `docs/decisions/` | 10 / 10 |
| Operational Readiness | 15 | `docs/ops/` runbooks, incident response, recovery, status page, SRE audit | 11 / 15 |
| Knowledge Transfer | 15 | README, staging-deploy, integrations-setup, local-testing-guide; no `ONBOARDING.md` | 9 / 15 |
| Ownership | 10 | No `CODEOWNERS`, escalation path unclear | 3 / 10 |
| Delivery Governance | 10 | `CONTRIBUTING.md`, `.github/workflows/`, pre-commit config | 8 / 10 |
| Security and Compliance | 5 | Threat model in `docs/audits/`, no `SECURITY.md` | 3 / 5 |
| Testability | 10 | `backend/tests/`, `frontend/src/` tests, CI test matrix | 8 / 10 |

**Weighted raw total:** `9 + 13 + 10 + 11 + 9 + 3 + 8 + 3 + 8 = 74` / 100

## 3. Score Caps

| Cap Rule | Applies | Result |
|---|---|---|
| Missing README caps score at 90 | NO | — |
| Missing architecture docs caps score at 85 | NO | — |
| Missing current-state artifact caps score at 85 | YES | <= 85 |
| Missing runbook/rollback for production systems caps at 80 | YES | <= 80 |
| Missing ownership/escalation path caps at 80 | YES | <= 80 |
| No `SECURITY.md` for production system handling sensitive data (v9.51 §14.3) | YES | <= 50 |

## 4. Final Score

```text
final_score = min(74, 85, 80, 80, 50)
final_score = 50
```

**Nelson Repo Score: 50 / 100**

## 5. Gate Verdict

| Band | Meaning | Status |
|---|---|---|
| 95-100 | Industry Leading | — |
| 85-94 | Enterprise Mature | — |
| 70-84 | Managed Risk | — |
| <70 | Operational Risk | **CURRENT** |

**Verdict:** `Operational Risk` — block major work until `SECURITY.md`, `CODEOWNERS`, canonical `RUNBOOK.md`/`ROLLBACK.md`, and frontend dependency vulnerabilities are addressed.
