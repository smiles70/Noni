---
name: error-taxonomy
description: Classify gate failures and route to correct remediation playbook for Noni
---

# Error Taxonomy for Noni

## Failure Categories

### Auto-Fix (No Approval Required)
- `ruff-error` → Run `ruff check --fix backend/`
- `black-format` → Run `black backend/`
- `mypy-error` → Fix type annotations
- `unused-import` → Remove unused imports
- `pre-commit-fail` → Run `pre-commit run --all-files`

### Escalate to User (Recovery Agent Writes Diagnosis)
- `test-failure` → pytest, vitest failures
- `e2e-failure` → Playwright + axe failures
- `migration-conflict` → Alembic migration issues
- `bundle-overflow` → Exceeds bundle size budget
- `wcag-failure` → axe WCAG 2.1 AA scan failure

### Hard Stop (Immediate Escalation)
- `security-block` → bandit, npm audit, TruffleHog, Trivy findings
- `auth-failure` → Clerk JWT verification broken
- `infra-drift` → Docker build or terraform plan failure

## Remediation Playbook

### Type + Lint Fixes
```bash
ruff check backend/ --fix
black backend/
mypy backend/
```

### Test Failure Diagnosis
1. Read test output
2. Identify failing test file and assertion
3. Check if test or code is at fault
4. Write diagnosis to `.ai/recovery/YYYY-MM-DD_failure.md`

### Security Block Response
1. Read security tool output
2. Identify CVE or vulnerability
3. Check if patch available
4. Escalate immediately — do not auto-fix

### Migration Conflict Resolution
1. Never auto-resolve schema conflicts
2. Run `alembic current` to identify issue
3. Escalate to user with schema diff
