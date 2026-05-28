# Technical Debt Register

**Version:** 1.0.0
**Last Reviewed:** 2026-05-28
**Review Cadence:** Monthly

---

## Active Debt Items

| # | Debt | Severity | Owner | Target Date | Impact if Not Addressed |
|:---|:---|:---:|:---|:---|:---|
| 1 | No circuit breaker on Clerk/Stripe API calls | **High** | Backend | 2026-06-15 | Cascade failure under load; auth outages |
| 2 | No background job queue (Celery/arq) | **High** | Backend | 2026-06-15 | Webhooks processed inline; slow checkout |
| 3 | No staging frontend environment | **High** | SRE | 2026-06-01 | Every deploy goes straight to production |
| 4 | No bundle verification in CI | **Medium** | SRE | 2026-06-01 | Bad builds can reach users |
| 5 | No idempotency keys on billing mutations | **Medium** | Backend | 2026-06-15 | Duplicate charges possible |
| 6 | No DB `statement_timeout` | **Medium** | Backend | 2026-06-15 | Slow queries exhaust connection pool |
| 7 | No external observability (Sentry/Datadog) | **Medium** | SRE | 2026-06-30 | Production failures invisible |
| 8 | No customer-facing status page | **Medium** | SRE | 2026-06-30 | No proactive incident communication |
| 9 | Curriculum content not regression-tested | **Low** | Backend | 2026-07-01 | Content changes may break lessons silently |
| 10 | No feature flag system | **Low** | Backend | 2026-07-15 | All features deploy to all users simultaneously |

---

## Resolved Debt Items

| # | Debt | Resolution Date | How Resolved |
|:---|:---|:---|:---|
| 11 | Frontend bundle missing API base URL | 2026-05-28 | Created `.env.production` with `VITE_API_BASE_URL` |
| 12 | Missing help center | 2026-05-28 | Created `HelpPage.tsx` with 4 articles |
| 13 | Concurrent Alembic deadlock | 2026-05-27 | Moved to Fly `release_command` |
| 14 | Missing `numpy` dependency | 2026-05-27 | Added to `requirements.txt` |

---

## ADR Cross-References

- ADR 0024: Database operational policy (addresses #6)
- ADR 0025: Secrets management (addresses operational security)
