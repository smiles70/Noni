# ADMIN-OPS-HYGIENE-001 — close-out: flags, deletion execution, B2B rescore

Date: 2026-09-07 · Parent epic: ADMIN-OPS-001 (E1–E6 shipped)

## Items

- **H1 flag resolution** — `account_flags` rows have no lifecycle. Add
  `resolved_at`/`resolved_by`/`resolution_note`, a staff `resolve` verb,
  open-only default filter, `flag.resolve` audit. Triage-level action:
  `require_staff` (not admin) — support owns flag review; documented.
- **H2 deletion execution** — `cleanup_deleted_accounts` Celery task is a
  stub (`return "not_implemented"`); `execute_deletion` exists but nothing
  calls it. Wire the daily beat task to execute due requests.
- **H3 B2B rescore** — re-score the enterprise-readiness rubric post-E1–E6;
  evidence-backed, no overclaim.

## Safety

- H2 is destructive-adjacent: task only executes requests where
  `status='requested' AND scheduled_for <= now`; per-row commit isolation;
  idempotent; logs counts; no PII in logs.
- H1: resolve is reversible-in-practice (rows retained, audit-logged).
