# Use Case Document — n8n Help Flow

**Document ID:** USECASE-N8N-HELP-001  
**Version:** 1.1  
**Date:** 2026-09-11  
**Status:** Draft — re-assessed for path-gated caregiver / facility scope  
**Source:** `.ai/intake/2026-09-11-n8n-help-flow-intake-001.md`

---

## 1. Actors

| Actor | Description |
|-------|-------------|
| Caregiver | A family member or friend purchasing or managing a mynaani gift for a learner. Reaches the help widget from `/gift` or related caregiver surfaces. |
| Facility staff | Adult day, assisted living, senior center, or similar staff using the B2B `/for-communities`, `/org`, or `/c/:slug` surfaces. |
| Support agent | Human reviewing and responding to help requests, grouped by persona. |
| n8n automation | Receives webhook, validates context, routes to caregiver or facility support channel, auto-acknowledges. |
| System | Mynaani backend, database, queue, audit logger. |

## 2. Use cases

### UC-001 — Caregiver submits a help request

**Trigger:** Caregiver is on `/gift` and has a question or problem.  
**Precondition:** User is on an allowed caregiver path; the `HelpRequestWidget` is rendered with `context="caregiver"`.  
**Postcondition:** Request is persisted with `context=caregiver`; n8n is notified; caregiver sees a calm confirmation.

**Steps:**

1. Caregiver selects a context-aware trigger such as "Questions about gifting?".
2. System opens the help widget with caregiver categories.
3. Caregiver chooses a category: "Buying a gift", "Payment issue", "Gift not received", "Redeeming a gift", "Managing recipient access", or "Something else".
4. Caregiver enters a message in plain language.
5. Caregiver provides or confirms an email address for reply.
6. Caregiver submits the form.
7. System validates input, rate-limits, stores the request, enqueues webhook call.
8. System displays confirmation: "We received your message. We will reply to [email] within [SLA]."

### UC-002 — Facility staff submits a help request

**Trigger:** Facility staff is on `/for-communities`, `/org`, or `/c/:slug` and needs help.  
**Precondition:** User is on an allowed facility path; the `HelpRequestWidget` is rendered with `context="facility"`.  
**Postcondition:** Request is persisted with `context=facility`; n8n is notified; staff member sees a calm confirmation.

**Steps:**

1. Facility staff selects a context-aware trigger such as "Community support" or "Facility support".
2. System opens the help widget with facility categories.
3. Facility staff chooses a category: "Partnership inquiry", "Licensing and seats", "Onboarding staff", "Technical setup", "Billing and invoice", "Existing account issue", or "Something else".
4. Facility staff enters a message.
5. Facility staff provides or confirms an email address for reply.
6. Facility staff submits the form.
7. System validates, stores, enqueues, and confirms.

### UC-003 — Receive auto-acknowledgment

**Trigger:** New help request persisted.  
**Precondition:** n8n workflow is active and email provider configured.  
**Postcondition:** Sender receives a calm, plain-text+HTML email confirming receipt and expected response time, using copy appropriate to the persona.

### UC-004 — Route and triage via n8n by context

**Trigger:** Webhook delivered to n8n.  
**Precondition:** n8n workflow has context-specific routing rules.  
**Postcondition:** Ticket routed to caregiver or facility support channel; P0/P1 escalate immediately.

**Steps:**

1. n8n receives POST with request payload including `context` and `category`.
2. n8n validates intake token.
3. n8n routes to the caregiver or facility branch.
4. n8n maps category to severity per support SLA.
5. n8n creates/updates ticket in support tool (email/Slack/Data Table).
6. n8n sends context-appropriate auto-acknowledgment.
7. For P0/P1, n8n alerts the relevant on-call channel immediately.

### UC-005 — Support agent updates status

**Trigger:** Agent resolves or needs more info.  
**Precondition:** Agent has staff access.  
**Postcondition:** Request status updated; audit log written.

**Steps:**

1. Agent opens admin endpoint.
2. Agent filters by `context`, status, and severity.
3. Agent updates status: `open`, `needs_info`, `resolved`, `closed`.
4. Agent optionally adds an internal note.
5. System writes audit row and timestamps.

## 3. User stories

- As a caregiver trying to buy a gift, I want to ask a purchase question without leaving the page, so I can complete the purchase.
- As a caregiver whose gift was not received, I want to report it quickly, so support can resend or refund.
- As a facility director exploring mynaani for my community, I want to ask a partnership question, so I can evaluate licensing.
- As a facility admin managing seat licenses, I want to report a billing or onboarding issue, so it reaches the right team.
- As a support agent, I want to see caregiver and facility requests in separate queues, so I can prioritize by persona and severity.
- As a product owner, I want to ensure the learner consumer path never shows this widget, so older adults are not rushed or alarmed.

## 4. Business rules

- BR-001: The `HelpRequestWidget` is only rendered on allowed caregiver/facility routes. Any consumer learner route must not render it.
- BR-002: The backend validates that the submitted `category` is valid for the given `context`. A mismatched pair returns 422.
- BR-003: Anonymous submissions are allowed but rate-limited per IP and email.
- BR-004: Authenticated facility staff have their org email pre-filled and linked to the request.
- BR-005: Category determines initial severity and SLA response time.
- BR-006: PII (email, message) is not logged in application logs; only `request_id`, `context`, and `category` may be logged.
- BR-007: Auto-acknowledgment must not promise resolution, only receipt and expected response time.
- BR-008: All status changes are append-only in an audit table.

## 5. Related documents

- BRD-N8N-HELP-001
- FRD-N8N-HELP-001
- PRD-N8N-HELP-001
- `.ai/research/2026-09-11-n8n-help-flow-research.md`
