# Super Prompt — Add QA → UAT to Existing Staging Flow (Process v9.51)

## Role

You are a Process v9.51 DevSecOps Agent. Your task is to analyze the current repository, identify the existing staging deployment flow, and add QA/UAT gates to that flow without creating a second staging push or a duplicate deployment path.

## Objective

Ensure every `push` to the `staging` branch runs **QA**, then **UAT**, then the existing staging deployment. Do not create a new deployment workflow. Do not add a second `push` trigger on `staging`.

## Operating rules (Process v9.51)

1. Read the existing workflow files before writing anything.
2. If a staging deploy already exists, modify it; do not create a new one.
3. If no staging deploy exists, create exactly one.
4. Every change must be traceable to an intake, preflight, or existing process document.
5. Log a `CostEvent` in `.ai/budgets/` for this work.
6. Do not run or push the workflow. Produce files only.

## Step-by-step procedure

### Step 1 — Discover the current CI/CD structure

Read these directories and files:

```bash
ls .github/workflows/
cat .github/workflows/deploy.yml
cat .github/workflows/deploy-staging.yml
cat .github/workflows/deploy-railway-prod.yml
cat .github/workflows/ci.yml
```

Answer these questions for yourself:

- Is there a workflow that deploys to staging on `push: branches: [staging]`?
- What is the exact filename of that workflow?
- What are the current jobs? Is there a preflight, build, or deploy job?
- What `needs` dependencies already exist?
- Does the repo have an existing `qa-uat-pipeline.yml` or similar gate?

### Step 2 — Decide the target workflow

If a `deploy-staging.yml` (or equivalent) already exists, that is your only target. Rename nothing. Create no new file for staging deployment.

If no staging deploy exists, create `.github/workflows/deploy-staging.yml` from scratch.

### Step 3 — Add QA agent job

Insert a `virtual-qa-agent` job before the deploy. It must:

- `needs:` the existing preflight job (if there is one), or run independently if no preflight exists.
- Set up Python 3.12 and Node 20.
- Install backend dependencies from `requirements.txt`.
- Run `python -m compileall backend/`.
- Run `bandit -r backend/` (advisory output, not blocking unless configured).
- Install frontend dependencies in `frontend/` with `npm ci`.
- Run `npm run lint`, `npm test`, and `npm run build` in `frontend/`.
- Run `truffleHog filesystem . --only-verified` (advisory).

### Step 4 — Add UAT agent job

Insert a `virtual-uat-agent` job that:

- `needs: virtual-qa-agent`
- Runs `pytest backend/tests/test_stripe_payment_provider.py -v`.
- Runs `npm run e2e --if-present` in `frontend/`.

If Playwright E2E requires a live backend, the step must be guarded so it does not fail the run when no test backend is available.

### Step 5 — Update deploy job dependencies

Find the staging deploy jobs (backend to Railway, frontend to Cloudflare Pages, etc.). Change their `needs:` to include `virtual-uat-agent`.

Example:

```yaml
  railway-deploy-backend:
    needs: [preflight, virtual-uat-agent]
    if: needs.preflight.outputs.railway_ready == 'true'
    ...

  cloudflare-pages-deploy:
    needs: [preflight, virtual-uat-agent]
    if: needs.preflight.outputs.cloudflare_ready == 'true'
    ...
```

### Step 6 — Ensure no duplicate staging push trigger

There must be exactly one workflow with:

```yaml
on:
  push:
    branches: [staging]
```

If another workflow already has this trigger, do not add the same trigger to a new file. Either remove the existing one (not recommended without preflight) or add the QA/UAT jobs to the existing file.

### Step 7 — Verify the repo matches the new flow

Read the updated workflow and confirm the job graph:

```
preflight (if exists)
    │
    ▼
virtual-qa-agent
    │
    ▼
virtual-uat-agent
    │
    ▼
deploy backend
    │
deploy frontend
```

### Step 8 — Validate before claiming complete

Run these local checks:

```bash
python -m compileall backend/
python -m json.tool .github/workflows/YOUR_WORKFLOW.yml > /dev/null
# Or use yamllint / python -c 'import yaml; yaml.safe_load(open(...))'
```

Do not push, commit, or trigger the workflow.

### Step 9 — Document the change in the v9.51 graph

Add or update these nodes in `.ai/nelson/requirements-knowledge-graph.json`:

- `Requirement`: `REQ-CD-001` — QA must run before staging deploy
- `Requirement`: `REQ-CD-002` — UAT must run before staging deploy
- `Capability`: `CAP-CD-QA` and `CAP-CD-UAT`
- `Gap`: `GAP-CD-001` resolved
- `SourceArtifact`: the updated workflow file

Recompute the graph hash and update `requirements-drift-report.json`.

### Step 10 — Log a `CostEvent`

Append to the appropriate budget file in `.ai/budgets/`.

## What to produce

1. The updated `.github/workflows/deploy-staging.yml` (or equivalent existing workflow).
2. A `requirements-drift-report.json` showing the change.
3. An updated `requirements-knowledge-graph.json`.
4. A `CostEvent` in the budget ledger.

## What not to do

- Do not create `.github/workflows/qa-uat-pipeline.yml` that also triggers on `push: branches: [staging]`.
- Do not create a second `deploy-to-railway` or `deploy-to-staging` job.
- Do not modify `deploy-railway-prod.yml` or `deploy.yml`.
- Do not push or run the workflow.
- Do not create new GitHub issues, project boards, or labels unless explicitly asked.

## Exit criteria

The only staging push flow in the repository now runs QA → UAT → deploy, and no duplicate staging workflow exists.
