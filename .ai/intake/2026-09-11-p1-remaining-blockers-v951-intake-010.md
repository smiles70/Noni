# Intake: Remaining launch blockers — evidence-based remediation

**Process:** v9.51
**Date:** 2026-09-11
**ID:** P1-REMAINING-BLOCKERS-010
**Status:** INTAKE — research complete; build NOT authorized.
**Owner:** Platform + Backend + Security + Compliance
**Source:** `.ai/research/2026-09-11-remaining-blockers-research-protocol.md`
**Supersedes:** the coverage/vendor/migration/PII estimates in
`P1-BE-COVERAGE-006`, `P1-MAGIC-REQUESTS-007`, `P1-CI-BRANCH-COVERAGE-008`,
and the Alembic/PII portions of `P1-PROD-READINESS-009`.

---

## 1. Problem statement

The four prior intakes (006–009) were written from **estimates**. Re-measuring
the repository at `485b6cd` changed the priority order materially:

1. **Backend coverage is not 42 %.** Statement coverage is **85.65 %** — 1.35
   points from target. **Branch coverage is 61.95 %** against a 75 % target.
   The real work is branch coverage, not bulk statement backfill.
2. **`magic-admin` cannot be upgraded.** 2.5.0 is the latest release on PyPI.
   "Update the vendor" is not an available remediation.
3. **Enabling branch coverage breaks the current gate.** `fail_under` applies
   to coverage.py's *combined* score, which is 81.66 % — below the existing
   85 % gate. The gate must be restructured, not extended.
4. **Migrations are healthier than assumed.** One head, 20/20 downgrades
   defined. Only *execution* is unproven.
5. **PII logging is nearly clean.** Exactly one real leak exists:
   `backend/services/email.py:47` logs the provider's raw response body,
   which echoes the recipient address.
6. **The workflow-scope blocker is confirmed** and requires owner action.

Shipping without these closed leaves an unenforced coverage gate, a declared
CVE in the dependency graph, unproven rollback, and an unmasked PII path.

## 2. ICP / personas

| Persona | Goal | Frustration if unfixed |
|---|---|---|
| **Engineer** | Trust the gate | 296 uncovered branches; `else`/`except` paths ship untested |
| **QA / Release manager** | Verify before UAT | Coverage gate reports a combined number nobody targets |
| **Security / compliance** | Clean audit | `pip check` fails on a hard vendor pin |
| **Compliance / Legal** | GDPR defensibility | A rejected email writes a learner's address to logs |
| **Ops** | Safe rollback | `alembic downgrade` has never been executed |
| **Platform** | Ship CI fixes | `f6d9718` cannot be pushed without the `workflow` scope |

## 3. Research summary

See `.ai/research/2026-09-11-remaining-blockers-research-protocol.md` for the
full measured evidence. Key figures:

| Metric | Measured | Target |
|---|---|---|
| Statement coverage | 85.65 % (3,284 / 3,834) | 87 % |
| Branch coverage | 61.95 % (482 / 778) | 75 % |
| Missing branches | 296 | ≤ 195 |
| Test outcome | 454 passed, 2 skipped, 14 xfailed | green |
| `magic-admin` latest | 2.5.0 (installed) | — |
| Alembic heads | 1 (`p1_guest_gift_checkout`) | 1 |
| Downgrades defined | 20 / 20 | 20 / 20 |
| Token scopes | `gist, read:org, repo` | + `workflow` |

External baseline: FAANG-tier Python services gate statement ≥ 85 % and
branch ≥ 75 % as **separate** assertions; `coverage.py` cannot express two
thresholds in one `fail_under`, so a JSON-report assertion is the standard
pattern.

## 4. Options evaluated

| Option | Description | Verdict |
|---|---|---|
| A — bulk statement backfill | Write tests until statements hit 87 % | Insufficient; ignores the 296 missing branches |
| B — branch-first, module-targeted | Target the 14 lowest-coverage modules, whose missing branches dominate the gap | **Selected** |
| C — lower the targets to current | Set gates at 85/62 | Rejected; codifies the debt |
| D — wait for `magic-admin` upstream | Take no dependency action | Rejected; no release pipeline visible |

**Selected:** Option B, plus a `requests` pin override guarded by an import
regression test, and a target state of replacing `magic-admin` with a small
owned verifier.

## 5. Architecture / approach

No product architecture change. Changes are confined to tests, CI
configuration, dependency constraints, and one logging call.

1. **Coverage**: enable `branch = true`; assert statement and branch
   separately from `coverage json`; consolidate the duplicated coverage
   config between `pytest.ini` and `pyproject.toml`.
2. **Dependency**: pin `requests` to a non-vulnerable version in
   `pyproject.toml`, override `magic-admin`'s `==` pin explicitly, and add a
   test importing `magic_admin.http_client` so the `requests.packages` shim
   breaking fails CI rather than production. Target state: replace
   `magic-admin` with a ~60-line DID verifier covering the four calls and
   four exception types we actually use.
3. **Migrations**: prove `upgrade head → downgrade base → upgrade head`
   against a real Postgres service, documenting behaviour across the
   `663520a73af6` mergepoint.
4. **PII**: add `backend/core/pii.py`; stop logging raw provider response
   bodies in `email.py`; install a process-wide `logging.Filter`.
5. **Token**: owner runs `gh auth refresh -h github.com -s workflow`.

## 6. Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Coverage measurement | single `--branch` run, JSON-asserted | `fail_under` cannot express two thresholds |
| Coverage config location | consolidate into `pyproject.toml` | pytest already warns it is ignoring it; the split is drift risk |
| Statement target | 87 % | 1.35 pt from current; achievable |
| Branch target | 75 % | Requires ~101 additional covered branches |
| Backfill order | route modules before services | Routes exercise service branches transitively |
| `requests` strategy | pin ours + import regression test | Vendor upgrade is impossible; the shim is the only real risk |
| `magic-admin` target state | owned verifier | Surface is four calls and four exceptions |
| Downgrade test scope | `downgrade base`, not `-1` | `-1` is ambiguous across the branch/merge pair |
| PII mask token | `<redacted>` | Explicit and greppable |
| Token remediation | human-only | Agents must not hold or mint `workflow` scope |

## 7. MLDC alignment

- No new UI surfaces; no component changes.
- Test selectors continue to prefer roles/labels over CSS.
- Feature flags (already shipped in `485b6cd`) can gate UI routes without
  touching MLDC-constrained components.

## 8. Nelson repo-hygiene / knowledge graph

- Adds `P1-REMAINING-BLOCKERS-010` and marks 006–009 as superseded in
  measurement, not in intent.
- Records `CoverageMeasurement`, `DependencyConstraint`,
  `MigrationReversibility`, and `PIISurface` as tracked facts with the
  commands that produced them.
- Every rack maps to an existing backend module, CI file, or migration —
  no orphan requirements.

## 9. Epic / Block / Rack plan

Build is **not authorized** at this intake. Proposed plan:

### Epic — REMAINING-BLOCKERS-010

| Block | Rack | Deliverable | Owner |
|---|---|---|---|
| **0. Preflight** | 0.1 | Preflight doc approved; branch created | Platform |
| **1. Coverage instrumentation** | 1.1 | `branch = true`; consolidate coverage config | Platform |
| | 1.2 | CI step asserting statement ≥ 87 % and branch ≥ 75 % separately | Platform |
| | 1.3 | Baseline HTML/JSON report committed as evidence | QA |
| **2. Route branch coverage** | 2.1 | `account.py` 29 % → ≥ 85 % | Backend |
| | 2.2 | `session_validation.py` 43 % → ≥ 85 % | Backend |
| | 2.3 | `billing.py` 69 % → ≥ 85 % (lines 248-299) | Backend |
| | 2.4 | `auth.py` + `me.py` error branches | Backend |
| **3. Service/task branch coverage** | 3.1 | `magic_verifier.py` 54 % → ≥ 85 % | Backend |
| | 3.2 | `webhook_handler.py` 63 % → ≥ 85 % | Backend |
| | 3.3 | `org_tasks.py` 51 % and `org_quota.py` 61 % | Backend |
| | 3.4 | `organizations.py` 66 % (lines 390-640) | Backend |
| | 3.5 | `secret_rotation.py`, `database.py`, `entitlements.py`, `auth_verifier.py` | Backend |
| **4. Dependency remediation** | 4.1 | Pin `requests`; explicit `magic-admin` override | Security |
| | 4.2 | Import regression test for `magic_admin.http_client` | Security |
| | 4.3 | `pip-audit` against the declared graph in CI | Security |
| | 4.4 | Spike: owned DID verifier replacing `magic-admin` | Backend |
| **5. Migration reversibility** | 5.1 | CI job: `upgrade head → downgrade base → upgrade head` on Postgres | Platform |
| | 5.2 | Document mergepoint `663520a73af6` behaviour | Backend |
| **6. PII / GDPR** | 6.1 | `backend/core/pii.py` sanitiser | Backend |
| | 6.2 | Fix `email.py:47` provider-body logging | Backend |
| | 6.3 | Process-wide `logging.Filter` | Backend |
| | 6.4 | `test_pii_masking.py` | QA |
| **7. Token scope** | 7.1 | Owner refreshes token with `workflow` scope | **Owner** |
| | 7.2 | Push `f6d9718` to `staging`; verify A10 workflow runs | Platform |
| **8. UAT & close** | 8.1 | Full CI green with both coverage gates | QA |
| | 8.2 | Command-center report refreshed with measured values | Platform |
| | 8.3 | Production deploy — explicit owner approval per `AGENTS.md` | Product |

## 10. Test plan

### Per-rack acceptance

Every rack must:
- keep `pytest backend/tests` green (454 passed baseline, no new failures);
- raise the branch count covered, never lower it;
- keep `npm run type-check` and `npm run test:unit` green;
- be independently revertible and deployable to `staging`.

### Final acceptance

- Statement coverage ≥ 87 %, branch coverage ≥ 75 %, asserted separately.
- No route module below 80 % statement coverage.
- `pip-audit` clean against the declared graph; `magic_admin.http_client`
  import test passes.
- `upgrade head → downgrade base → upgrade head` green in CI.
- `test_pii_masking.py` proves email addresses are masked in log records.
- `gh auth status` includes `workflow`; `f6d9718` pushed and A10 green.

## 11. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Enabling `branch = true` breaks the existing 85 % gate | **High** | Restructure the gate in rack 1.1/1.2 *before* any backfill rack |
| Overriding the `magic-admin` pin breaks auth at runtime | **High** | Import regression test (4.2) plus full Magic auth suite; staging verification before prod |
| `downgrade base` is destructive | **High** | Run only against an isolated CI Postgres service; never against staging or production data |
| 296 missing branches is more work than estimated | Medium | Time-box blocks 2 and 3; promote overflow to a new intake rather than scope-creep |
| PII filter suppresses useful diagnostics | Medium | Mask values, preserve event names and status codes |
| Token scope never granted | Medium | A10 workflow stays local; document as a standing blocker rather than silently dropping it |
| Coverage config consolidation changes CI behaviour | Low | Land as its own commit with a before/after report |

## 12. Acceptance criteria / Definition of Done

| Blocker | Done when | Evidence |
|---|---|---|
| Backend coverage | statement ≥ 87 %, branch ≥ 75 % | `coverage json` output in CI artifacts |
| Branch gate | two separate assertions enforced in CI | `ci.yml` run log |
| `magic-admin` | `pip-audit` clean on declared graph; import test passes | audit log, test output |
| Alembic | full up→down→up cycle green | CI job log |
| PII / GDPR | no raw provider bodies logged; masking test passes | `test_pii_masking.py` |
| Token scope | `workflow` present; `f6d9718` pushed | `gh auth status`, push output |

## 13. Rollback / operational notes

- Coverage gates land as `warn` for one cycle before `error`, so in-flight
  PRs are not blocked.
- The `requests` override is a single-line revert.
- Migration downgrade testing never touches staging or production data.
- The PII filter is log-only and does not alter stored data.
- Per `AGENTS.md`: all work ships to `staging`; production requires explicit
  owner approval for that specific change.
- Per `AGENTS.md`: workflow changes ship as their own commit using
  `ALLOW_WORKFLOW_CHANGES=1`, never staged alongside other files.

## 14. Evidence

- `.ai/research/2026-09-11-remaining-blockers-research-protocol.md` — measured baseline
- `.ai/research/2026-09-11-backend-maturity-research-protocol.md` — superseded estimates
- `.ai/intake/2026-09-11-p1-backend-coverage-v951-intake-006.md`
- `.ai/intake/2026-09-11-p1-magic-requests-v951-intake-007.md`
- `.ai/intake/2026-09-11-p1-branch-coverage-gate-v951-intake-008.md`
- `.ai/intake/2026-09-11-p1-prod-readiness-v951-intake-009.md`
- `pytest.ini`, `pyproject.toml` — conflicting coverage configuration
- `backend/services/magic_verifier.py` — vendor usage surface
- `backend/services/email.py:47` — the one confirmed PII leak
- `alembic/versions/*.py` — 20 revisions, 20 downgrades
- `.github/workflows/a10-smoke.yml` — blocked by token scope
