# Business Requirements Document (BRD) — n8n Help Flow

**Document ID:** BRD-N8N-HELP-001  
**Version:** 1.1  
**Date:** 2026-09-11  
**Status:** Draft — re-assessed for path-gated caregiver / facility scope  
**Source:** `.ai/intake/2026-09-11-n8n-help-flow-intake-001.md`  
**Owner:** Mynaani Product / Engineering

---

## 1. Business objective

Provide a calm, structured, and trackable way for **caregivers** and **senior care facility staff** to request help from Mynaani support, while **explicitly keeping the main consumer learner path free of any interactive help chat or request widget** to comply with the geragogy contract.

## 2. Problem statement

- The main consumer learner path (`/help`) is intentionally a static, self-service support surface per `docs/library/CONTRACT.md`. Adding a chat-like or dynamic help flow there would introduce urgency, cognitive load, and pressure that harms older adult learners.
- **Caregivers** purchasing gifts on `/gift` currently have only a generic `mailto` link. They lack context-aware support (e.g., payment failure, gift not received).
- **Facility staff** exploring/operating B2B features on `/for-communities`, `/org`, and `/c/:slug` also have only a generic contact link. They cannot send structured org/licensing/seat context to support.
- There is no internal routing or SLA tracking for these high-value B2C/B2B personas.

## 3. Business goals

| ID | Goal | Success measure |
|---|---|---|
| B-001 | Increase gift checkout completion by reducing support friction for caregivers | `/gift` checkout completion rate improves by 10% in pilot |
| B-002 | Improve facility partnership inquiry response time | P0/P1 facility request initial response within SLA for > 95% of valid requests |
| B-003 | Reduce back-and-forth by capturing persona context upfront | Median messages per ticket reduced by 30% |
| B-004 | Maintain zero n8n chat exposure on consumer learner paths | E2E tests pass on `/`, `/help`, `/curriculum`, `/paywall`, `/account`, `/menu`, `/welcome`, `/signin`, `/gift-redeem` |
| B-005 | Preserve calm, dignity-preserving UX on allowed paths | Zero exclamation marks; zero urgency language; geragogy review pass for any consumer-facing surfaces |
| B-006 | Protect user privacy | No PII in logs; secure n8n payload; audit trail |

## 4. Stakeholders

- **Primary:** Caregivers buying/managing gifts; senior care facility staff and partners.
- **Secondary:** Mynaani customer success, support agents, B2B sales.
- **Internal:** Engineering, geragogy lead, security/compliance.
- **External:** n8n (automation), email provider (Resend/SES), Slack/notification channel.

## 5. Constraints

- The n8n help widget must **not** be reachable from the main consumer learner path (`/`, `/help`, `/curriculum`, `/paywall`, `/account`, `/menu`, `/welcome`, `/signin`, `/gift-redeem`, `/purchase/success`, `/purchase/cancel`).
- The existing static `HelpPage` (`/help`) must remain unchanged for consumer learners.
- The `/gift` path is a purchase-adjacent caregiver flow; any help widget there must not create a purchase/paywall loop.
- Must comply with `docs/library/CONTRACT.md` on any surface reachable by learners.
- `docs/governance/support-sla.md` severity definitions still apply.
- PII must not be logged; credentials are env vars; no secrets in repo.
- Deployment to `staging` first; `main` requires explicit human permission.

## 6. Assumptions

- `/gift` is the primary caregiver purchase path.
- `/for-communities`, `/org`, and `/c/:slug` are facility/B2B paths.
- `/gift-redeem` is a consumer learner path (recipient) and does **not** get the widget.
- An n8n instance (Cloud or self-hosted) will be available and reachable from the backend.
- Support staff have separate channels or queues for caregiver vs facility tickets.

## 7. Risks

| Risk | Mitigation |
|---|---|
| Widget accidentally rendered on a consumer learner route (geragogy violation) | Route allowlist in `App.tsx`; component `useLocation` guard; E2E asserting absence on consumer routes. |
| Wrong category set shown for a persona | `context` prop from route; backend validates `category` belongs to `context`. |
| Caregiver `/gift` support flow creates gift-purchase loop | Journey-loop guard; widget does not redirect to `/paywall` or `/gift-redeem`. |
| Webhook abuse / spam | Rate limiting, IP reputation, per-context throttling. |
| n8n webhook unavailable or slow | Async enqueue with Celery/Redis fallback; retry; status tracking. |
| PII exposure in n8n execution logs | Redact PII in payload; use n8n credentials vault; no full-body logging. |
| Auto-ack email delays or spam-boxing | Authenticated domain, plain-text fallback. |
| Support SLA missed because ticket routed to wrong persona queue | n8n branches by `context` and category; fallback alert. |

## 8. Related documents

- USECASE-N8N-HELP-001
- FRD-N8N-HELP-001
- PRD-N8N-HELP-001
- `.ai/research/2026-09-11-n8n-help-flow-research.md`
