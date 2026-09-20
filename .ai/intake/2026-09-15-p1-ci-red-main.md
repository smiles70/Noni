# P1 — `CI` workflow is red on `main` (ruff F401 ×2, Trivy 12 OS CVEs, a10-smoke corrupt YAML)

## Problem

The `CI` workflow has failed on every `main` push since at least
`34720490235` (2026-09-12) — pre-existing, unrelated to the caregiver
work. The latest run `35023135102` (on `f73ca68`) fails in three
independent places:

### 1. Backend ruff lint — 2 × F401 (auto-fixable)

- `backend/app/main.py:43` — `FeatureFlags` imported but unused
  (`from backend.core.feature_flags import FeatureFlags, get_flags` —
  only `get_flags` is referenced).
- `backend/tests/test_feature_flags.py:5` — `import pytest` unused.

Ruff reports `[*] 2 fixable with the --fix option`.

### 2. Trivy backend image scan — 12 vulns (3 CRITICAL, 9 HIGH)

Job `container-scan`, action `aquasecurity/trivy-action@v0.36.0`,
severity gate `CRITICAL,HIGH`, `exit-code: 1`, `ignore-unfixed: true`.
All findings are **OS packages** in the `python:3.12-slim` (Debian 13 /
trixie) base image used by `backend/Dockerfile`, and all have status
`fixed` — patched Debian packages exist:

| Package | CVEs | Fix |
|---|---|---|
| `perl-base` | CVE-2026-13221 (CRITICAL) + CVE-2026-42496, -8376, -42497, -48962, -57432, -57433 | `5.40.1-6` → `5.40.1-6+deb13u1` |
| `libpcre2-8-0` | CVE-2026-86145, CVE-2026-89161 | `10.46-1~deb13u1` → `~deb13u2` |
| `libsqlite3-0` | CVE-2026-11822, CVE-2026-11824 | `3.46.1-7+deb13u1` → `+deb13u2` |
| `gzip` | CVE-2026-41992 (HIGH) | `1.13-1` → `1.13-1+deb13u1` |

Likely remediation: `apt-get upgrade` in the runtime stage, or repin the
`python:3.12-slim` base digest — needs the research protocol to pick the
correct option (see below). **Note:** per `error-taxonomy` skill,
`security-block` findings are classified *Hard Stop — escalate, do not
auto-fix*, so the Trivy remediation path needs explicit review.

### 3. `a10-smoke.yml` — corrupted workflow, zero-duration failures

Every push spawns an `a10-smoke.yml` run that fails in ~0s with no logs
("log not found" — GitHub cannot parse the workflow). The committed file
is structurally broken:

- Line 1 begins mid-file with `    - name: Install system dependencies`
  — the top of the workflow (name key, first steps) is missing/mangled.
- Line 4: `sudo apt-get install -y libpq-dev python3-devname: Backend A10 isolated smoke`
  — the top-level `name:` key was concatenated onto a `run:` block line.

The file is invalid YAML, so Actions rejects it at parse time. It has
never run its actual steps (Postgres service + `test_a10_smoke.py`).

## Trigger

Any push to `main` or `staging`. Inspect with
`gh run list --branch main` / `gh run view <id> --log-failed`.

## Current impact

- `CI` is permanently red on `main` — masks future regressions and
  trains everyone to ignore the signal.
- The backend image ships to Railway with 3 CRITICAL + 9 HIGH OS-level
  CVEs that all have available fixes.
- The A10 isolated smoke gate (Postgres + migrations + smoke test) has
  been silently dead — a designed safety net that does not exist.

## Outcome needed

1. Ruff clean on `backend/` (remove the two unused imports; verify no
   other F401s).
2. Trivy scan passes `CRITICAL,HIGH` gate — choose base-image repin vs
   `apt-get upgrade` vs `.trivyignore` via research; document decision.
3. `a10-smoke.yml` either repaired to valid YAML and passing, or
   consciously removed (decision recorded).
4. `CI` green on `main`.

## Scope / non-goals

- In scope: `backend/app/main.py`, `backend/tests/test_feature_flags.py`,
  `backend/Dockerfile`, `.github/workflows/a10-smoke.yml`, possibly
  `.github/workflows/ci.yml` / `.trivyignore`.
- Out of scope: dependency-version bumps for Python packages (separate
  intake), Deploy workflow changes.
- **Workflow-file changes must ship as their own commit** per
  `AGENTS.md` (`ALLOW_WORKFLOW_CHANGES=1 git commit`).
- Local working tree has an uncommitted `.github/workflows/ci.yml`
  modification belonging to the human — do not stage it.

## References

- Failing run: `gh run view 35023135102`
- Dockerfile: `backend/Dockerfile` (`python:3.12-slim`, 2-stage)
- Corrupt workflow: `.github/workflows/a10-smoke.yml`
- CI workflow: `.github/workflows/ci.yml` (locally modified — uncommitted)
- Error taxonomy skill: `.devin/skills/error-taxonomy/SKILL.md`
  (`security-block` → hard stop)
- Research memo: `.ai/research/2026-09-15-ci-red-remediation.md`
