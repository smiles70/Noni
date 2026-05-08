# Noni - Progress

## Active Sprint
None. Sprint 5: Landing Copy + Page Rendering completed (tag sprint-5-landing-copy-v1).

## Completed
- Sprint 0: Initial Scaffolding
- Sprint 1: Progress Closeout (sprint-closeout-v1)
- Sprint 2: Curriculum Expansion (sprint-2-curriculum-v1)
- Sprint 3: Golden Landing Flow Contract (sprint-3-landing-contract-v1)
- Sprint 4: Engineering Foundations (sprint-4-engineering-foundations-v1)
- Sprint 5: Landing Copy + Page Rendering (sprint-5-landing-copy-v1)
  - backend/content/landing_page.py canonical copy
  - LandingPageContent Pydantic schema
  - GET /api/landing/page endpoint
  - ADR 0006 (landing content separate from step model)
  - Frontend LandingPage.tsx + api/landing.ts + App.tsx toggle
  - 8 new tests (46 total); frontend builds 188.86 kB / 63.36 kB gzipped

## Out of Scope (deferred)
- Real Claude API integration
- Authentication / user accounts
- Production deployment pipeline beyond GitHub Actions config
- Real-time durable telemetry export
- Accessibility audit (WCAG AA, axe-core)
- Internationalization
- Container scanning, Bundle size budgets, Browser observability, Feature flags, E2E tests, Design system
- Copy for Golden Flow Steps 5-7 (post-interaction; requires real Claude)

## Known Environment Quirks
- IDE write_to_file/edit do not persist to WSL filesystem in this setup. Use shell heredocs.
