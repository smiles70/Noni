# PS-N8N-001B — Promote n8n cleanup batch to production

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** awaiting owner prod sign-off
**Parent:** PS-N8N-001 · Staging commits: `17a54cd` (config removal) +
`d9ef1c7` (alembic renames) + `a0a5fa7`/`a1f7670` (RESUME docs).

## Problem statement

The n8n residual-removal batch (dead config vars + alembic filename
renames) sits on staging only. Production still declares
`N8N_WEBHOOK_*`/`FEATURE_HELP_REQUESTS` in `config.py` (harmless but
drift) and the old migration filenames.

## Scope

- `backend/core/config.py` — 3 dead fields removed.
- `alembic/versions/` — 4 renames (revision IDs unchanged; prod chain
  unaffected — alembic reads IDs, not filenames).
- Intake/RESUME docs.

## Risk

Near-zero: no code reads the removed fields; renames don't alter
migration content; prod alembic head already `retire_n8n_help`.

## Acceptance criteria

- [ ] Cherry-pick/merge staging batch onto main, verify diff is only
      these files.
- [ ] Prod deploy green; API health 200; `/health` unchanged.
- [ ] CI green (bundle/black already fixed in prior batch).
- [ ] Jev post-deploy gate.
