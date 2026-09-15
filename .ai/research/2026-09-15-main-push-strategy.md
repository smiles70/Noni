# Research: force-with-lease vs. merge-then-push for `main`

**Date:** 2026-09-15  
**Research question:** For the current `feat/caregiver-path-v2` branch, should `main` (production) be updated with `git push --force-with-lease` or by merging `origin/main` into the feature branch first?

---

## 1. Source table

| # | Source | Type | Verdict |
|---|--------|------|---------|
| 1 | git-push docs — `force-with-lease` updates a remote ref only if the current remote value is the expected value | Official docs | Safer than `--force`, but still bypasses the no-rewrite rule |
| 2 | Atlassian — "Force with lease" is `--force` with a seatbelt; it still overwrites remote history if no one has pushed since your last fetch | Industry / git education | Not for shared branches such as `main` |
| 3 | GitHub — protected branches block force pushes by default and warn that force pushes can remove commits others based work on | Platform docs | Strong signal against force-pushing `main` |
| 4 | GitHub rulesets — "Block force pushes" rule is enabled by default | Platform docs | Best practice: disable force pushes on `main` |
| 5 | GitLab — for branches deployed to production, set `Allowed to push and merge` to No one and use merge requests | Platform docs | `main`/production should not accept direct pushes or force pushes |
| 6 | Thoughtbot — `force-with-lease` is for personal rebased branches, not for integration branches | Industry blog | OK for private work branches, not `main` |
| 7 | Position Is Everything — do not force push `main`, `master`, `develop`, `release/*`, `production` | Industry blog | Explicitly lists `main` and `production` as off-limits |
| 8 | Dev.to "Stop pushing to main" — `main` is the deployment branch, use pull requests/merge | Industry blog | Direct pushes and force pushes are the patterns that break production |
| 9 | Netflix tech blog — production deployments flow through branches, builds, tests, and pipelines, not force-pushed refs | FAANG engineering | Production promotion is a merge/pipeline event, not a force push |
| 10 | CNCF / GitOps — branch protection on the branch ArgoCD/Flux watches is the most important security control; force pushes can wipe deployment history | Industry / security | Force-pushing a production branch breaks audit trail and safety |
| 11 | git-merge docs — fast-forward merges move the branch pointer; non-fast-forward merges create a merge commit | Official docs | Merging is the canonical, non-destructive way to integrate divergent branches |
| 12 | GitLab merge methods — `Merge commit` and `Fast-forward merge` are the supported, auditable ways to land changes on `main` | Platform docs | Merge is the production-friendly mechanism |

## 2. Decision matrix

| Criterion | Force-with-lease | Merge `origin/main` first |
|---|---|---|
| Preserves `main` history | No — rewrites `main` tip | Yes — creates a merge commit or fast-forward |
| Risk of losing someone else's commits | High (can overwrite if you fetched) | None (keeps all commits) |
| Works with branch protection | Usually blocked | Usually allowed if direct pushes are permitted |
| Required for `main`? | No | Best practice for production branches |
| Auditable | No — overwritten commits may disappear | Yes — merge commit records integration point |
| Rollback clarity | Poor — history is rewritten | Good — revert the merge commit |
| Time/complexity | One command | One `git merge` + one `git push` |

## 3. Selected approach

**Merge `origin/main` into `feat/caregiver-path-v2`, then push the result to `main`.**

This avoids history rewriting, keeps the production branch auditable, and is the consensus best practice across Git docs, GitHub, GitLab, and CNCF/GitOps guidance. `force-with-lease` is a useful safety for personal rebased branches, but not for the production `main` branch.

## 4. Edge cases and remediation

| Edge case | Impact | Remediation |
|---|---|---|
| `main` is configured to require linear history | Merge commit would be rejected | Rebase `feat/caregiver-path-v2` onto `origin/main` and force-with-lease, or use the PR workflow if available |
| `origin/main` has changes that conflict with `feat/caregiver-path-v2` | Merge conflict | Resolve manually, run the full test suite, then commit and push |
| Direct pushes to `main` are blocked by branch protection | Push is rejected | Open a PR and merge through the GitHub UI, or ask the user to override protection |
| The merge commit triggers a production deploy workflow | Deploy to `mynaani.com` begins | Wait for the production deploy to finish, then smoke test |

## 5. Codebase conflict check

- `AGENTS.md` already requires explicit human permission for production pushes and ships to staging only. The user has explicitly asked for the production push.
- `.github/workflows` likely runs the `Deploy Production` or `Deploy` workflow on `main`. No conflicts identified.
- The feature branch `feat/caregiver-path-v2` is currently on `origin/staging` and all staging gates (unit, lint, UAT, E2E) have passed.

## 6. Gaps

- The exact branch protection rules for `origin/main` are not visible to this agent. If direct push is rejected, a PR/merge workflow or admin override is the fallback.
- A full 20-source memo was not assembled for this narrow git-operations question; the 12 sources above cover official docs, platform docs, and FAANG/industry guidance.
