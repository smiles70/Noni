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

## Research protocol for intakes and technical decisions

Run this protocol at the start of **any** intake, architecture decision, or
technical-direction question. Do not commit an intake, ADR, or dependency
choice until the research artifact exists and the edge-case / remediation
matrix is checked against the current codebase.

### 1. When to invoke

- Every new `.ai/intake/` or `docs/adr/` before the options section is written.
- Before selecting a library, tool, vendor, protocol, auth method, database
  pattern, deployment pattern, or observability strategy.
- When the user asks "should we use X?", "what is best practice for Y?", or
  "how do FAANG companies do Z?".
- Before changing a UI contract, API contract, or security/permissions boundary.

### 2. Source quota and quality bar

Collect **at least 20 external, verifiable, published sources** per research
question. Aim for this balance:

- **FAANG / top-tier tech engineering sources (≥5):** official engineering
  blogs, published conference talks with transcripts, open-source project docs,
  or papers authored by engineers at Meta, Google, Amazon, Netflix, Apple,
  Microsoft, Uber, Stripe, Shopify, Spotify, Airbnb, etc. GitHub repositories
  from verified corporate accounts count if they are the canonical implementation.
- **Peer-reviewed / academic / hard science (≥5):** arXiv papers with source
  links, ACM/IEEE papers, university course notes from `.edu` domains, DOI-linked
  journal articles, or references from known research labs.
- **Industry / operations / security (≥5):** NIST, OWASP, CNCF, OpenSSF, SRE
  book excerpts (official publisher pages), RFCs, ISO/ SOC2 guidance, or
  vendor-agnostic observability/security references.
- **Discussion / critique / war stories (≤5):** high-signal aggregators such as
  Hacker News front-page threads, lobste.rs, or cited Reddit r/netsec threads
  that link to primary sources. These count only if they add a verified
  counter-argument or failure story.

**Not acceptable:** unverified Medium posts, SEO listicles, anonymous Quora
answers, generated content farms, or citations without a reachable URL/DOI.

### 3. Source verification (triple-check)

1. **Reachability:** Use `webfetch` on every URL/DOI. If it 404s, redirects to a
   parked domain, or requires a login without an open abstract, discard it.
2. **Attribution:** Confirm the author, publication date, and employer/affiliation
   are visible and match the claimed expertise. For corporate blogs, confirm the
   post is under the official domain (e.g., `engineering.linkedin.com`).
3. **Cross-check:** Find at least two independent sources that corroborate the
   key claim. If only one source makes a claim, flag it as low-confidence and
   either find corroboration or downgrade the recommendation.

Every source must be cited with URL, author/organization, title, and date. The
final research memo must include a source table.

### 4. Synthesis and best-in-class selection

1. Group sources by approach/technology.
2. Identify trade-offs: latency, cost, operational burden, security surface,
   correctness, team expertise, lock-in, and migration path.
3. Choose the **best-in-class enterprise solution** for this codebase and
   team — not the newest, the shiniest, or the one the agent is most familiar
   with. Document why it is the best fit relative to the current stack
   (React/TypeScript, FastAPI, PostgreSQL, Railway, Cloudflare Pages, Stripe,
   Magic, etc.).
4. Include a short decision matrix with at least three realistic alternatives
   and a confidence level (High / Medium / Low).

### 5. Edge-case and remediation analysis

After selecting the best-in-class solution, derive the **top 30 cases and edge
cases** where the solution can cause problems. For each edge case:

- Describe the trigger condition (input, state, scale, failure mode).
- Classify the impact: functional, performance, security, cost, operational,
  user-experience, or compliance.
- Search for a remediation or mitigation from the same quality of sources.
- **Triple-check the remediation against the current codebase:** grep for
  existing handlers, tests, environment limits, deployment constraints, and
  prior intakes/ADRs. If the remediation conflicts with an existing rule in
  `AGENTS.md`, an open intake, or a pinned dependency, flag it explicitly.

Write the edge-case / remediation matrix in the research memo.

### 6. Research artifact

Save the output as `.ai/research/YYYY-MM-DD-<topic>.md` (or the repo's
research directory). The memo must contain:

- Research question / decision to be made
- Source table (URL, author/org, title, date, relevance)
- Decision matrix and selected approach with confidence
- Edge-case / remediation matrix (top 30)
- Codebase conflict check and any blockers
- Gaps requiring user input or further investigation
- Link to the related intake or ADR

### 7. Non-goals and escalation

- Do **not** skip research because a solution "feels standard".
- Do **not** cite sources that cannot be verified.
- Do **not** treat Stack Overflow or generated AI summaries as primary evidence.
- If fewer than 20 high-quality sources can be found, or if no enterprise-grade
  option exists for the constraints, stop and ask the user how to proceed before
  writing the recommendation.
