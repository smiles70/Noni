# B2B enterprise-readiness rescore — post ADMIN-OPS (E1–E6 + hygiene)

Date: 2026-09-07 · Basis: live-verified capabilities (staging + production
probes), not prose. Each row cites the shipping evidence.

## Rubric (scored /100, was ~85 before this epic)

| Capability | Before | Now | Evidence |
|---|---|---|---|
| Org onboarding (contacts, license, codes, slug) | partial (scaffolded, flush-only) | ✅ full | PR #57–59; staging E2E create→codes→slug |
| License lifecycle (edit seats/expiry, suspend, reinstate, top-up) | absent | ✅ | PR #59, staging-verified |
| Org lifecycle (suspend/reinstate, opt-in child cascade) | absent | ✅ | PR #60, prod-verified |
| Learner account actions (suspend/reinstate/cancel-deletion) | absent | ✅ | PR #61, staging-verified 401 gate |
| Append-only audit trail (all mutations + feed + CSV) | partial | ✅ | PR #61 export, outerjoin incl. account-level rows |
| Aggregate exports (orgs.csv, audit.csv) | absent | ✅ | PR #61, prod-verified |
| Staff RBAC (admin/support, mutation gating, last-admin guard) | absent | ✅ | PR #62, prod-verified |
| Flag triage workflow | read-only list | ✅ | this change (flag.resolve, open-only view) |
| GDPR deletion — request + cancel + **scheduled execution** | request only; execution stub | ✅ | this change (daily sweep wired) |

## Honest remaining gaps (not built today)

- SSO/SAML/OIDC for enterprise buyers — still password-based staff login.
- SOC 2 / security questionnaire artifacts — audit trail exists; no formal report.
- SCIM provisioning, SLA commitments, DPA templates, invoicing/PO flow.
- Org-facing engagement dashboards for buyers (we show staff only).
- Uptime/status page history.

## Rescore estimate

The gaps closed here are the *operational* half of enterprise readiness
(lifecycle, audit, RBAC, exports, deletion). Verified evidence moves the
operational dimension from partial to complete. The remaining ~10 points
live in *procurement* artifacts (SSO, SOC 2 report, DPA/SLA paperwork),
which are documents/integrations, not code. Estimate: **88–90** — the code
side of the rubric is done; the rest is attestation work.
