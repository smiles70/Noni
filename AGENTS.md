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

## Commit hygiene — no sweeps

- **Never `git add -A` or `git add .`.** Stage explicit paths only —
  two incidents came from blanket adds sweeping in unrelated local
  files (da1d538: stray docs + a WIP workflow edit that broke 5
  staging deploys).
- Before every commit: `git diff --cached --stat` and confirm every
  staged file belongs to the change.
- The `.husky/pre-commit` sweep guard **blocks commits touching
  `.github/`** unless run as `ALLOW_WORKFLOW_CHANGES=1 git commit` —
  workflow changes ship as their own commit, never riding along.
- Unrelated untracked/modified files in the working tree belong to the
  human — leave them alone, don't stage, don't delete.

## Journey loop and paywall guard

- Load `.devin/skills/journey-loop-guard/SKILL.md` when modifying any
  curriculum end-state, paywall, purchase success/cancel, gift redemption,
  or progress-resume surface.
- After a successful **self-purchase of `modules_4_5`**, the primary
  success CTA must route to `/paid-curriculum`, not `/curriculum`.
- After a successful **gift redemption**, the primary "continue" CTA
  must also route to `/paid-curriculum`, not `/curriculum`.
- The free `/curriculum` track ends with a CTA to `/paywall`. If the
  learner is already entitled, that CTA must route to `/paid-curriculum`.
- `/paywall` must detect an active `modules_4_5` entitlement and offer
  "Continue to the paid modules" instead of a "Buy" CTA.
- `goCurriculum` is a progress-based resume helper. Never use it in a
  post-purchase or post-redemption flow; it sends entitled learners with no
  paid progress back to the free track.
- `PurchaseCancelPage` must not route an already-entitled learner back
  to `/paywall`; use `/` or the appropriate curriculum track.
- Progress stored only in `localStorage` does not resume across devices.
  Any cross-device resume feature must use server-side progress.
- Any change to `PurchaseSuccessPage`, `GiftRedeemPage`,
  `PurchaseCancelPage`, `PaywallPage`, or the resume/route helpers must be
  accompanied by both a unit/journey-contract test and a Playwright E2E test.
