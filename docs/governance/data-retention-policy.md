# Data Retention Policy

**Version:** 1.0.0
**Effective Date:** 2026-05-28
**Owner:** Engineering

---

## Default Retention

All telemetry data is retained for **90 days** by default unless a specific schedule applies.

---

## Per-Event-Type Retention Schedule

| Event Type Prefix | Retention | Rationale |
|:---|:---|:---|
| `iscs_decision` | 90 days | ISCS audit trail for estimator tuning |
| `iscs_recommendation` | 90 days | ISCS audit trail |
| `envelope_served` | 30 days | UI envelope access logs |
| `unit_view` | 90 days | Curriculum engagement metrics |
| `purchase_` | 365 days | Billing audit and refund support |
| `auth_` | 30 days | Auth security logs |
| `gift_` | 365 days | Gift token redemption audit |
| `deletion_` | 730 days | Legal compliance for deletion requests |

---

## Automated Enforcement

Retention is enforced by `pg_cron` job defined in `supabase/migrations/0002_pg_cron_retention.sql`:

- **Frequency:** Nightly at 02:00 UTC
- **Mechanism:** `DELETE FROM telemetry_events WHERE expires_at < NOW()`
- **Logging:** Deleted row count logged to application logs

---

## Manual Deletion

For GDPR deletion requests:

1. User initiates deletion via `POST /me/delete`
2. 7-day grace period allows cancellation via `POST /me/delete/cancel`
3. After grace period, account and all associated data are deleted
4. Deletion is logged as `deletion_executed` event

---

## Backup Retention

| Backup Type | Frequency | Retention | Location |
|:---|:---|:---|:---|
| Database dump | Daily | 30 days | Cloudflare R2 |
| Restore drill artifact | Quarterly | 1 year | `docs/operations/` |

---

## Policy Review

This policy is reviewed **annually** or after any significant data incident.
