# ADMIN-OPS-001 — external research digest (lifecycle operations)

20 verifiable sources informing the "can't-do" epic. Full digest held in
subagent transcript; key mappings:

## Sources
- Stripe — Modify Subscriptions (docs.stripe.com/billing/subscriptions/change)
- Chargebee — Subscriptions API (apidocs.chargebee.com/docs/api/subscriptions)
- Paddle — SaaS Subscription Lifecycle (developer.paddle.com)
- 10Duke — Provision a Subscription License (docs.enterprise.10duke.com)
- Keygen — License Lifecycle API (keygen.sh/docs/api/licenses)
- ISO 27001:2022 A.5.16/A.5.18 — identity lifecycle (upguard.com interpretation)
- SOC 2 CC6.3 — remove access when appropriate (compliancebase.org)
- AppMaster — SaaS offboarding: export→revoke→delete
- Coggno — LMS buyers guide, compliance priorities (2026)
- AccountableHQ — HIPAA-compliant LMS checklist
- TouchClass/LMSPedia — LMS RFP data-export expectations
- NIST SP 800-53 AC-3(7) — RBAC
- OWASP — Forgot Password cheat sheet
- Auth0 — RBAC permission/role model
- Okta — Custom admin roles / resource sets
- Recurly — account hierarchy & invoice rollup
- CoreLine — enterprise entitlements & account hierarchies
- Keycloak — multi-tenancy with organizations

## Design principles mapped to Noni
1. Seats = line items on ONE license record: edit in place (extend
   seats/expiry), never cancel+recreate (Stripe, Chargebee, Paddle).
2. Discrete idempotent lifecycle verbs: suspend / reinstate / renew /
   revoke — not a generic "edit" (Keygen).
3. Soft-first deprovisioning: suspend → retain → delete only after an
   export window; export→revoke→delete order (SOC2 CC6.3, AppMaster,
   Okta `active=false`).
4. Never cascade suspension parent→children by default; prompt for
   scope (Recurly hierarchy).
5. Reports are audit artifacts: CSV + immutable UTC-stamped audit
   export; default aggregate-only, individual drill-down needs a
   higher logged role (Coggno, AccountableHQ).
6. RBAC = roles + resource sets enforced at API layer, never attached
   to users directly (NIST AC-3(7), Auth0, Okta).
7. Async exports with generated-at + data-as-of timestamps; hash the
   audit export for tamper evidence.
8. Parent/child orgs: per-child privacy boundaries, consolidated
   rollup at parent, dedupe learners across sites.

## Edge cases adopted into the epic
- Seat decrease below assigned learners → require deprovisioning rule
  (last-invited-first-out / longest-inactive / manual) + confirmation.
- Concurrent license edits → optimistic locking / one in-flight edit.
- Suspend must revoke live sessions + tokens immediately.
- Reactivation stores pre-suspension seat count and restores exactly.
- Legal/audit hold blocks deletion; keep minimum records.
- Export PII guard: default institutional summary contains counts only.
- UTC + ISO-8601 everywhere; timezone label in exports.

## Checklist (all epic work)
- [ ] In-place license edit w/ audit event
- [ ] suspend/reinstate/renew/revoke as distinct verbs
- [ ] session+token revocation on suspend
- [ ] soft-first deactivation w/ retention window
- [ ] RBAC roles scoped, enforced at API
- [ ] exports aggregate-first, async, UTC-stamped, tamper-evident
- [ ] parent/child rollup w/ dedupe + per-site privacy boundary
- [ ] every mutation → immutable audit log
