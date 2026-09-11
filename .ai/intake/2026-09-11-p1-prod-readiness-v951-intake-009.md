# Intake: Production-readiness features (feature flags, Alembic rollback, PII/GDPR) — research closed

**Process:** v9.51  
**Date:** 2026-09-11  
**ID:** P1-PROD-READINESS-009  
**Status:** INTAKE — BUILD AUTHORIZED — implementation ready.  
**Owner:** Platform + Backend + Compliance  
**Source:** `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §4

---

## 1. Problem statement

Three production-readiness layers are not yet implemented:

1. **Feature flags** — no runtime toggles for canary or dark-launch.
2. **Alembic downgrade validation** — `alembic downgrade` has not been exercised in CI.
3. **PII / GDPR scan** — no automated audit of logged or stored personal data.

These are tracked as a single readiness intake because they are all required before a compliant, controlled go-live.

## 2. ICP / personas

| Persona | Goal | Frustration if unfixed |
|---|---|---|
| **Product owner** | Canary-deploy safely | Cannot roll out gradually or roll back without a full redeploy |
| **Compliance / Legal** | GDPR readiness | Cannot demonstrate data minimization and right-to-erasure |
| **Ops** | Safe migrations | No proof that a failed migration can be rolled back |
| **Engineer** | Safe experimentation | New features cannot be toggled off in production |

## 3. Research summary

### Internal evidence

- `/health/live` and `/health/ready` were added; readiness probes Postgres.
- No `backend/core/feature_flags.py` module exists.
- `alembic downgrade` has not been run in CI; the `0003` migration requires `pgcrypto`.
- Telemetry and logging may include raw emails, names, tokens, or billing details.

### External baseline

- Feature flags are typically env-var or DB-backed with middleware gating.
- GDPR Article 5 requires data minimization; logs should not include PII unless necessary and masked.
- Alembic downgrade safety is a standard CI gate for schema changes.

## 4. Options evaluated

| Option | Description | Verdict |
|---|---|---|
| A — implement all three | Add feature flags, downgrade CI, and PII masking | **Recommended when authorized** |
| B — implement separately | Split into three intakes | Viable if A is too large |
| C — defer to post-launch | Launch without these controls | **Rejected** — compliance and ops risk |

## 5. Architecture / approach

When implementation is authorized:

1. **Feature flags**: add `backend/core/feature_flags.py` with `os.environ` lookup and FastAPI middleware that injects flags into request state.
2. **Alembic rollback**: add a CI step that runs `alembic upgrade head && alembic downgrade -1` against a Postgres 15 service.
3. **PII/GDPR**: create `backend/core/pii.py` with a sanitizer; add a `logging.Filter` that masks configured fields; write `test_pii_masking.py`.

## 6. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Feature flags | Env-var based | Simplest; canary controlled via deployment config |
| Alembic gate | `upgrade head && downgrade -1` | Verifies reverse path |
| PII fields | email, name, token, password, billing details | Highest-risk fields |
| Mask pattern | `****` or `<redacted>` | Explicit and greppable |

## 7. MLDC alignment

- No new UI surfaces.
- Feature flags can gate UI routes without changing components.

## 8. Nelson repo-hygiene / knowledge graph

- Tracked as `P1-PROD-READINESS-009`.
- Readiness endpoints map to `.ai/journeys/default/journey.md` operational gates.

## 9. Epic / Block / Rack plan

Build is **not authorized** at this closure. If authorized:

| Block | Rack | Deliverable | Owner |
|---|---|---|---|
| 1. Feature flags | 1.1 | `backend/core/feature_flags.py` and middleware | Backend |
| | 1.2 | `test_feature_flags.py` | Backend |
| 2. Alembic | 2.1 | Add `alembic downgrade` step to `a10-smoke.yml` | Platform |
| | 2.2 | Prove `upgrade head && downgrade -1` works | Platform |
| 3. PII/GDPR | 3.1 | `backend/core/pii.py` sanitizer | Backend |
| | 3.2 | `logging.Filter` integration | Backend |
| | 3.3 | `test_pii_masking.py` | QA |

## 10. Test plan

- Feature flags: unit tests for middleware and gating.
- Alembic: CI step runs without exceptions.
- PII: every log event containing a configured field is masked.

## 11. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| PII scan finds more data than expected | High | Time-box audit; create follow-up intakes for each surface |
| Alembic downgrade is destructive | High | Run in isolated CI Postgres, not production |
| Feature flags complicate debugging | Medium | Log flag state at startup, not per request |

## 12. Acceptance criteria / Definition of Done

- `GET /health/ready` still passes and optionally checks Redis.
- `FEATURE_X` env var can disable a route without a new deploy.
- `alembic upgrade head && alembic downgrade -1` succeeds in CI.
- No PII appears unmasked in logs; `test_pii_masking.py` passes.

## 13. Rollback / operational notes

- Feature flags default to current behavior (off = existing flow).
- Migrations are tested in a CI Postgres container only.
- PII masker is non-destructive to stored data; it only affects logs.

## 14. Evidence

- `.ai/research/2026-09-11-backend-maturity-research-protocol.md` §4
- `.ai/audit/2026-09-11-agentic-ci-pipeline-002.md` readiness section
- `backend/app/main.py` health endpoints
- `backend/models/telemetry.py`
- `backend/app/telemetry.py` logging code
