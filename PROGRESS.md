# Noni - Progress

## Deferred Decisions

See [`docs/deferred-decisions.md`](./docs/deferred-decisions.md) for the bundle of 3rd-party / vendor decisions explicitly held for a single later pass (auth, real Claude, email, hosting, observability, etc.).

## Active Sprint

None. **Sprint 6: Hardening & Coverage completed** (tag `sprint-6-hardening-coverage-v1`).

## Completed

- Sprint 0: Initial Scaffolding
- Sprint 1: Progress Closeout (`sprint-closeout-v1`)
- Sprint 2: Curriculum Expansion (`sprint-2-curriculum-v1`)
- Sprint 3: Golden Landing Flow Contract (`sprint-3-landing-contract-v1`)
- Sprint 4: Engineering Foundations (`sprint-4-engineering-foundations-v1`)
- Sprint 5: Landing Copy + Page Rendering (`sprint-5-landing-copy-v1`)
- Sprint 6: Hardening & Coverage (`sprint-6-hardening-coverage-v1`)
  - Curriculum Units 5-7: Verifying Suggestions, When to Ignore, Recovering from Mistakes
  - Telemetry export: `/api/telemetry/export` (JSON) and `/api/telemetry/export.csv`
  - Accessibility: `:focus-visible` rings, larger-text toggle (localStorage-persisted), `prefers-reduced-motion`
  - Playwright + axe-playwright E2E suite at `frontend/e2e/` with 4 specs including WCAG 2.1 AA scan
  - ADRs 0007 (accessibility) + 0008 (E2E + axe)
  - 49 backend tests; frontend builds 189.70 kB / 63.59 kB gzipped

## Out of Scope (deferred)

- Real Claude API integration (vendor pass)
- Authentication / per-learner state (vendor pass)
- Email provider, observability, hosting, CDN, payments (vendor pass)
- Production deployment pipeline beyond GitHub Actions config
- Internationalization
- Container scanning (Trivy/Grype) and Dockerfile
- Bundle size budgets
- Browser observability (Sentry / Datadog RUM)
- Feature flags
- Manual screen-reader audit (NVDA/JAWS/VoiceOver)
- Design system / component library
- Copy for Golden Flow Steps 5-7 (post-interaction; needs real Claude)

## Known Environment Quirks

- IDE write_to_file/edit do not persist to WSL filesystem in this setup. Use shell heredocs.
