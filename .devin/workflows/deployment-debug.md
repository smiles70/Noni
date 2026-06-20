---
description: Systematic debugging workflow for Fly.io deployment failures, Gunicorn worker boot errors, and Docker cache issues. Based on production incidents and external expert resources.
---

# Deployment Debug Workflow

Use this workflow when `flyctl deploy` fails with health check timeouts, worker boot failures, or `ModuleNotFoundError`.

## Phase 1: STOP — Do Not Guess

1. **Cease all command execution.**
2. Do not modify code, add dependencies, or run deploy commands until root cause is known.
3. Write down the exact error message and the machine ID.

## Phase 2: Gather Evidence (Logs)

// turbo
1. Get logs from the FIRST failed boot cycle (not restart loops):
   ```bash
   flyctl logs --app noni-api --machine <ID> --no-tail | head -50
   ```
2. Look for Python tracebacks, `ModuleNotFoundError`, `SyntaxError`, `ImportError`.
3. If the log shows `HaltServer 'Worker failed to boot.' 3`, the error is in **import/startup phase**, not runtime.
4. Check `flyctl status --app noni-api` and `flyctl checks list --app noni-api`.

## Phase 3: Root Cause Classification

### Category A: `ModuleNotFoundError` or `ImportError`
- **Check `requirements.txt` FIRST.**
- Scan all backend imports: `grep -r "^import\|^from" backend/ --include="*.py" | grep -v "backend\." | grep -v "test_" | sort | uniq`
- Compare against `requirements.txt`. Any missing entry = guaranteed failure on fresh build.
- **Ask:** Was Docker build cache recently invalidated? (New file added, `COPY` layer changed?)
- If cache was stale, the previously "working" image was hiding dependency drift.

### Category B: `HaltServer` with No Import Error (Timeout)
- **Check for Alembic in lifespan.** If `main.py` lifespan calls `alembic upgrade head`, this is the cause.
- Gunicorn spawns multiple workers. Each executes lifespan independently.
- Concurrent Alembic = deadlock on `alembic_version` table lock.
- **Fix:** Move to `fly.toml` `[deploy] release_command = "alembic upgrade head"`. Remove from lifespan.

### Category C: 19–20 Second Timeout Pattern
- If workers boot then crash after ~19s, check for:
  - Database connection pool exhaustion
  - `lifespan` hanging on synchronous DB call
  - External service dependency unreachable at startup

## Phase 4: Verify Before Fix

1. Do not add a dependency version without checking Python compatibility.
2. Do not modify `lifespan` without confirming the release_command path.
3. Cross-reference all changes against `infra/Dockerfile` and `fly.toml`.

## Phase 5: Apply Fix — Single Change at a Time

1. Make ONE change.
2. Commit and push.
3. Deploy.
4. Verify: `flyctl status --app noni-api` should show `started` with checks `passing`.
5. If still failing, return to Phase 2. Do not stack multiple fixes.

## Phase 6: Post-Incident Prevention

1. After any new Python file addition, run the import scan against `requirements.txt`.
2. Consider adding `RUN pip check` to the Dockerfile build stage.
3. Document the fix in commit messages and memory.

## Critical Rules

- **Rule 1:** Stale Docker cache hides dependency drift. A "working" deploy does not prove dependencies are correct.
- **Rule 2:** The real error is in the FIRST boot log. Restart loops obscure it.
- **Rule 3:** Fixing one layer can expose a deeper layer. Continue until checks pass.
- **Rule 4:** `release_command` runs ONCE before workers boot. `lifespan` runs PER WORKER. Never put migrations in lifespan.
- **Rule 5:** Run `flyctl deploy` from the repo root (`/mnt/c/Users/kimem/Noni` in WSL), never from `infra/`.
