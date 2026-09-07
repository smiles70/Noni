# Intake — ADMIN-IA-001: admin console information architecture

**Date:** 2026-09-07 · **Process:** v9.51 · **Trigger:** owner review — console
assumes orgs already exist; no onboarding UI; no landing-level signal

## Current-state inventory (verified from source)

### Screens
- `/admin` — single page: staff login card → staff console
  (org search + flags list + sign out). Org detail is read-only fetch.
- `/org` — OrgDashboardPage: aggregate-only org dashboard (org admin view).
- All other routes are learner-facing (landing, signin, curriculum,
  paywall, account, etc.) — out of scope for the staff console.

### Staff-relevant API surface
- `admin`: whoami, whoami-check, orgs search, org detail, accounts
  search, flags, login
- `organizations` (staff-gated): org/create, org/{id}/license,
  org/{license_id}/codes, org/{id}/usage, org/redeem, org/{id}/slug,
  org/{id}/dashboard, org/by-slug/{slug} (public)

### Gap (observed by owner)
- No "create org" affordance → console dead-ends when zero orgs exist.
- No landing-level operational signal (counts, expiring licenses,
  pending flags, recent audit) → search is the only entry point.
- No navigation model — single flat page; will not scale past a few
  staff tasks.

## Research protocol
≥10 verifiable published sources on enterprise admin-console IA,
B2B customer onboarding tooling, and ops-dashboard design. Log below.

## Research log — 12 verified published sources

**Internal-tools / admin-IA canon:**
1. GOV.UK Service Manual — "Services for government users": internal services held to the same standard as public ones; admin users repeat and switch tasks quickly → not one-thing-per-page.
   https://www.gov.uk/service-manual/design/services-for-government-users
2. DWP Design System — "Designing data interfaces": do NOT render database rows as screens; design around staff *tasks*; climb raw-data → information → actionable-information.
   https://design-system.dwp.gov.uk/research/data-interfaces
3. Chris Armstrong (Home Office interaction designer) — caseworker systems still use the design system; multi-input task pages are fine for internal tools.
   https://chrisarmstrong.io/Designing-Internal-Services/
4. NN/g — Dashboards are for at-a-glance operational signal, not exploration; portals are the task gateway. Distinct artifacts.
   https://www.nngroup.com/articles/dashboards-preattentive/
5. NN/g — Intranet IA/Navigation report: role-based organization, clear labels, breadcrumbs.
   https://www.nngroup.com/reports/intranet-information-architecture-navigation/

**SaaS admin-console patterns (industry exemplars):**
6. AdminLTE/Stripe/Linear breakdown — fixed left sidebar + top bar scales 5→50 menu items; Stripe labels navigation by *user jobs* not data model.
   https://adminlte.io/blog/admin-dashboard-design/
7. Stripe Dashboard teardown — nav = six jobs (Payments, Customers, Reporting…), not system objects; home shows only decision-driving metrics.
   https://www.925studios.co/blog/stripe-dashboard-design-breakdown
8. Multi-tenant dashboard guide — tenant context wraps navigation; role-aware hierarchy.
   https://www.orbix.studio/blogs/multi-tenant-dashboard-design
9. Dashboard patterns 2026 — sidebar nav + restrained KPI strip + aligned tables + skeleton loading.
   https://artofstyleframe.com/blog/dashboard-design-patterns-web-apps/

**LMS admin consoles (domain comparators):**
10. Docebo — branches/sub-branches mirror org structure; Power Users delegate admin; group-based reporting.
    https://help.docebo.com/hc/en-us/articles/360020084140-Organizing-users-with-branches
11. Canvas Admin Guide — admin panel = sub-account tree; analytics at every level; reports are downloadable outputs.
    https://its.gmu.edu/knowledge-base/canvas-admin-guide/

**B2B onboarding practice:**
12. Rocketlane/GUIDEcx — onboarding is a templated, trackable project; portals give customers real-time status; create-once-reuse-forever templates.
    https://www.rocketlane.com/blogs/customer-onboarding-best-practices-guide
    https://www.guidecx.com/blog/how-to-onboard-a-customer/

## Synthesis — what the evidence converges on

A. **Navigation organized by staff jobs, not DB tables** (DWP, Stripe).
   Our jobs: *Onboard an org* · *Find an org* · *Find an account* ·
   *Review flags* · *Check portfolio health*.
B. **A landing that carries operational signal** (NN/g dashboard def.):
   counts + pending work, not exploration.
C. **Multi-step creation needs a guided flow** (onboarding templating),
   because org+license+codes+slug is a 4-step task today done by API.
D. **Sidebar/section nav** so the console can grow (AdminLTE pattern),
   with tenant/org context inside the work area (multi-tenant guide).
E. **Role boundary stays**: staff ≠ learner surfaces; staff ≠ org admin
   (/org dashboard stays the customer-facing aggregate view).

## Deep research round 2 — admin console charter & full-scope gap analysis

### Charter (from repo + owner statements)
The console's purpose: internal employee-only ops for a B2B2C e-learning
platform for adults 55+. Its jobs: onboard organizations (facilities,
communities, nonprofits, health plans), manage licenses/seats/codes,
support accounts, review sharing flags, produce aggregate reporting,
prove auditability — while NEVER exposing per-learner data.

### Additional verified sources (round 2)
13. Yaro Labs — SaaS admin panel canon: account lookup w/ full context,
    role/permission management, account status ops, impersonation
    (high-value, high-risk), seat/license management.
    https://yaro-labs.com/blog/saas-user-management-admin-panel
14. Voxire — internal admin layer = tenant mgmt + impersonation + job
    monitoring + billing ops; warns against bolting admin onto
    customer APIs.
    https://voxire.com/blog/internal-admin-tools-saas-go/
15. Dusko Licanin — year-one admin panel = 5 things: lookup+
    impersonation, subscription inspector, tenant overrides, manual
    billing actions, audit log search.
    https://www.duskolicanin.com/blog/saas-admin-dashboard-that-saves-hours-2026
16. Agnite Studio — audit trail requirements: actor, tenant scope,
    object, action, authz result, export/deletion events, denied
    attempts, tamper resistance, searchability.
    https://agnitestudio.com/blog/audit-trail-requirements-saas-compliance/
17. SOC2 CC6 (AuditFront) — least privilege, RBAC, access reviews,
    segregation of duties.
    https://www.auditfront.com/frameworks/soc-2/common-criteria/cc6-3/
18. WorkOS enterprise-readiness — SSO, SCIM, audit logs, RBAC as the
    enterprise buyer's checklist.
    https://workos.com/blog/enterprise-readiness-checklist-2026
19. CIAM Compass — org-as-contract-unit; per-org audit logs; SCIM hard
    requirement ~1000 seats.
    https://guptadeepak.com/ciam-compass/guides/b2b-saas-identity/
20. ShipSolid checklist — user visibility, billing ops, product/pricing
    mgmt, content ops, status metrics, safe workflows, permission clarity.
    https://shipsolid.heinerdevelops.tech/en/blog/saas-admin-panel-features-checklist

### Gap analysis — console vs charter (verified against source)

P0 — blocks the stated purpose (owner-visible today):
- G1  No org onboarding UI (create/license/codes/slug all API-only)
- G2  No operational landing signal (counts, expiring, pending flags)
- G3  No org contact/location data (address, city/state/zip, phone,
      multiple contacts) — schema gap, needs migration
- G4  Org detail not surfaced in UI (licenses/codes/audit exist API-side)

P1 — charter-level gaps (vs sources 13–20):
- G5  No staff roles beyond binary staff (kim/steven) — SOC2 CC6.3
      expects least-privilege roles; shared password already recorded
      as attribution caveat
- G6  Audit log not searchable/visible in console UI (exists in DB,
      shown only per-org recent entries)
- G7  No account support actions (status, purchase view-only today)
- G8  No billing ops surface (licenses are the billing record until
      Stripe live; manual invoice/PO path exists API-side only)
- G9  No impersonation/view-as — per sources it is the highest-value
      support feature BUT it collides with the privacy boundary;
      recommend explicit defer (staff must never see learner progress)
- G10 No system/job health surface (deploy status, queue, email delivery)
- G11 No notifications/comms tooling (renewal reminders are manual)
- G12 No content-ops surface (curriculum is code-managed; acceptable now)

Deferred-by-design (documented, not forgotten):
- SSO/SCIM — only at ~1000-seat customers (source 19); revisit at scale
- Impersonation — conflicts with learner privacy boundary (G9)
