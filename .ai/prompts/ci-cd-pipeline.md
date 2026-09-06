# Role & Objective

You are an expert DevSecOps, GitHub Automation, and AI Agent Architect operating under **Process v9.51** for the `smiles70/Noni` repository (customer-facing product: Mynaani).

Your task is to produce a **single, adapted prompt document** that an AI IDE or agent can later use to set up an agile project-management workflow and a **pre-deploy validation pipeline**. The pipeline simulates a virtual multi-stage environment using automated testing suites ("agents and skills") to validate code before the existing Railway deployment workflows run. It does **not** deploy on its own.

This document is **advisory only**. Do not generate files, push commits, or run commands. It is a Process v9.51-compliant blueprint for a future implementation.

---

## Repository Context (Noni / Mynaani)

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React + TypeScript + Vite (`frontend/`) | Build with `npm ci && npm run build` inside `frontend/` |
| Backend | Python 3.12 + FastAPI (`backend/`) | Dependencies in `requirements.txt`; tests in `backend/tests/` |
| Database | PostgreSQL (Railway) | Most backend tests require Postgres; payment-provider tests can run without real Stripe |
| Auth | Mock / Magic (deferred) | `AUTH_PROVIDER=mock` in production currently; Magic is the target |
| Payments | Stripe mock + live | `PAYMENT_PROVIDER=mock`; live `StripePaymentProvider` is ready but not yet switched on |
| Deployment | Railway backend + Cloudflare Pages frontend | Existing workflows: `deploy.yml`, `deploy-staging.yml`, `deploy-railway-prod.yml` |
| Process | v9.51 | `PROCESS_V9.51_SPEC.md` governs intake, preflight, ontology, and tokenomics |

---

## System Architecture & Multi-Stage Pipeline Logic

1. **GitHub Issues & Board Setup**  
   Enables tracking, provides structured templates, and initializes a GitHub Projects v2 board. Welcome notifications are optional and non-blocking. Follow v9.51 `Owner` and `WorkItem` conventions; any created issue should reference a knowledge-graph `Requirement`, `Gap`, or `Decision` node when one exists.

2. **Virtual QA Agent Stage**  
   Runs on `pull_request` to `staging` (or `workflow_dispatch`). Executes:
   - Backend: `python -m compileall backend/`, `ruff` or `bandit` if installed, `pytest backend/tests/test_stripe_payment_provider.py` (no Postgres/Stripe required).
   - Frontend: `npm ci && npm run lint && npm test && npm run build` inside `frontend/`.
   - Secret leak detection: `truffleHog filesystem . --only-verified` (advisory, not blocking).

3. **Virtual UAT Agent Stage**  
   Triggers only if QA passes. Executes:
   - Contract / payment-provider tests that do not require a live database.
   - Playwright E2E tests (`npm run e2e`) **only when a test backend is available**. If not, the stage returns a clear advisory that E2E is pending.

4. **Pre-Deploy Gate (no deployment)**  
   The existing `deploy-staging.yml` and `deploy-railway-prod.yml` remain the only deployment workflows. This new pipeline only validates. It can be configured as a **required status check** for `staging` pull requests so a deploy cannot proceed until QA + UAT pass.

---

## Non-Goals and Constraints

- Do **not** create a second deployment path.
- Do **not** modify the existing `deploy.yml`, `deploy-staging.yml`, or `deploy-railway-prod.yml`.
- Do **not** flip `PAYMENT_PROVIDER` to `stripe` or change Railway CPU/memory sizing.
- Do **not** run the pipeline in this session. This is a prompt blueprint.
- All work must respect v9.51 `BudgetProfile` and `CostEvent` governance if an AI agent later executes it.

---

## Adapted File Plan

### File 1: Bug Report Template
Path: `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug Report
about: Create a report to help us improve and fix errors.
title: '[BUG] '
labels: bug
assignees: ''
---

## Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
What actually happened, including any error messages or screenshots.

## Environment
- URL:
- Browser:
- Device:

## Knowledge-Graph Link (optional)
Node ID: 

## Acceptance Criteria
- [ ] Bug is fixed on the respective route.
- [ ] Unit or integration tests covering this edge case are passing.
- [ ] No regression impacts on existing UI workflows.
```

### File 2: Feature Request Template
Path: `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature Request
about: Suggest an idea or new user story for this project.
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## User Story
As a [user type], I want [action] so that [benefit/value].

## Context
Why is this needed? Link to any related intake, ADR, or conversation.

## Knowledge-Graph Link (optional)
Node ID:

## Acceptance Criteria
- [ ] Requirement 1 built out.
- [ ] Requirement 2 tested and validated.
- [ ] UI elements match designs.
- [ ] Related intake or ADR is updated if applicable.
```

### File 3: Work Tracking Setup Workflow
Path: `.github/workflows/setup-work-tracking.yml`

```yaml
name: Setup Work Tracking

on:
  workflow_dispatch:

jobs:
  configure-repo:
    runs-on: ubuntu-latest
    permissions:
      repository-projects: write
      contents: write
      issues: write

    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Enable GitHub Issues
        run: |
          echo "Enabling GitHub Issues..."
          gh repo edit ${{ github.repository }} --enable-issues=true

      - name: Create GitHub Project v2 board
        run: |
          gh project create \
            --owner "${{ github.repository_owner }}" \
            --title "Mynaani Sprint Board" \
            --format github-v2 \
            || echo "Board already exists or could not be created."

      - name: Create standard labels
        run: |
          for label in bug enhancement blocked qa-pending; do
            gh label create "$label" --force || true
          done
```

### File 4: New Collaborator Welcome Workflow
Path: `.github/workflows/collaborator-welcome.yml`

```yaml
name: New Collaborator Welcome

on:
  member:
    types: [added]

jobs:
  welcome:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      NEW_USER: ${{ github.event.member.login }}
    steps:
      - name: Create welcome issue
        run: |
          gh issue create \
            --repo ${{ github.repository }} \
            --title "Welcome @${NEW_USER} to the Mynaani team" \
            --assignee "${NEW_USER}" \
            --body "Hello @${NEW_USER},

You have been added to the project work-tracking loop.

### Getting started
1. Check the repository **Projects** tab for the sprint board.
2. Use the bug report or feature request templates when logging new work.
3. Reference 'Closes #IssueNumber' in your pull requests.
4. Read '.ai/intake/' for active work streams and 'PROCESS_V9.51_SPEC.md' for our delivery model."
```

### File 5: QA + UAT Pipeline Workflow (Pre-Deploy Validation)
Path: `.github/workflows/qa-uat-pipeline.yml`

```yaml
name: QA and UAT

on:
  workflow_dispatch:
  pull_request:
    branches:
      - staging

jobs:
  virtual-qa-agent:
    name: QA - Lint, Security, and Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install backend dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Backend syntax and compile check
        run: python -m compileall backend/

      - name: Backend security scan
        run: |
          pip install bandit
          bandit -r backend/ -f txt -o bandit-report.txt || true
          cat bandit-report.txt

      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci

      - name: Frontend lint
        working-directory: frontend
        run: npm run lint

      - name: Frontend tests
        working-directory: frontend
        run: npm test

      - name: Secret leak detection
        run: |
          pip install truffleHog
          truffleHog filesystem . --only-verified || true

  virtual-uat-agent:
    name: UAT - Contract and E2E Tests
    needs: virtual-qa-agent
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install backend dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Payment-provider contract tests
        run: |
          pytest backend/tests/test_stripe_payment_provider.py -v

      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci

      - name: Playwright E2E tests
        working-directory: frontend
        run: npm run e2e --if-present

  report-uat-result:
    name: Report UAT Status
    needs: virtual-uat-agent
    runs-on: ubuntu-latest
    steps:
      - name: Post pre-deploy validation outcome
        run: |
          echo "QA and UAT completed."
          echo "The existing deploy-staging.yml remains responsible for actual deployment."
```

---

## Execution Instructions (for a future AI agent)

1. Confirm the preflight for this pipeline is approved.
2. Create the directories `.github/ISSUE_TEMPLATE/` and `.github/workflows/`.
3. Write the five files above, preserving the exact `{{ }}` GitHub Actions syntax.
4. Before the first run:
   - Confirm GitHub Issues are enabled and a Project v2 board exists.
   - Confirm `npm run lint`, `npm test`, `npm run build`, and `npm run e2e` are defined in `frontend/package.json`.
   - Confirm `pytest` and the backend test configuration work in the Actions environment.
5. Run the `setup-work-tracking.yml` workflow manually first.
6. Optionally set `qa-uat-pipeline.yml` as a required status check for `staging` branch protection so `deploy-staging.yml` cannot deploy a failing PR.
