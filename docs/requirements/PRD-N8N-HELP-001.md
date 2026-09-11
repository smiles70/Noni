# Product Requirements Document (PRD) — n8n Help Flow

**Document ID:** PRD-N8N-HELP-001  
**Version:** 1.1  
**Date:** 2026-09-11  
**Status:** Draft — re-assessed for path-gated caregiver / facility scope  
**Source:** `.ai/intake/2026-09-11-n8n-help-flow-intake-001.md`

---

## 1. Product overview

A **path-gated, context-aware support request widget** that appears only on the caregiver path (`/gift`) and the senior care facility path (`/for-communities`, `/org`, `/c/:slug`). It captures persona-specific context, persists the request in the Mynaani backend, and pushes it to an n8n webhook for routing, auto-acknowledgment, and support-team notification. The main consumer learner path (`/help`, `/curriculum`, `/paywall`, `/account`, etc.) is intentionally unchanged and does **not** display the widget.

## 2. Non-functional requirements

| ID | Requirement | Priority | How verified |
|---|---|---|---|
| NFR-001 | Widget absent from all consumer learner paths | Critical | Playwright E2E asserting absence on `/`, `/help`, `/curriculum`, `/paywall`, `/account`, `/menu`, `/welcome`, `/signin`, `/gift-redeem`, `/purchase/success`, `/purchase/cancel` |
| NFR-002 | Calm, dignity-preserving UX on allowed paths per `docs/library/CONTRACT.md` | Critical | Geragogy review of `HelpRequestWidget.tsx` copy and design. |
| NFR-003 | WCAG 2.1 AA accessibility | Critical | `axe-playwright` E2E, manual focus/screen-reader check. |
| NFR-004 | PII protection in logs and n8n payloads | Critical | Code review; no full message or email in application logs. |
| NFR-005 | Rate limiting and abuse resistance | Critical | Load test; verify throttle after 5 requests / 15 min per context. |
| NFR-006 | Async, non-blocking webhook delivery | High | Unit/integration tests; n8n timeout does not block form submission. |
| NFR-007 | Graceful degradation when n8n is unavailable | High | Webhook retries; status remains `pending` and recovers. |
| NFR-008 | Feature flag gating | Medium | `FEATURE_HELP_REQUESTS=false` hides every widget and POST returns 404. |
| NFR-009 | Observability: metrics and alerts on webhook failures | Medium | BetterStack / Prometheus metrics on n8n delivery failures. |

## 3. Technical requirements

| ID | Requirement | Priority | Evidence |
|---|---|---|---|
| TR-001 | Add `N8N_WEBHOOK_URL` and `N8N_WEBHOOK_TOKEN` to `backend/core/config.py` | High | `.env.example` updated; config loads. |
| TR-002 | Create `backend/models/support.py` with `SupportRequest` and `SupportRequestAudit` | High | Migrations; unit test for model. |
| TR-003 | Create `backend/api/routes/help.py` with `POST /api/v1/help/requests` | High | Validates `context` enum and `category` set; returns 422 on mismatch. |
| TR-004 | Create `backend/services/n8n_client.py` for async webhook delivery with retries | High | Test with mocked HTTP client; retry on 5xx/timeout. |
| TR-005 | Add `backend/api/routes/admin/help.py` or extend `admin.py` for staff endpoints | Medium | `require_staff` gate; filter by `context`; list/filter/update. |
| TR-006 | Add `FEATURE_HELP_REQUESTS` feature flag | Medium | Config, route guard, widget visibility. |
| TR-007 | Create `frontend/src/components/HelpRequestWidget.tsx` | High | Accepts `context` prop and renders correct categories. |
| TR-008 | Mount `HelpRequestWidget` only on `/gift`, `/for-communities`, `/org`, `/c/:slug` | High | App.tsx route allowlist; `useLocation` guard. |
| TR-009 | Leave `HelpPage` (`/help`) and consumer help bubble unchanged | High | No diff on `HelpPage.tsx` or `LandingPage` consumer path. |
| TR-010 | Add `context`-specific category validation in Pydantic | High | `CaregiverHelpRequest` and `FacilityHelpRequest` schemas, or unified with validator. |
| TR-011 | Add backend unit tests and frontend unit tests | High | `pytest backend/tests/test_help_requests.py`; `vitest` for `HelpRequestWidget`. |
| TR-012 | Add Playwright E2E for presence on allowed routes and absence on consumer routes | High | `frontend/playwright` tests. |
| TR-013 | Document n8n workflow setup in `docs/integrations/n8n-help-flow.md` | Medium | Manual test against n8n test webhook. |

## 4. UX requirements

- The widget must use approved colors, typography, spacing, and shapes.
- Trigger labels are context-specific, not generic:
  - `/gift`: "Questions about gifting?"
  - `/for-communities`: "Community support"
  - `/org`, `/c/:slug`: "Facility support"
- No exclamation marks, no countdown, no urgency.
- Validation errors appear inline, not as blocking alerts.
- Confirmation page restates the reply email and expected SLA.
- Focus returns to the first invalid field on submit failure.

## 5. Release criteria

- [ ] `npm run type-check` passes
- [ ] `npm run test:unit` passes
- [ ] `npm run build` passes and bundle guard is clean
- [ ] `pytest backend/tests/test_help_requests.py` passes
- [ ] Playwright E2E: widget present on `/gift`, `/for-communities`, `/org`, `/c/:slug`
- [ ] Playwright E2E: widget absent from `/`, `/help`, `/curriculum`, `/paywall`, `/account`, `/menu`, `/welcome`, `/signin`, `/gift-redeem`, `/purchase/success`, `/purchase/cancel`
- [ ] `npm audit` and `pip-audit` are clean
- [ ] Geragogy review passes for all affected files
- [ ] Journey-loop guard invoked and passed for `/gift` changes
- [ ] Feature flag documented and disabled by default until n8n is configured

## 6. Dependencies

- n8n instance (Cloud or self-hosted) with a Webhook node.
- `httpx` or `requests` for backend outbound webhook (already in `requirements.txt` via `httpx`).
- Email provider (Resend/SES) for context-specific auto-acknowledgment.
- Optional: Slack/notification channel for P0/P1 routing.

## 7. Open questions

- Should `/purchase/success` and `/purchase/cancel` include the widget for post-purchase caregiver support?
- Should `/c/:slug` partner landing use `facility` context or a separate `partner` context?
- Should there be one n8n intake webhook that branches by `context`, or two separate webhooks?
- Is `/gift-redeem` ever reached by caregivers assisting a recipient?
- Should the admin endpoint also allow replying, or is reply handled entirely in n8n?

## 8. Related documents

- USECASE-N8N-HELP-001
- BRD-N8N-HELP-001
- FRD-N8N-HELP-001
- `.ai/research/2026-09-11-n8n-help-flow-research.md`
