# Data Classification Policy

**Version:** 1.0.0
**Effective Date:** 2026-05-28
**Owner:** Engineering / Legal

---

## Classification Levels

| Level | Definition | Examples |
|:---|:---|:---|
| **Public** | Information intended for public access | Landing page copy, curriculum content, pricing |
| **Internal** | Operational data, not customer-facing | Deployment configs, build logs, telemetry aggregates |
| **Confidential** | Customer data, requires protection | Learner progress, account emails, purchase history |
| **Restricted** | High-sensitivity, regulated data | Auth tokens (transient), raw telemetry with PII |

---

## Data Types by Classification

| Data Type | Classification | Storage | Retention |
|:---|:---|:---|:---|
| Curriculum content | Public | Supabase `units` | Indefinite |
| Learner account (email, auth_user_id) | Confidential | Supabase `accounts` | Until deletion |
| Learner progress | Confidential | Supabase `progress` | Until deletion |
| Purchase records | Confidential | Supabase `purchases` | 7 years (tax) |
| Telemetry events | Restricted | Supabase `telemetry_events` | 90 days default |
| Gift tokens | Confidential | Supabase `gift_tokens` | Until redeemed + 365d |
| Deletion requests | Restricted | Supabase `deletion_requests` | 730 days |
| API error logs | Internal | Fly.io logs / BetterStack | 30 days |
| Stripe webhooks | Confidential | Supabase `processed_webhook_events` | 365 days |

---

## Handling Requirements

| Level | Encryption at Rest | Encryption in Transit | Access Control |
|:---|:---:|:---:|:---|
| Public | Optional | Required | Public |
| Internal | Required | Required | Employee-only |
| Confidential | Required (AES-256) | Required (TLS 1.3) | RLS + application auth |
| Restricted | Required (AES-256) | Required (TLS 1.3) | RLS + application auth + admin only |

---

## PII Inventory

| PII Field | Location | Purpose | Deletion |
|:---|:---|:---|:---:|
| Email address | `accounts.email` | Identity, communication | On account deletion |
| Auth provider ID | `accounts.auth_user_id` | Clerk user linkage | On account deletion |
| IP address | `telemetry_events.client_ip` | Rate limiting, security | After 90 days |
| User agent | `telemetry_events.user_agent` | Debugging | After 90 days |

---

## Compliance Mapping

| Regulation | Requirement | Implementation |
|:---|:---|:---|
| GDPR Article 5 | Data minimization | 90-day default telemetry retention |
| GDPR Article 17 | Right to erasure | `/me/delete` endpoint with 7-day grace |
| GDPR Article 32 | Security of processing | TLS + RLS + AES-256 |
| SOC 2 CC6.1 | Logical access controls | RLS on all customer tables |
