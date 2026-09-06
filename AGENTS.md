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
