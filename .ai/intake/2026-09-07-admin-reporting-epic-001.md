# ADMIN-REPORTING-001 — B2B customer activity reporting surface

## Ask

> "reporting should be a feature on the admin console menu and allow us
> to run reports against all critical B2B customer activities at the
> account level."

CSV downloads (E4) exist but are buttons, not a feature. The ask is a
first-class Reporting surface: interactive, filterable, org/account-level
rollup of B2B customer activity.

## Constraints (carried, non-negotiable)

- **Privacy boundary**: aggregate-only org rollups. No individual learner
  names, progress rows, or confidence values — the org→learner link is
  `access_codes.claimed_by_account_id` (claimed seat = enrolled learner).
- **Staff-gated**: `require_staff` for reads (consistent with overview/
  audit/exports). Any mutation stays `require_admin`.
- **Audit-visible**: report runs may be audit-logged (staff accountability).
- **Geragogy calm**: staff tools are utilitarian; no dark-pattern urgency.
- CSV remains as an export artifact, not the primary interface.

## Candidate report surfaces (to confirm via research)

1. Org activity rollup: seats/utilization, codes issued/claimed in window,
   learners enrolled, active learners, units completed, last activity.
2. Audit/ops events per org in a window.
3. Export-to-CSV retained as secondary.

## Ontology targets (v9.51)

- Capability: B2B activity reporting
- Gap closed: "reporting not linked / undiscoverable" (observed UX gap)
- Epic: ADMIN-REPORTING-001, parent ADMIN-OPS-001
