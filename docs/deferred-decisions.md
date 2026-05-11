# Deferred Decisions

Durable, version-controlled record of decisions explicitly held for later.

## Status

Active. Reviewed at the start of each future "Vendor Selection Pass" sprint.

## Bundle: 3rd-Party Integration & Vendor Selection (was Sprints 6 + 7)

Deferring all third-party / vendor decisions to a single dedicated pass so they can be evaluated holistically (cost, SOC2/HIPAA, data residency, vendor lock-in, free tiers, support quality) instead of piecemeal.

### Items in this bundle

| Item | Originally planned in | Notes |
|---|---|---|
| Authentication provider | Sprint 6 | Options surveyed: self-hosted FastAPI Users + JWT; Auth0; Clerk; magic-link self-hosted. |
| Per-learner state model | Sprint 6 | Anonymous-session approach drafted (users / sessions / learner_progress tables, X-Noni-Session-Id header). Implementation deferred until auth choice is made; the user model converges. |
| Anthropic API key + real Claude | Sprint 7 | Mock `claude_engine` keeps working. Plan: USE_REAL_CLAUDE feature flag, default off. |
| Email provider | Likely needed alongside auth | Postmark / SES / Resend / Mailgun. Needed for magic-link, password reset, transactional email. |
| Observability / error tracking | Future | Sentry / Datadog / Honeycomb / OpenTelemetry-only. |
| Production hosting | Future | Render / Fly.io / Railway / AWS / GCP / Azure / Vercel (FE only). |
| Database hosting | Future | Managed Postgres (Supabase / Neon / RDS / Cloud SQL). |
| Frontend deploy + CDN | Future | Vercel / Netlify / Cloudflare Pages / S3+CloudFront. |
| Payment processor (if/when monetized) | Future | Stripe / Paddle / Lemon Squeezy. |

### Why deferring

- Avoids piecemeal integration creating tech debt
- Some vendors overlap (Auth0 also offers email; Cloudflare offers hosting + observability)
- Makes a single procurement / accounts pass possible
- Keeps the codebase focused on patentable / proprietary work (ISCS, geragogy, curriculum) until a runway/launch decision firms up

### What is in place that already works without these decisions

- Mock Claude engine (`backend/core/claude_engine.py`)
- Module-level ISCS estimator (effectively a single shared "user", fine for solo dev)
- Anonymous backend (no login required)
- Local Postgres via Docker Compose
- Tests and CI workflow file (CI fires when the repo gets a remote)

### Trigger to revisit

Any of the following should pull this bundle off the deferred list:
- Decision to begin pilot user testing with real older adults
- Investor / funder request for a deployable demo with real Claude
- IRB submission requiring per-learner data attribution
- Patent filing scheduled (real per-session telemetry strengthens claims)

## Module 2 enforcement (added in Sprint 17)

- Module 2 units declare `telemetry_requirements` (volatility_max, strain_max, mastery_min). Enforcement requires per-learner state, which requires the auth vendor decision. Until then the values are recorded in audit telemetry per ADR 0009 / 0015.

## Claude Skills creation flow (added in Sprint 19)

- Module 4 (`/api/curriculum/module-4/...`) lands the *declarative* content about Claude Skills. The *interactive Skill-creation flow* (wizard UI, Anthropic API calls, per-Skill persistence, review/edit cycle) requires the Claude API vendor decision AND the auth vendor decision (per-Skill ownership). Both are tracked above.
