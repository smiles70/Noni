# Sprint 9: Curriculum View Accessibility Polish (CLOSED)

Tag: `sprint-9-curriculum-a11y-v1`. Brings CurriculumRenderer up to the same accessibility bar as LandingPage and enforces the Reversibility architectural rule in code.

## Phases

- 9.1 Rewrite `CurriculumRenderer.tsx` with semantic landmarks, CSS variables, aria-live
- 9.2 `onReturn` callback exposes a Return-to-start button (Reversibility rule)
- 9.3 `App.tsx` wires the callback
- 9.4 `frontend/e2e/curriculum.spec.ts`: 3 specs incl. axe WCAG 2.1 AA scan
- 9.5 Closeout
