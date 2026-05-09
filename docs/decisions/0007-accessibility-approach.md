# 0007 - Accessibility approach: WCAG 2.1 AA via axe + visible focus + larger-text mode

## Status

Accepted (Sprint 6).

## Context

Noni's primary audience is older adults. Accessibility is a product requirement, not a polish item. Three reinforcing layers are needed:

1. **Static / semantic correctness** — proper landmarks, headings, ARIA where appropriate.
2. **Keyboard usability** — visible focus indicators on every interactive element.
3. **Vision and reading comfort** — user-controlled larger-text mode that survives reload, plus respect for `prefers-reduced-motion`.

## Decision

- Adopt **WCAG 2.1 Level AA** as the minimum bar.
- Enforce automated checks via `axe-playwright` inside the E2E suite (see ADR 0008). The axe scan covers tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`.
- Provide a **visible `:focus-visible` ring** in `frontend/src/styles.css` on all interactive elements (3px solid `#ffbf47`, 2px offset). This is shown only for keyboard users, not for mouse clicks.
- Provide a **larger-text mode** toggle persisted in `localStorage` under key `noni_large_text`. The toggle adds class `large-text` on `<html>` and bumps the root font-size from 100% to 125%, scaling all `rem`-based sizes.
- Honor `prefers-reduced-motion: reduce` to disable scroll-smooth and any animations.
- Keep CSS variables for color tokens (`--noni-text`, `--noni-accent`, etc.) so future contrast adjustments are localized.

## Consequences

- The E2E `axe` check is a **gating** test in the Playwright suite. A new violation breaks CI.
- Every new interactive control must be keyboard-reachable and respect the focus-visible style. Custom elements that suppress this style require an ADR-style justification.
- The larger-text toggle preference is per-browser. Cross-device sync requires the deferred auth + per-learner state work.
- Future component decisions (design system, icon library) must not regress focus visibility or contrast.
- A formal manual screen-reader audit (NVDA / JAWS / VoiceOver) remains out of scope for this sprint and is tracked as a follow-on.
