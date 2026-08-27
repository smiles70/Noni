# Security Policy — Noni

## Supported versions

| Version | Supported |
|---|---|
| `main` | Yes |
| older tags | No |

## Reporting a vulnerability

Do not open a public issue for security concerns. Contact the maintainers through a private channel (e.g., the repository owner or the escalation path in `CODEOWNERS`).

## Security posture

- **Authentication:** Mock provider is used for dev/tests while a production provider is deferred per `docs/deferred-decisions.md`. The `backend/api/routes/auth.py` endpoints enforce stateless Bearer token verification.
- **Authorization:** Session TTL (`SESSION_TTL_DAYS`), rate limiting (`backend/services/rate_limit.py`), admin gating for telemetry export.
- **Input validation:** Pydantic models for all request/response contracts.
- **Database access:** SQLAlchemy ORM with parameterized queries; no raw `execute()` with user input.
- **Secrets:** Loaded via `pydantic-settings` from environment variables. `.sops.yaml` is configured for encrypted secret management. CI runs `secrets-drift.yml` and `truffleHog` to detect leaks. No hardcoded production secrets are present in source.
- **Data handling:** GDPR erasure workflow in `backend/services/deletion.py`. PII: email, display_name, auth_user_id.
- **Dependency scanning:** `npm audit` (frontend), `bandit` (backend SAST), `trivy` (container scan) in `.github/workflows/ci.yml`.
- **Known active issues:** `npm audit` currently reports 0 vulnerabilities.

## Threat model and audits

- `docs/audits/enterprise-security-threat-model-2026-05-25.md`
- `docs/audits/production-readiness-100-point-audit-2026-05-25.md`

## Incident response

See `docs/ops/incident-response-runbook.md` and `docs/RUNBOOK.md`.
