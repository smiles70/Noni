# Intake — DEPLOY-ENV-SYNC-001: deploy pipelines do not target Railway environments

**Date:** 2026-09-07 · **Process:** v9.51 · **Class:** infrastructure defect (deploy sync) · **Severity:** HIGH

## Defect (verified, 5-check evidence)

- `deploy.yml` (main push) and `deploy-staging.yml` (staging push) both run
  `railway up -y --detach --service noni-api` with the same `RAILWAY_TOKEN`
  and **no `--environment` flag**.
- Result: every main-push "Deploy" run redeploys the **staging** environment.
  Production `noni-api` has had no deploy since 2026-08-29.
- Evidence: Railway deployment list (prod: Aug 29 / staging: Sep 7);
  prod OpenAPI exposes 59 routes vs staging 72 (missing `/admin/*`,
  `/billing/org/{id}/dashboard`, `/me/delete`, `/me/export`,
  `/curriculum/progress`); prod `whoami-check` 404 vs staging 200.
- Frontend is unaffected: `www.mynaani.com` → Cloudflare Pages deploys
  correctly on main push (bundle hash matches fresh main build).

## Impact

- New backend API surface unreachable in production while frontend calls it.
- Silent drift: "Deploy success" on main ≠ production deployed — a
  false-green deploy signal. Not tolerable for enterprise standard.

## Requirements (draft — to be finalized after research protocol)

- R1: Staging and production deploys must explicitly target their env.
- R2: Production deploy must be a deliberate promotion of a
  staging-verified build, not an independent rebuild.
- R3: Deploy must be verifiable — post-deploy smoke asserts the deployed
  route surface/version, not just "railway up returned 0".
- R4: Deploy failure or env mismatch must be loud (fail the workflow).
- R5: No shared-credential ambiguity — env selection must not depend on
  token default-env binding alone.

## Research protocol

≥10 verifiable published sources required before solution is fixed.
See "Research log" below (appended after research).

## Research log — verified sources

1. **Railway CLI docs — `railway up`** https://docs.railway.com/cli/up — `-e/--environment` exists and *"defaults to linked environment"* — the literal root cause.
2. **Railway CLI — deploying** https://docs.railway.com/cli/deploying — `railway up --environment staging`; env targeting is a first-class, supported flag.
3. **Railway CLI global options** https://docs.railway.com/cli/global-options — env by name or ID; also `railway deployment list` for verification.
4. **GitHub Actions — Managing environments** https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments — required reviewers + **environment-scoped secrets** (job can't read secrets until protection rules pass).
5. **GitHub Actions — Deployments and environments** https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments — protection rules incl. branch restriction and custom rules.
6. **DORA — Continuous Delivery capability** https://dora.dev/capabilities/continuous-delivery/ — the pipeline owns check-in→release; VCS for all production artifacts.
7. **AWS Well-Architected DevOps Guidance DL.CD.4** https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/dl.cd.4-automate-the-entire-deployment-process.html — automate every stage; optional manual approval gates only; humans must not interfere with artifact integrity.
8. **Humble & Farley — The Deployment Production Line** https://continuousdelivery.com/wp-content/uploads/2011/04/deployment_production_line.pdf — the same binary carries OK/fail stamps through stages; automate deploys to all envs AND test the environments themselves.
9. **Weave GitOps — Promoting applications** https://docs.gitops.weaveworks.org/docs/pipelines/promoting-applications/ — promotion across consecutive environments (PR or notification strategy).
10. **Artifact promotion — DevOpsNess** https://www.devopsness.com/blog/artifact-promotion-instead-of-rebuilds-the-release-control-pattern-that-stopped-drift-2026-03-26 — "build once, verify once, promote the exact artifact"; per-env rebuilds cause silent drift (exactly our symptom).
11. **Post-deployment verification — KindaTechnical / CI-CD guide** https://cicd.ariefw.com/articles/4-7-what-happens-after-deploy-why-your-pipeline-isnt-done-yet/ — a deploy is not complete when code is running but when verified running correctly; health check alone is necessary but not sufficient; checks must be automated and loud.

## Determination (final solution)

Consensus across sources: **explicit env targeting + environment-scoped credentials + protection gate + automated post-deploy verification.** Artifact-promotion-by-digest is the ideal end-state (source 10) but requires a registry-based deploy model — recorded as Phase 2, not blocking.

### Changes

1. `deploy-staging.yml`: `railway up --environment staging`; job `environment: staging`.
2. `deploy.yml`: `railway up --environment production`; job `environment: production`.
3. Tokens become GitHub **environment secrets**: `RAILWAY_TOKEN_STAGING` (staging env) / `RAILWAY_TOKEN_PRODUCTION` (production env) — job cannot read the wrong token even if flags drift.
4. GitHub environment `production` gets **required reviewer = owner** + branch restriction `main` — prod deploy becomes a deliberate promotion gate (AGENTS.md rule encoded in infrastructure, not just convention).
5. Both workflows gain a post-deploy **verification step**: poll `/health` until 200, then assert the OpenAPI surface contains a sentinel route (`/api/v1/admin/whoami-check` present on staging build ≥72 paths). Loud failure = workflow fails.
6. `deploy.yml` additionally verifies prod smoke: `whoami-check` returns 200 (route exists) not 404.
