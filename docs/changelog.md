# Changelog

All notable changes to the Noni platform.

Format based on [Keep a Changelog](https://keepachangelog.com/).

---

## [1.0.0] -- 2026-05-28

### Added
- Help center with 4 geragogy-compliant articles
- `/help` route in React app
- Navigation links to Help from all major pages (Landing, Curriculum, Paywall, Gift, Account)
- `frontend/.env.production` for reliable build-time API URL configuration

### Fixed
- Production frontend calling `localhost:8000` instead of `noni-api.fly.dev`
- Build process now includes bundle verification step

---

## [0.9.0] -- 2026-05-27

### Added
- Clerk JWT authentication (ADR 0024)
- Session-aware NavBar
- Curriculum menu with progress tracking
- Paid lesson renderer for Modules 4-5
- Gift token redemption flow
- Stripe Checkout integration
- Telemetry retention policy with pg_cron

### Fixed
- JsonFormatter `KeyError` crash in production logging
- PyJWKClient `cache_ttl` parameter error

---

## [0.8.0] -- 2026-05-24

### Added
- Module 4 (Claude Skills) curriculum content
- Module 5 (Composing Agents) curriculum content
- UI State Envelope system (ADR 0019)
- Design tokens and `RenderGuard` component

---

## [0.7.0] -- 2026-05-17

### Added
- Landing page with hero, introduction, and CTA sections
- First-win content flow
- Multi-page lesson structure (context, principle, example, retrieval)

---

## [0.1.0] -- 2026-05-01

### Added
- Initial scaffolding
- Modules 1-3 curriculum content
- FastAPI backend with curriculum endpoints
- React + Vite frontend
- Playwright E2E tests with axe WCAG 2.1 AA
