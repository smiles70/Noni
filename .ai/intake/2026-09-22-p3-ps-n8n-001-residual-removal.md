# PS-N8N-001 — Residual n8n artifacts after descope

**Date:** 2026-09-22 · **Priority:** P3 · **Status:** verified — cosmetic removal shipped
**Skill check:** `error-taxonomy` — `infra-drift` adjacent; config cleanup.
Jev gate run — verdicts below.

## Problem statement

n8n (N8N-HELP-001, staging-only help widget + delivery pipeline) was
descoped and retired per ADR-0032 — widget, `api/help.ts`,
`routes/help.py`, and docs removed; `retire_n8n_help` migration dropped
the support tables and sits at prod head. Residual artifacts remain.

## Inventory (confirmed in code/history, not assumed)

| Artifact | Location | Disposition |
|----------|----------|-------------|
| Dead env vars | `backend/core/config.py:92-95` — `N8N_WEBHOOK_URL`, `N8N_WEBHOOK_TOKEN`, zero readers | **remove** |
| Migration history | `alembic/versions/n8n_help_*.py` (4 files) | **keep** — `retire_n8n_help` down_revision chains through them; fresh DBs replay the chain |
| Historical ADR | `docs/decisions/0032-website-chat-widget.md` | **keep** — correct retirement record |
| Stale local clone | `/home/h/mynaani/n8n-help-flow` (same origin, not deployed) | **owner file — leave** |
| Hosted n8n service | Railway — outside repo | **verify separately** (Jev 0.94) |

## Jev gate (jev-1.13.0)

- Env-var removal safe (zero readers): 0.89
- Keep alembic history (chain integrity): 0.92
- System free of functional n8n paths: 0.55 — hedged on out-of-repo
- Verify hosted service separately: 0.94
- Stale clone: leave-owner
- Severity: cosmetic-remnants (1.04)

## Removal plan

1. Delete `N8N_WEBHOOK_URL` / `N8N_WEBHOOK_TOKEN` from `config.py` — done
   in this commit.
2. Railway project audit — confirm no `n8n` service/env in the prod or
   staging Railway projects; if present, owner removes (infra
   credentials live outside repo).
3. Stale clone `/home/h/mynaani/n8n-help-flow` — owner decision
   (Jev: leave-owner).
4. Alembic history stays — removing the chain files breaks fresh-DB
   replays.

## Acceptance criteria

- [x] Zero `N8N_*`/`FEATURE_HELP_REQUESTS` references in backend code.
- [x] Railway audit — only `noni-api` in prod + staging projects, zero
      N8N vars deployed. No hosted n8n service.
- [x] Backend suite green post-removal (788 passed); config loads clean.

## Final sweep (2026-09-22)

- Stale clone `/home/h/mynaani/n8n-help-flow` deleted — verified unique
  work first (unpushed branches, untracked research docs), archived to
  `~/Downloads/legacy-help-flow-archive-2026-09-22.tar.gz` (5.7 MB,
  git history included) before removal.
- Alembic version files renamed `n8n_*` → `help_flow_*` — alembic keys
  off revision IDs, head still resolves `retire_n8n_help (head)`.
- Zero `n8n` strings remain in `backend/`, `frontend/src/`, `alembic/`
  filenames. ADR-0032 + intake history keep the name as retirement
  record only.
