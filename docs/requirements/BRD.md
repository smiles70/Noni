# Business Requirements Document (BRD) — Mynaani Authentication

**Document ID:** BRD-AUTH-001  
**Version:** 1.0  
**Date:** 2026-08-27  
**Status:** Accepted  
**Source:** User request; `docs/decisions/0027-magic-link-auth.md`; `.ai/intake/2026-08-27-magic-link-auth.md`  
**Owner:** Mynaani Engineering Team  

---

## 1. Business objective

Enable older adults to sign in to Mynaani without remembering or resetting passwords, using a calm, non-urgent, passwordless authentication flow that aligns with Mynaani's geragogy-first values.

## 2. Problem statement

- Older adults often abandon digital learning before observable task errors due to cognitive overload, anxiety, or lost credentials.
- Passwords create a failure class: forgotten credentials, reset loops, and auto-generated "strong" passwords that are hard to recall or type.
- Clerk was removed because no live account credentials were available and the team wanted a more geragogy-aligned provider.

## 3. Business goals

| ID | Goal | Success measure |
|---|---|---|
| B-001 | Reduce sign-in abandonment for learners 55+ | Sign-in completion rate > 85% in pilot |
| B-002 | Eliminate password management burden | Zero password reset requests |
| B-003 | Maintain vendor independence and dignity | No auto-renew, no mid-lesson paywall, no dark patterns |
| B-004 | Enable real older-adult pilots | Production auth provider selected and implemented |
| B-005 | Keep dev/test path frictionless | Mock auth continues to work without external API keys |

## 4. Stakeholders

- **Primary:** Adults 55+ new or anxious about AI.
- **Secondary:** Caregivers/adult children gifting access.
- **Internal:** Mynaani engineering, product, geragogy lead.
- **External:** Magic.link (vendor).

## 5. Constraints

- No urgency framing (ARCHITECTURE.md Rule 5).
- No dark patterns (Rule 6).
- No automated actions without explicit review (Rule 7).
- Cognitive safety first (Rule 8).
- WCAG 2.1 AA.
- Budget: Magic.link free tier initially; monitor usage.

## 6. Assumptions

- Magic.link email deliverability is acceptable for the target audience.
- Learners have access to an email account and can follow a simple link.
- The pilot will remain within Magic's free tier for the initial older-adult cohort.

## 7. Risks

| Risk | Mitigation |
|---|---|
| Magic.link pricing changes | Track usage; keep mock fallback; architect around `AuthProvider` protocol for swapability |
| 15-minute DID token expires during a lesson | Design a calm re-auth prompt, not auto-disruption |
| Email deliverability issues | Monitor bounce rates; keep a support channel |
| Vendor lock-in | `AuthProvider` protocol isolates the provider; IDs are stable `uuid5` of email |

## 8. Related documents

- ADR 0027: `docs/decisions/0027-magic-link-auth.md`
- Magic Intake: `.ai/intake/2026-08-27-magic-link-auth.md`
- Integration Plan: `.ai/process/MAGIC_LINK_INTEGRATION_PLAN.md`
