# Intake — WS-D: scroll-depth telemetry on marketing pages (FIRST)

- Priority: P1 (lands before any wayfinding change — we need OUR
  baseline, not the industry's ~50% figure)
- Date: 2026-09-17
- Persona: shared — /caregiver + /for-communities.
- Research: `.ai/research/2026-09-17-long-scroll-marketing-ux.md` (WS-D)

## Why first

Every other workstream (anchor nav, mid-page CTA, divider fix) is a
hypothesis. Without per-page scroll-depth data we cannot tell whether
they helped. Ship measurement alone, collect a baseline, then judge.

## Scope

1. Lightweight `scrollDepthTelemetry` module mirroring
   `onboardingTelemetry` (singleton, dedup via `shouldEmit`, silent
   failure — telemetry must never break a page).
2. Events: `marketing.scroll_depth` with metadata
   `{ page: "caregiver" | "for-communities", depth: 25 | 50 | 90,
   viewport: "mobile" | "desktop" }` — fired once per threshold per
   pageview via IntersectionObserver or scroll listener (passive).
3. Backend: accept on a telemetry route following the
   `/api/v1/telemetry/onboarding` shape (extend or sibling endpoint —
   match existing envelope and BetterStack forwarding).
4. Wire into both page components on mount/unmount only — zero visual
   change.

## Edge cases

- StrictMode double-mount → dedup window covers it (existing
  `shouldEmit` contract).
- Endpoint down → silent catch, no retry storm, no user-visible error.
- Bots/preload → depth events only on real scroll, not synthetic.
- PII: page + depth + viewport class only — no session/user identity
  beyond what existing telemetry already carries.

## Acceptance

- Events visible in BetterStack/backend logs for both pages.
- Unit test: thresholds fire once each; dedup works; failure is silent.
- No visual or behavioral change on either page (unit + e2e no-op).
