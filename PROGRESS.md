# Noni - Progress

## Deferred Decisions

See [`docs/deferred-decisions.md`](./docs/deferred-decisions.md) for the bundle of 3rd-party / vendor decisions held for a single later pass.

## Active Sprint

None. **Sprint 7: Documentation & Developer Onboarding completed** (tag `sprint-7-docs-onboarding-v1`).

## Completed

- Sprint 0: Initial Scaffolding
- Sprint 1: Progress Closeout (`sprint-closeout-v1`)
- Sprint 2: Curriculum Expansion (`sprint-2-curriculum-v1`)
- Sprint 3: Golden Landing Flow Contract (`sprint-3-landing-contract-v1`)
- Sprint 4: Engineering Foundations (`sprint-4-engineering-foundations-v1`)
- Sprint 5: Landing Copy + Page Rendering (`sprint-5-landing-copy-v1`)
- Sprint 6: Hardening & Coverage (`sprint-6-hardening-coverage-v1`)
- Sprint 7: Documentation & Developer Onboarding (`sprint-7-docs-onboarding-v1`)
  - README rewritten end-to-end (current setup, structure, API surface, dev workflow, sprint history, ADR + deferred-decisions pointers)
  - CONTRIBUTING.md added (sprint workflow, ADR convention, how-to guides, commit hygiene)
  - All commands in README smoke-tested (pytest passes, frontend builds)

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
