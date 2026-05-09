# Noni - Progress

## Deferred Decisions

See [`docs/deferred-decisions.md`](./docs/deferred-decisions.md) for the bundle of 3rd-party / vendor decisions held for a single later pass.

## Active Sprint

None. **Sprint 8: CI Playwright Integration completed** (tag `sprint-8-ci-e2e-v1`).

## Completed

- Sprint 0: Initial Scaffolding
- Sprint 1: Progress Closeout (`sprint-closeout-v1`)
- Sprint 2: Curriculum Expansion (`sprint-2-curriculum-v1`)
- Sprint 3: Golden Landing Flow Contract (`sprint-3-landing-contract-v1`)
- Sprint 4: Engineering Foundations (`sprint-4-engineering-foundations-v1`)
- Sprint 5: Landing Copy + Page Rendering (`sprint-5-landing-copy-v1`)
- Sprint 6: Hardening & Coverage (`sprint-6-hardening-coverage-v1`)
- Sprint 7: Documentation & Developer Onboarding (`sprint-7-docs-onboarding-v1`)
- Sprint 8: CI Playwright Integration (`sprint-8-ci-e2e-v1`)
  - New `e2e` job in `.github/workflows/ci.yml` running after backend + frontend jobs
  - Postgres service container, backend booted in background, health-checked
  - Playwright chromium browser cached by `package-lock.json` hash
  - Playwright config now CI-aware: `forbidOnly`, retries=2, traces + screenshots on failure
  - Failure artifacts uploaded: HTML report + backend log (14-day retention)
  - WCAG 2.1 AA axe scan now enforced on every push/PR

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
- Cross-browser E2E (Firefox + WebKit) — chromium only for now
- Copy for Golden Flow Steps 5-7 (post-interaction; needs real Claude)

## Known Environment Quirks

- IDE write_to_file/edit do not persist to WSL filesystem in this setup. Use shell heredocs.
