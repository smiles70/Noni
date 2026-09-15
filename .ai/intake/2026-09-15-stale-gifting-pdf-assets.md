# P1 — Remove stale `gifting-ai-learning.pdf` from Cloudflare Pages deployments

## Problem

The `gifting-ai-learning.pdf` whitepaper was removed from the repository in commit `1a44978` (`feat(content): replace gift-giving whitepaper with cognitive engagement brief`) and does not exist in the local `frontend/dist/whitepapers/` build. However, both production and staging still return `HTTP 200` for:

- `https://www.mynaani.com/whitepapers/gifting-ai-learning.pdf`
- `https://staging.noni-web.pages.dev/whitepapers/gifting-ai-learning.pdf`

The new `cognitive-engagement.pdf` is served correctly, so the deployment pipeline *does* add new files. The issue is that previously-deployed files are not being removed from the active Cloudflare Pages deployment.

## Trigger

After `git rm frontend/public/whitepapers/gifting-ai-learning.pdf` and a successful `Deploy` workflow run, the old URL still responds with `200` and the old PDF content.

## Current impact

- The deprecated gift-giving whitepaper is still publicly downloadable.
- The caregiver page now links to `cognitive-engagement.pdf`, but an old, contradictory PDF remains accessible by direct URL.
- Users/caregivers who bookmarked or were emailed the old URL still receive outdated content.

## Outcome needed

1. Ensure `gifting-ai-learning.pdf` returns `404` (or `301` to `cognitive-engagement.pdf`) on production and staging.
2. Establish a process so that future `git rm` of `public/` assets is reflected in Cloudflare Pages deployments.
3. Avoid redeploying the file or serving it under a different name.

## Scope / non-goals

- In scope: Cloudflare Pages deployment behavior, `frontend/public/whitepapers/` asset lifecycle, and the `Deploy`/`Deploy Staging` GitHub workflows.
- Out of scope: changing the `cognitive-engagement` whitepaper content or modifying the caregiver page marketing copy.

## References

- Workflow: `.github/workflows/deploy.yml` (`cloudflare-pages-deploy`)
- Workflow: `.github/workflows/deploy-staging.yml`
- Live prod URL: `https://www.mynaani.com/whitepapers/gifting-ai-learning.pdf`
- Live staging URL: `https://staging.noni-web.pages.dev/whitepapers/gifting-ai-learning.pdf`
- Removed file: `frontend/public/whitepapers/gifting-ai-learning.pdf`
