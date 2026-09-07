# TRUST_PRIVACY_RUBRIC_001 — Audience Security/Privacy Scoring

**Date:** 2026-09-06 · **Process:** v9.51 · **Sources:** FTC Protecting Older Consumers 2024-25;
Pew Research (2019, 2023, 2025); AARP Tech Trends 50+ (2024, 2025); arXiv 2410.08555
(e-payment, n=400, 60+); Springer Security Journal (fear-of-fraud); AIS SIGHCI phishing study.

**Scoring rule:** 0–10 per concern, scored on *deployed/verifiable code*, not intent.
A gap that exists in code counts against the score even when a fix is planned.

---

## Rubric (what the audience fears, in data order)

| # | Concern (weight = audience salience) | Evidence anchor |
|---|---|---|
| 1 | Fraud/scam exposure when transacting | FTC: $2.4B reported losses by 60+, 2024 |
| 2 | Payment/credential interception | arXiv e-payment study: top adoption barrier |
| 3 | Data privacy / silent tracking | AARP 2025: #1 barrier (29%); Pew: 81% no control |
| 4 | Identity theft via collected PII | FTC Sentinel: 1.1M reports |
| 5 | Password burden / credential reuse | Pew 2023; password reuse = documented vector |
| 6 | Phishing / "is this link or site real" | AIS: elevated susceptibility 60+ |
| 7 | Post-signup transparency (what happens next) | Pew: only 39% of 65+ click-agree blindly |
| 8 | Who can see my data (peers, family, org) | Springer: social visibility compounds fear |
| 9 | Lockout / losing account access | arXiv: 91% prefer simple single-mode auth |
| 10 | No human help when stuck | AARP 2025: support is an adoption lever |

## Scores (triple-checked against code 2026-09-06)

| # | Score | What exists today | Gap |
|---|---|---|---|
| 1 | **9** ⬆ | Org learners redeem AccessCodes — never see checkout; paywall states we never email/call asking for payment + `checkout.stripe.com` address cue (PR #43); one-time price, no recurring-billing trick | — |
| 2 | **7** | Stripe-hosted checkout — card data never reaches our DB; webhook queue is idempotent | PAYMENT_PROVIDER=mock on staging; live activation is an open intake item |
| 3 | **9** ⬆ | Canonical tested React `/privacy` live + linked from `/help`; server-side event-name allowlist now enforces `/signals/telemetry` (unknown types soft-drop `accepted:false`, verified live); contract synced to real emitted events | — |
| 4 | **9** ⬆ | `POST /me/delete` (202 + `scheduled_for`, verified live), `delete/cancel`, `GET /me/export` all implemented; tombstone gate + hashed IDs; grace aligned 7→30 to match published copy | — |
| 5 | **10** | Magic.link — zero passwords exist anywhere in the system | — |
| 6 | **9** ⬆ | Magic-link sender-domain recognition copy on `/signin` + `/help` (PR #42); org-code-first framing on `/for-communities` (PR #44) — B2B learners bypass email trust entirely | — |
| 7 | **8** ⬆ | Post-purchase reassurance on mock-checkout (what you bought, where to go next, email receipt); `/privacy` states exactly what's kept; calm single-payment copy on `/paywall` | Real Stripe post-purchase email unverified until live keys |
| 8 | **9** ⬆ | Boundary enforced in code AND inspectable: `/org` staff dashboard is aggregate-only by design (seats/codes/expiry/audit — no per-learner fields); policy published on `/privacy` + `/for-communities`; portfolio children see aggregates only | — |
| 9 | **9** ⬆ | 30-min idle signout confirmed in code (`AuthProvider` elapsed check); shared-device guidance live on `/help` (PR #42) | — |
| 10 | **9** ⬆ | Tiered published commitment grounded in solo-SaaS SLA research: learners two business days (`/help`); **program partners one business day, urgent same business day** (`/for-communities`, PR #46); `security.txt` security contact; a person answers — no ticket portal | Owner commitment: inbox checked daily |

**Total: 62/100** at intake → **88/100** post-merge (PRs #42–#46: privacy surface, legitimacy cues, /me delete+export, server telemetry allowlist, trust-hub docs, org schema+audit+dashboard, partner SLA)

**Rescore 2026-09-07 (post AC-1 #53 + AC-2 #54, staging-verified): 88/100 — unchanged.**
Verified on staging: `/health` 200; `/api/v1/admin/whoami` anonymously 401; org
service endpoints live. AC-1/AC-2 are staff-support surfaces — `require_staff`
allowlist enforced on every admin route, org/admin reads are aggregate-only or
support metadata; no new learner-facing exposure was introduced and no existing
control weakened. Concern #8's structural boundary (aggregate-only, k-anonymity
floor) is now shared by both routers via `services/organizations.py`.

Remaining: #2 Stripe live keys (owner action, +2). **90 is the self-serve ceiling** — every point beyond it requires third-party attestation (pen-test, SOC 2) which by definition cannot be claimed in code.

## Gap analysis → path to 10/10

| # | To reach 10 | Effort |
|---|---|---|
| 1 | Org-code path covers B2B; for B2C add "verify this site" anti-scam guidance at checkout (domain shown, no urgency language) | S |
| 2 | Complete live Stripe activation intake (exists: `.ai/intake/2026-08-29-stripe-live-readiness-intake.md`) | M — owner-side keys |
| 3 | Publish a `/privacy` page: what we collect (milestones), what we never collect (browsing, contacts, location), retention period, plain language at 6th-grade reading level | S |
| 4 | Implement `/me/delete` (already a failing spec-forward test) + data-export; this also clears residual R-items | M |
| 5 | Done — hold the line: never add a password field | — |
| 6 | Add "How to recognize our sign-in email" guidance on `/signin` + `/help`; sender-domain callout; optionally phrase magic link as "sign-in link" not "click here" | S |
| 7 | `/privacy` + a one-line post-checkout "what happens next" card | S |
| 8 | Publish an org-visibility policy: admins see cohort aggregates, never individual activity; reflect it in the (future) org dashboard design | M |
| 9 | Document shared-device sign-in story; verify session persistence semantics; add "sign in on a different device" help entry | S |
| 10 | Surface the human channel: org contact on /help for B2B learners; support email for B2C; response-time expectation | S |

**Sequence to 100:** the five "S" items (1, 3, 6, 7, 9, 10) are content/copy — one PR.
The two "M" items (2 Stripe live, 4 `/me/delete`+export) are existing backlog items this
rubric now justifies prioritizing. #8 depends on the org-dashboard feature existing.

**Closeout:** rescore after the S-PR lands (~75) and after Stripe-live + deletion (~90);
#8 and full-10 require the org dashboard milestone.
