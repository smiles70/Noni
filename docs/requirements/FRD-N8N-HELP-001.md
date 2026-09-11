# Functional Requirements Document (FRD) — n8n Help Flow

**Document ID:** FRD-N8N-HELP-001  
**Version:** 1.1  
**Date:** 2026-09-11  
**Status:** Draft — re-assessed for path-gated caregiver / facility scope  
**Source:** `.ai/intake/2026-09-11-n8n-help-flow-intake-001.md`

---

## 1. Scope

Defines what the n8n-powered help widget must do for caregivers, facility staff, support agents, and the system. The widget is intentionally **not** available to the main consumer learner.

## 2. Functional requirements

| ID | Requirement | Priority | Acceptance criteria |
|---|---|---|---|
| FR-001 | Render `HelpRequestWidget` only on allowed routes: `/gift`, `/for-communities`, `/org`, `/c/:slug` | High | Widget absent from `/`, `/help`, `/curriculum`, `/paywall`, `/account`, `/menu`, `/welcome`, `/signin`, `/gift-redeem`, `/purchase/success`, `/purchase/cancel`. E2E passes. |
| FR-002 | Display context-aware form: caregiver categories on `/gift`; facility categories on facility routes | High | Categories match `context` prop and route; backend validates the pair. |
| FR-003 | Provide a context-aware trigger label (e.g., "Questions about gifting?" / "Community support") | High | Label is calm, non-urgent, no exclamation marks. |
| FR-004 | Backend `POST /api/v1/help/requests` accepts `context` (`caregiver` \| `facility`) and a `category` valid for that context | High | Mismatched `context`/`category` returns 422. |
| FR-005 | Pre-fill `reply_email` for authenticated facility staff; caregiver may enter any valid email | High | Auth optional; when authenticated, email is pre-filled and disabled. |
| FR-006 | Persist support request to a new `support_requests` table including `context`, `category`, `sub_category`, `message`, `reply_email`, `status` | High | Row created with all required fields. |
| FR-007 | Enqueue async webhook call to n8n with `context` and `category` | High | Request returns 202; webhook delivered or retried. |
| FR-008 | Implement per-IP and per-email rate limiting per context | High | >5 submissions per 15 minutes returns a calm rate-limit message. |
| FR-009 | Provide admin endpoint to list and update support request status, filtered by `context` | Medium | `GET/PUT /api/v1/admin/help/requests` behind `require_staff`. |
| FR-010 | Write an audit row for every status change and webhook attempt | Medium | `support_request_audit` table records actor, timestamp, old/new status. |
| FR-011 | Expose `FEATURE_HELP_REQUESTS` env flag to disable all help widgets in an emergency | Medium | Flag off hides every widget and returns 404 on POST. |

## 3. User flows

### 3.1 Caregiver submits request from `/gift`

1. Caregiver visits `/gift` to buy a gift.
2. Caregiver sees "Questions about gifting?" trigger (calm, non-urgent).
3. Caregiver opens widget and selects a category such as "Payment issue".
4. Caregiver enters message and email.
5. System validates `context=caregiver` + category, stores request, enqueues webhook.
6. System shows confirmation with expected SLA.
7. n8n routes to caregiver support channel and sends auto-acknowledgment.

### 3.2 Facility staff submits request from `/for-communities` or `/org`

1. Facility staff visits `/for-communities` or signs in to `/org`.
2. Facility staff sees "Community support" or "Facility support" trigger.
3. Facility staff opens widget and selects a category such as "Licensing and seats".
4. Facility staff enters message and email (pre-filled if signed in).
5. System validates `context=facility` + category, stores request, enqueues webhook.
6. System confirms; n8n routes to facility/B2B support channel.

### 3.3 Support agent triage

1. Support agent receives n8n-routed ticket in the appropriate caregiver or facility channel.
2. Agent opens admin endpoint and filters by `context` and status.
3. Agent updates status or adds internal note.
4. System writes audit row.

## 4. Data requirements

- New table: `support_requests`
  - `id` UUID PK
  - `account_id` UUID nullable FK to `accounts.id`
  - `context` VARCHAR(16) not null — `caregiver` or `facility`
  - `category` VARCHAR(64) not null
  - `sub_category` VARCHAR(64) nullable
  - `message` TEXT not null
  - `reply_email` CITEXT not null
  - `status` VARCHAR(32) default `submitted`
  - `severity` VARCHAR(8) nullable
  - `n8n_status` VARCHAR(32) default `pending`
  - `n8n_retry_count` INT default 0
  - `client_ip` INET nullable
  - `created_at`, `updated_at` timestamps
  - Unique/constraint: `category` must be in allowed set for `context`.
- New table: `support_request_audit`
  - `id` UUID PK
  - `support_request_id` UUID FK
  - `actor` VARCHAR(64)
  - `old_status`, `new_status`
  - `note` TEXT
  - `created_at`

## 5. Category sets by context

### Caregiver (`context=caregiver`)

- `buying_gift`
- `payment_issue`
- `gift_not_received`
- `redeeming_gift`
- `managing_recipient_access`
- `something_else`

### Facility (`context=facility`)

- `partnership_inquiry`
- `licensing_and_seats`
- `onboarding_staff`
- `technical_setup`
- `billing_and_invoice`
- `existing_account_issue`
- `something_else`

## 6. Interface requirements

- `HelpRequestWidget.tsx` must be RenderGuard-compliant.
- Trigger label must be specific to the page (not a generic floating "Help" bubble).
- Copy must be calm: "We will read your message and reply to [email]."
- Errors: "Please check the highlighted field and try again."
- Success: "We received your message. We usually reply within [SLA]."

## 7. Related documents

- USECASE-N8N-HELP-001
- BRD-N8N-HELP-001
- PRD-N8N-HELP-001
- `.ai/research/2026-09-11-n8n-help-flow-research.md`
