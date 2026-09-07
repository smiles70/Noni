# Adapted Spec — B2B Onboarding & Org Dashboard (Mynaani)

**Date:** 2026-09-06 · **Status:** adapted, not executed · **Source:** generic Python/Railway
e-learning onboarding spec, rewritten against verified repo state.
**Rubric link:** closes TRUST_PRIVACY_RUBRIC_001 item #8 (org visibility → 9).
**Gate:** staging only; `main` requires owner approval.

---

## Verified baseline (already built — do not re-spec as "missing")

| Capability | Evidence | Status |
|---|---|---|
| Org model | `Organization` + `OrgLicense` + `AccessCode` (`models/organizations.py`) | ✅ exists, **flat** (no parent_id) |
| Passwordless auth | `MagicAuthProvider` (`services/auth_provider.py`), DID-token | ✅ ideal for 55+; no SSO work needed now |
| Payment path | Stripe Checkout + `processed_webhook_events` dedup + queued processing | ✅ idempotent — but `PAYMENT_PROVIDER=mock` on staging |
| Org rate fairness | `services/org_quota.py`, per-org token bucket | ✅ shipped (PR #41) |
| Account deletion | `services/deletion.py` + `POST /me/delete`/`cancel`/`export` | ✅ shipped (PR #43), 30-day grace |
| Telemetry allowlist | server-side on `/signals/telemetry` | ✅ shipped |
| Trust surfaces | `/privacy` (sub-processors, DPA path), `security.txt`, `/help` channels | ✅ live |
| Privacy boundary | orgs see code-claim booleans only — enforced in `organizations.py` | ✅ code-enforced, now documented |

## Genuinely absent (the spec's real scope)

1. **Org hierarchy** — no `parent_org_id`; multi-site/150+/health-plan tier can't be modeled today
2. **Tier capture** — no `org_type` (nonprofit/for-profit), `community_size`, `tier` fields on `Organization`
3. **Org admin dashboard** — the #8 feature: staff see only "code used" booleans; no aggregate view, no seat management, no renewal surface
4. **License lifecycle** — `OrgLicense` has seats but no expiry enforcement, no renewal reminders, no de-provisioning path
5. **Invoice/PO path** — Stripe card checkout only; no manual-invoice flow for nonprofits
6. **Audit trail for org/billing mutations** — `deletion_requests` + `processed_webhook_events` cover those flows; **license grants/tier changes are unlogged**
7. **Seat-drift handling** — overage is a policy decision, currently undefined

## Adapted build sequence (reuse-first)

| Block | Work | Size | Rubric |
|---|---|---|---|
| OB-1 | `Organization` schema: `org_type`, `community_size`, `parent_org_id`, `custom_flag`, `tier` | M | enables #8 |
| OB-2 | Org admin dashboard (read-only): seats, codes issued/claimed, aggregate engagement — **aggregate-only, the visibility boundary IS the feature** | M-L | #8 →9 |
| OB-3 | License lifecycle: `expires_at`, renewal reminder (Celery beat exists), soft-deprovision on expiry | M | trust pack |
| OB-4 | Invoice/PO manual-provisioning path (staff-side, key into existing `OrgLicense`) | M | enables nonprofit sales |
| OB-5 | Audit log for org/billing mutations (who granted, who changed tier, who impersonated) | M | enterprise gate |
| OB-6 | Portfolio (parent/child) permission model — portfolio admin sees aggregates across children; child admins isolated | M-L | health-plan gate |

## Explicit non-goals (over-engineering call-outs)

- ❌ Google Workspace SSO / SAML — passwordless email already fits this audience
- ❌ Full proration engine — flat mid-year tier upgrade, manual adjustment
- ❌ Per-tenant dedicated instances — shared multi-tenant + `org_quota` already provides isolation
- ❌ Automated seat-drift hard-block — soft warning + sales follow-up
- ❌ HIPAA self-certification — health-plan sales require **legal sign-off**, not engineering claims

## Decisions requiring human sign-off (cannot be inferred from code)

- Pricing enforcement behavior when a 25-seat org grows to 40 (soft warn vs. block vs. sales call)
- Invoice/PO payment terms and who keys them
- Whether `expires_at` hard-locks or soft-locks lapsed orgs
- HIPAA-adjacent exposure for health-plan tier (named-resident completion data)

## Executive summary (≤10 bullets)

- The org/code model is **already 70% built** — we're extending, not starting
- The trust/privacy layer shipped this week is the foundation the dashboard sits on
- The biggest real work is **OB-1 schema + OB-2 dashboard** — one epic
- Health-plan/enterprise tier is a **legal gate**, not an engineering one
- No new third-party services needed — everything reuses Stripe/Magic/Railway
- **Don't build SSO or proration** — wrong audience, wrong stage
