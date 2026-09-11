# A10 isolated smoke — workflow problem research

Date: 2026-09-11
Scope: `backend/tests/test_a10_smoke.py` cannot be run in GitHub Actions yet.

## Observed symptoms

1. `git push` of `.github/workflows/a10-smoke.yml` from Devin was rejected:
   `refusing to allow an OAuth App to create or update workflow ... without workflow scope`.
2. Manual creation of the workflow through the GitHub UI was error-prone:
   - First attempt merged `python3-dev` and `name:` on the same line.
   - Second attempt placed the `Install system dependencies` step at the root of the
     workflow, above `on:`.
3. The first workflow run (before the YAML was mangled) failed at the
   `Install dependencies` step.

## Root causes

### 1. Devin token lacks `workflow` scope
- GitHub requires the `workflow` OAuth scope to create or modify `.github/workflows/*`.
- The current Devin token only has `repo` (or equivalent) and does not include `workflow`.
- This forces every workflow change to be done by the human in the GitHub UI, which is
  slow and error-prone.

### 2. Manual YAML edits are fragile
- Pasting multi-line YAML into the GitHub web editor can collapse newlines or insert
  text at the wrong indentation.
- A workflow has strict structure: the workflow `name:` is a root key, whereas step
  `name:` keys live inside `steps:`.
- Without linting before commit, malformed YAML is committed and the workflow fails
  before any tests run.

### 3. The workflow itself is not yet complete
- `pyproject.toml` does not declare `alembic` as a dependency, but the workflow calls
  `python -m alembic upgrade head`. `alembic` is already used in the repo for
  migrations and should be in `project.dependencies` or installed explicitly in the
  workflow.
- `psycopg2-binary>=2.9.0` may fall back to source compilation if a compatible wheel is
  not available for the GitHub Actions runner. Source compilation requires `libpq-dev`
  and `python3-dev` (or `python3.x-dev`) on the runner.
- `pip install -e '.[dev]'` will install the whole backend. If any of the transitive
  dependencies cannot build, the `Install dependencies` step fails.

## Options

### A. Grant Devin the `workflow` scope (recommended)
- Re-authorize the Devin GitHub integration and ensure `workflow` is checked.
- After that, Devin can create, lint, and push `.github/workflows/*` files through
  `git`, eliminating the manual UI whack-a-mole.
- This is the only sustainable option for ongoing CI work.

### B. One-time manual commit with a known-good workflow
- Copy the exact YAML into the GitHub UI, lint it locally first, and commit.
- Update `pyproject.toml` to add `alembic` and possibly pin `psycopg2-binary` to a
  Python-3.12-compatible wheel.
- This works once, but every future CI tweak will require the same manual dance.

### C. Run A10 smoke outside GitHub Actions
- Use an existing staging deployment with a Postgres instance and run the test there.
- Not ideal because it does not give us a clean, isolated, reproducible A10 gate on
  every backend change.

## Recommended immediate next step

Option A: re-authorize Devin with the `workflow` scope, then let Devin commit a
validated, linted workflow file and any needed `pyproject.toml` changes.

If Option A is not possible, use Option B with a single, final manual commit of the
complete, correct YAML.
