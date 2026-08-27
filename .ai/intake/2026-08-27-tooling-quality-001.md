# Intake — TOOLING-QUALITY-001: Frontend developer-experience and quality tooling

**Date:** 2026-08-27  
**Requester:** Product  
**Process:** v9.51  
**Scope:** Address Aura Code Intelligence report tooling gaps for the Mynaani/Noni repo. Focus on quick, high-impact frontend tooling and knowledge-continuity improvements.

---

## Gaps to close

1. Missing `.nvmrc` for Node version consistency.
2. Missing Prettier and `format:check`.
3. Missing ESLint with `max-warnings=0`.
4. Missing Vitest coverage thresholds.
5. Missing circular-dependency / dead-code / complexity checks.
6. Missing license-compliance check.
7. Missing husky pre-push / pre-commit hooks.
8. Knowledge continuity: central onboarding in README.

## Constraints

- Do not break the existing build, type-check, or tests.
- Do not introduce excessive new dependencies; prefer the smallest tool that satisfies the scanner.
- Preserve Process v9.51 artifact discipline.
- Keep changes additive where possible.

## Success criteria

- `.nvmrc` exists and matches the production Node version.
- `npm run format:check` passes in CI.
- `npm run lint` runs ESLint with `max-warnings=0`.
- `npm run test:unit` produces a coverage report with thresholds.
- `npm run lint:circular`, `npm run lint:dead-code`, and `npm run lint:complexity` exist and pass (or warn without failing CI).
- `npm run lint:licenses` checks for GPL.
- `.husky/pre-push` runs type-check and unit tests.
- README has a clear local setup and contribution guide.
- All existing builds and tests still pass.
