# 0003 — Vite + React 18 + TypeScript (strict) for the frontend

## Status

Accepted (Sprint 1 Phase 4, durably documented in Sprint 4).

## Context

The frontend is an authenticated single-page application that renders backend-approved UI states. SSR/SEO/edge rendering are not required (no public marketing surface). Three credible options:

- **Create React App** — deprecated, no active maintenance.
- **Next.js** — heavyweight, optimized for SSR/edge use cases we do not have.
- **Vite + React + TypeScript** — minimal, fast HMR, modern bundler, current Fortune-500 default for new SPAs.

## Decision

Vite + React 18 + TypeScript with `strict: true`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`.

## Consequences

- TypeScript strict mode catches errors at build time; CI runs `tsc --noEmit`.
- No SSR / SEO benefits; not a goal.
- No runtime framework lock-in beyond React.
- Frontend is a passive renderer (per ARCHITECTURE rule 1); zero business logic in `src/`.
- Server state (when added later) will use TanStack Query, not Redux.
