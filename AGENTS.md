# Noni / Mynaani — agent working rules

## Deployment gate (human review required)

- All work ships to **staging** only. Push feature branches to `staging`
  (`git push origin <branch>:staging`) to trigger the Deploy Staging
  workflow and verify there.
- **Production (`main` → live) requires explicit human permission.**
  Do not merge PRs to `main` or push `main` to production-facing branches
  without the user's explicit go-ahead for that specific change.
- Stated 2026-09-05 by repo owner.

## Landing page

- The hero is intentionally a **fixed, non-scrolling single viewport**.
  Do not change its positioning/flow without explicit approval — a prior
  attempt (SCROLL-DEPTH-001, `height: 100vh` in-flow) visibly shrank the
  hero image and was rolled back.
- Research for B2B + page-depth options lives in
  `.ai/intake/2026-09-05-b2b-landing-research-001.md`.
