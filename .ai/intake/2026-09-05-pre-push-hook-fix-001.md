# Intake: pre-push hook repair (non-destructive analysis)

**Date:** 2026-09-05
**ID:** TOOLING-QUALITY-002
**Status:** RESEARCHED — fix is a revert to a previously-working pattern

## Problem

`.husky/pre-push` fails on every push: `frontend/node_modules/.bin/tsc: not found`.

## Root cause (evidence)

- Commit `99ff3ad` ("fix husky pre-push to use workspace binary paths") rewrote
  the working `cd frontend && npm run type-check && npm run test:unit` into
  direct binary paths `frontend/node_modules/.bin/{tsc,vitest}`.
- This repo is an npm workspace (`package.json` → `workspaces: ["frontend"]`);
  binaries hoist to root `node_modules/.bin/`. `frontend/node_modules/` exists
  but contains no `.bin/tsc` — the path is permanently absent.
- Verified empirically: root `node_modules/.bin/tsc --noEmit -p
  frontend/tsconfig.json` exits 0; `cd frontend && vitest run` passes
  13 files / 120 tests (15 expected-fail).

## Non-destructive assessment

| Question | Answer |
|---|---|
| Does the fix change app code? | No — only `.husky/pre-push`, which executes exclusively during `git push`. |
| Does it alter what the hook enforces? | No — restores the originally intended checks (type-check + unit tests) that were live before `99ff3ad`. |
| Regression surface | None: the hook currently always fails, so any working version is strictly better; the checks themselves were already verified green. |
| Push latency | Restores ~15s of checks — the intended, previously-accepted cost. |
| Alternative rejected | Keeping direct binary paths — fragile under workspace hoisting; npm scripts are the canonical entry points in `frontend/package.json`. |

## Fix

Restore npm-script invocation via workspace flags from the repo root
(husky executes hooks at repo root):

```sh
npm run type-check --workspace=frontend
npm run test:unit --workspace=frontend
```

## Acceptance

- `sh .husky/pre-push` exits 0 locally.
- A real `git push` completes without `--no-verify`.
- `npm run lint --workspace=frontend` unaffected.
