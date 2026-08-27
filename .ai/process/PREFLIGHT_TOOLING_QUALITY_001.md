# Preflight — TOOLING-QUALITY-001: Frontend tooling and knowledge continuity

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-tooling-quality-001.md`

## Pre-flight checklist

| # | Gate | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 1 | Intake approved | GO | Product | Intake created |
| 2 | Aura report reviewed | GO | Research | `Downloads/noni/aura-report-analysis-noni.html` |
| 3 | Existing CI understood | GO | Engineering | `.github/workflows/ci.yml` |
| 4 | Build and tests currently pass | GO | Engineering | Last successful build on main |
| 5 | Package manager available | GO | Engineering | `npm` in `frontend/` workspace |
| 6 | No breaking changes expected | GO | Engineering | All fixes additive |

## Go / no-go

**GO** for Phase 0. Execute tooling fixes.

## Risks

1. ESLint may surface many warnings; applying `max-warnings=0` could require many small fixes.
2. Prettier may re-format many files; review diff carefully.
3. New dependencies must be pinned and installed with `npm install`.
