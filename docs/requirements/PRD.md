# Product Requirements Document (PRD) — Mynaani Authentication

**Document ID:** PRD-AUTH-001  
**Version:** 1.0  
**Date:** 2026-08-27  
**Status:** Accepted  
**Source:** `.ai/intake/2026-08-27-magic-link-auth.md`; ADR 0027  
**Owner:** Mynaani Engineering Team  

---

## 1. Product overview

Replace the decommissioned Clerk integration and the dev-only mock provider with Magic.link passwordless authentication, chosen for its geragogy fit and Vite+FastAPI compatibility.

## 2. Non-functional requirements

| ID | Requirement | Priority | How verified |
|---|---|---|---|
| NFR-001 | No passwords, no dark patterns, no urgency framing | Critical | Manual geragogy review of `SignInPage.tsx` |
| NFR-002 | No auto-renew or subscription vendor lock-in | Critical | Vendor contract review; pricing page inspection |
| NFR-003 | DID tokens refreshed only by user action | High | Token lifetime 15 min; no silent refresh |
| NFR-004 | Geragogy-first copy on the sign-in page | High | Content review against `docs/library/CONTRACT.md` |
| NFR-005 | Maintain WCAG 2.1 AA | High | `axe-playwright` E2E |
| NFR-006 | Maintain the closed-world UI contract | High | `RenderGuard` still passes |

## 3. Technical requirements

| ID | Requirement | Priority | Evidence |
|---|---|---|---|
| TR-001 | Add `magic-admin>=2.4.0,<2.6.0` to Python dependencies | High | `pyproject.toml`, `pip install` success |
| TR-002 | Add `magic-sdk@~33.9.0` to `frontend/package.json` | High | `package-lock.json`, `npm install` success |
| TR-003 | Implement `MagicAuthProvider` class | High | Unit test for `get_auth_provider()` with `AUTH_PROVIDER=magic` |
| TR-004 | Implement `backend/services/magic_verifier.py` | High | `pytest backend/tests/test_magic_verifier.py` pass |
| TR-005 | Update `backend/core/config.py` with `MAGIC_*` settings | High | Config loads with `AUTH_PROVIDER=magic` |
| TR-006 | Update `auth_verifier.py` to route `magic` provider | High | 401/403 mapping for invalid DID tokens |
| TR-007 | Update `SignInPage.tsx` to call `magic.auth.loginWithMagicLink` | High | Manual/E2E sign-in flow |
| TR-008 | Update `AuthProvider.tsx` to use DID token | High | Unit tests pass |
| TR-009 | Update infrastructure and secret files | Medium | `npm run build` with `VITE_AUTH_PROVIDER=magic` |
| TR-010 | Add unit + integration tests | High | New `test_magic_verifier.py` and updated frontend auth tests |

## 4. UX requirements

- The sign-in screen must not display a countdown or pressure language.
- Errors must be calm and actionable: "Please check your email and try again."
- The magic-link button must be the primary action.
- No third-party widget should take over the page unless RenderGuard has approved the envelope.

## 5. Release criteria

- [ ] `npm run type-check` passes
- [ ] `npm run test:unit` passes
- [ ] `npm run build` passes and bundle guard is clean
- [ ] `pytest backend/tests/test_magic_verifier.py` passes
- [ ] `npm audit` and `pip-audit` are clean
- [ ] PRA evidence is updated
- [ ] Nelson score is rescored
- [ ] Privacy/terms pages updated

## 6. Dependencies

- Magic Dashboard account and API keys (`MAGIC_PUBLISHABLE_KEY`, `MAGIC_API_SECRET_KEY`).
- `magic-admin` and `magic-sdk` packages are vetted and pinned.

## 7. Open questions

- What is the re-auth UX when the 15-minute DID token expires mid-lesson?
- What is the expected cost per user on Magic's free tier?
- Should we add a "remember this device" feature in a future ADR?

## 8. Related documents

- BRD-AUTH-001: `docs/requirements/BRD.md`
- FRD-AUTH-001: `docs/requirements/FRD.md`
- ADR 0027: `docs/decisions/0027-magic-link-auth.md`
