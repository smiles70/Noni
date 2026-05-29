---
description: Enterprise-grade code change discipline — research, blueprint, 1440-degree regression, triple-check, test review, implementation, verification, commit. Every code change gets the same rigorous treatment.
---

# Code Check Workflow

**Purpose:** Ensure every code change is researched, planned, tested, and verified before touching production code.

**Rule:** Never implement without explicit user approval at Gate 8.

---

## Phase 1 — Discovery

1. Read the active file the user is looking at.
2. Search the repo for all files related to the same concern (same imports, same patterns, same module).
3. Identify the scope: 1 file? Cross-module? Frontend + backend?
4. If the change is backend Python, run dependency scan: `grep -r "^import\|^from" backend/ --include="*.py" | grep -v "backend\." | grep -v "test_" | sort | uniq` — compare against `requirements.txt`.

---

## Phase 2 — External Research

5. Search web for best-in-class enterprise approach to the problem.
6. Read at least 3 authoritative sources (official docs, proven implementations, 2026 current).
7. Summarize: What did you learn that changes your prior assumptions?

---

## Phase 3 — Architecture Blueprint (Only if user requests)

8. Write `docs/blueprints/<issue>-<name>.md` covering:
   - Problem statement
   - Root cause
   - Design principle
   - Exact changes (file + line)
   - Files that do NOT change
   - Rollback plan
9. Write `docs/blueprints/<issue>-1440-regression.md` covering:
   - 12 test dimensions × 2 passes
   - Pass/fail criteria for each dimension
   - Execution order
   - Sign-off checklist

---

## Phase 4 — Risk Analysis

10. List 25 things most likely to go wrong (likelihood, impact, why).
11. List 30 edge cases (timer semantics, env/platform, error paths).
12. Mitigate all to Very Low with external research citations.
13. Identify the ONE thing (if any) that requires actual action.

---

## Phase 5 — Triple Check

14. **Check 1:** Read current state of target file(s). Establish baseline.
15. **Check 2:** Grep for related patterns across src/. Identify all files that need changes.
16. **Check 3:** Verify environment compatibility (tsconfig, package.json, test config, CI config).

---

## Phase 6 — Planned Code Presentation

17. Show exact diff — before/after, line numbers.
18. List files that do NOT change.
19. Verify no new dependencies needed (check package.json / requirements.txt).

---

## Phase 7 — Test Code Review

20. Present all planned test code.
21. Triple-check tests for:
    - False negatives (test passes on broken code)
    - Timer leaks (real timers left running)
    - TypeScript strict mode issues
    - Missing cleanup (spies, mocks, modules)
    - Environment mismatches (Node vs browser)
22. Revise tests based on findings. Remove misleading test names.

---

## Phase 8 — User Approval Gate (CRITICAL)

23. **STOP.** Present summary:
    - What files will change
    - What tests will be created
    - Estimated risk
    - Rollback plan
24. Ask explicitly: **"Do you want me to proceed with implementation?"**
25. If NO → stop immediately. Do not touch any file.

---

## Phase 9 — Implementation (Only after YES)

26. Apply code changes — minimal, focused edits only.
27. Create/update test files.
28. Run syntax check: `npx tsc --noEmit` or `python -m py_compile`.

---

## Phase 10 — Verification

29. Run unit tests: `npx vitest run` or `python -m pytest`.
30. Run regression tests specific to the change.
31. Run grep guard to verify the fix took and no regressions introduced.
32. Run full build: `npm run build` or `docker build`.

---

## Phase 11 — Commit & Push

33. `git diff --stat` — show what changed.
34. `git add -A && git commit --no-verify -m "..."`.
35. `git push origin main`.

---

## Phase 12 — Post-Verification

36. Monitor GitHub Actions for successful CI/CD.
37. Smoke test deployed behavior if applicable.
38. Update 720 assessment if score changed.

---

## Pre-Command Safety Checklist (BEFORE every `run_command`)

**Rule:** If a command must run from a specific directory, you MUST use the `Cwd` parameter.

1. Does this command need a specific working directory? (e.g., `frontend/`, `backend/`)
2. If YES → set `Cwd` parameter explicitly. **Never use `cd` in the command string.**
3. If NO → command runs from project root (where `package.json` or `pyproject.toml` lives).
4. **Never use PowerShell `&&` chaining** — it fails with parser error. Use `Cwd` + separate commands instead.
5. **Never use `cd` as part of the command** — `cd frontend && npm run build` is forbidden. Use `Cwd: ".../frontend"` instead.

## Forbidden Actions (Never Do These)

- Never implement without explicit user approval at Gate 8.
- Never create files the user did not ask for (no surprise .md files).
- Never write new code before showing the planned diff.
- Never skip the triple-check.
- Never skip test code review for bugs/blockers/breakers.
- Never leave real timers running in tests (use `vi.useFakeTimers()` + `vi.useRealTimers()`).
- Never use `window.*` in shared/isomorphic code (use `globalThis`).
- Never run `flyctl deploy` without dependency verification (check requirements.txt).
- Never run `npm`/`python` commands from the wrong directory — always verify `Cwd`.
