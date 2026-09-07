# ADMIN-REPORTING-001 — research synthesis (verifiable sources)

## Sources

1. **RevOS — License Utilization Benchmarks** (revos.ai): healthy seat
   utilization 60–85%; <50% = churn risk; >90% = expansion signal.
   "Active user" must be defined once (monthly distinct) and used
   consistently. Account-level, not portfolio-level, surfaces risk.
2. **Yaro Labs — SaaS license utilization dashboards**: signals are
   last-active + feature-depth; last-login alone is a floor, not a ceiling.
3. **Dusko Licanin — SaaS admin panels**: read-first by default, audit
   every mutation, roles in middleware — matches our require_admin split.
4. **Orbix — admin dashboard IA**: group nav by user goal not data type;
   permission flags not role names (our `canWrite` pattern aligns).
5. **AdminLTE — dashboard design**: distinguish operational vs analytical
   surfaces; every analytical number needs a comparison/baseline, bare
   figures are decoration.
6. **FPF — PETs for EdTech providers** (fpf.org): aggregate reporting and
   small-group protection — small cohorts can inadvertently reveal
   individual outcomes; keep learner-level detail out of staff views.
7. **App-Learning — data hygiene in learning design**: test-user
   separation, explicit definitions for "active learner"/"completion".
8. **Edilec — admin dashboard governance**: written data contract per
   metric — definition, cadence, lineage; label provisional data.
9. **Respectlytics — GDPR/LMS analytics**: data minimization — collect and
   expose only what's needed for the decision at hand.
10. **LMSPedia — GDPR for LMS**: every learning event carries obligations;
    aggregate institutional reporting is the accepted pattern.

## Design decisions from research

- **D1** Report definition is explicit: "active learner" = claimed seat
  with ≥1 progress row whose first_started_at or completed_at falls in
  the window. Documented on the report card itself (data contract, S8).
- **D2** Analytical surface → every metric carries context: utilization %
  with healthy-band framing (60–85%, S1), counts over a named window.
- **D3** Aggregate-only (S6, S9, S10): counts and timestamps per org;
  never learner names, unit rows, or confidence. Small orgs show the
  same aggregates — no per-learner breakout ever.
- **D4** Nav by goal (S4): "Reports" is a first-class nav item, not a
  button hidden inside another view.
- **D5** Reads stay `require_staff`; no new mutation verbs.
- **D6** CSV export retained as a secondary artifact, not the interface.

## KG/ontology mapping (v9.51)

- Capability: `b2b-activity-reporting` — evidenced_by `/admin/reports/org-activity`
- Gap closed: "reporting undiscoverable / not a feature"
- Acceptance: nav item present; report runs per-org or all-orgs in a
  named window; aggregate-only response verified by test; support role
  can read, mutation role unaffected.
