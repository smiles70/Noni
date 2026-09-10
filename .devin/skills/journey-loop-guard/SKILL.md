---
name: journey-loop-guard
description: >-
  Run whenever a change touches a curriculum end-state, paywall,
  purchase-success, purchase-cancel, gift-redemption, or progress-resume
  surface. Runs a full analysis → validation → report → remediation plan and
  verifies that routing respects an active paid entitlement without creating
  paywall/purchase loops, reset-to-free-track regressions, or cross-device
  progress regressions.
---

# Journey loop and paywall guard (super prompt)

This skill applies to any application where users move between a free tier, a
paywall, a paid tier, purchase success/cancel, gift redemption, or progress
resume. It is app- and codebase-agnostic: drop it into a repo and run it from
analysis through to a findings report and a remediation plan.

## When to invoke

Invoke this guard when the task touches any of the following surfaces:

- Free-track end-of-track CTAs or `onSequenceComplete` / completion handlers.
- Paywall/upsell pages that offer a "Buy" or "Continue" CTA.
- Purchase success/cancel pages and their primary/secondary CTAs.
- Gift redemption success CTAs.
- Progress resume helpers, `localStorage` / `sessionStorage` progress, or any
  `goFree` / `goPaid` / `goCurriculum`-style routing function.
- Any new route, CTA, or state change that can move a user from free to paid,
  paid to free, or from a purchase to a curriculum.

Replace `<app>` / `<free-tier>` / `<paid-tier>` / `<paywall>` with the actual
names in the target repository.

---

## Phase A — Analyze the current state

1. **Map the surfaces**
   - Locate every component, page, or controller that handles:
     - completion of the free tier
     - the paywall / upsell surface
     - purchase success and purchase cancel
     - gift or invite redemption
     - resume / continue learning
   - For each surface, record the primary and secondary CTAs and the
     destination route they trigger.

2. **Locate the sources of truth**
   - `<entitlement-source>`: where does the app know whether the user already
     owns the paid product? (e.g., `/api/me/entitlements`, a DB check, a token,
     a Stripe webhook outcome, a `Purchase` record.)
   - `<progress-source>`: where is the user's progress stored? (e.g.,
     `localStorage`, `sessionStorage`, server-side `Progress` table, a cache.)
   - `<auth-source>`: how does the app know whether the user is authenticated?

3. **Trace the routes**
   - For each CTA, trace: *current user state → CTA → destination → what happens
     next if the user is already entitled / not entitled / signed out*.
   - Flag any destination that can lead back to the paywall after a successful
     purchase or redemption.

---

## Phase B — Validate

### B.1 Journey logic validation

Run the journey graph validator over the realistic user-journey graph
(including back-edges and cross-links). Produce a report in this form:

```markdown
# Journey logic validation report

- Journeys checked: <N>
- P0: <n>, P1: <n>, P2: <n>, P3: <n>

## Findings

- **P1** — Cycle (SCC): <list of stages in the strongly connected component>
```

A P1 cycle is acceptable if it is **intentional** and has clear off-ramps.
A P1 cycle that contains a paywall → purchase → paywall loop is **not**
acceptable.

### B.2 Persona / journey mapping validation

Run the persona and anti-persona validator. Produce a report in this form:

```markdown
# Persona/Journey validation report

- Persona slugs: <N>
- Journey slugs: <N>
- P0: <n>, P1: <n>, P2: <n>, P3: <n>

## Findings

- No findings.  OR
- **P1** — <persona> is not represented on <journey> ...
```

### B.3 UX / accessibility validation (MARTY-style)

Run automated contrast, heading, and semantic-role checks against the touched
surfaces. Record any P0/P1 findings.

---

## Phase C — Findings report

Compile the evidence into a findings report with this taxonomy:

| Severity | Definition | Example |
|---|---|---|
| **P0** | User cannot complete a critical task; data or security issue. | Already-entitled learner is forced to purchase again. |
| **P1** | Significant friction, unintentional cycle, or broken promise. | Free-track end always routes to paywall, even when entitled. |
| **P2** | Missing guard, missing test, or poor UX that may cause loops. | Progress is local-only but the UI implies cross-device resume. |
| **P3** | Cosmetic or documentation gap. | Contrast passes but copy uses urgency language. |

---

## Phase D — Remediation / intake plan

If the implementation is **not** yet authorized, produce an intake document with:

1. **Problem statement** — which user sees which failure mode.
2. **Persona / ICP table** — affected goals and frustrations.
3. **Current-state evidence** — file paths, line numbers, and snippets.
4. **Options evaluated** — at least "leave as-is", "heuristic", and
   "source-of-truth" approaches.
5. **Selected architecture** — explicit entitlement endpoint, hook placement,
   frontend checks, and cross-device progress scope.
6. **Design decisions** — token choices, CTA labels, error handling.
7. **Epic / Block / Rack plan** — who owns what and the deliverables.
8. **Test plan** — unit, journey-contract, and E2E coverage.
9. **Acceptance criteria** — measurable exit state.
10. **Rollback / operational notes** — how to revert and how to monitor.

If the implementation **is** authorized, proceed to Phase E and F.

---

## Phase E — Implementation guard checklist

For every change that this guard applies to:

1. **Entitlement-aware free-track completion**
   - If the user already has the paid product, the end-of-free-track CTA must
     not route to a paywall.
   - It should route directly to the paid track entry point.
   - If the frontend cannot check entitlement, the parent or context that
     supplies the entitlement must be wired before the route is merged.

2. **Entitlement-aware paywall surface**
   - If the user already has the paid product, the paywall must not show only a
     "Buy" CTA.
   - It should offer a "Continue to paid track" CTA that routes to the paid
     track entry point.

3. **Resume helpers are not used after access is granted**
   - Never use a progress-based resume function (e.g., `goFree`) in a
     post-purchase, post-redemption, or post-grant flow.
   - Those helpers use local-only progress and will send an entitled user with
     no paid progress back to the free track.
   - After purchase / redemption / grant, route straight to the paid track
     entry point.

4. **Purchase cancel surface does not loop entitled users**
   - A purchase cancel page should not route an already-entitled user back to
     the paywall.
   - The secondary CTA should route to a safe, non-looping destination such as
     the home page or the paid track.

5. **Progress sync is explicit and documented**
   - If a feature depends on progress resuming across devices, the progress
     must be stored server-side.
   - If progress is local-only (`localStorage`, `sessionStorage`, etc.), the
     code and any resume surface must not imply cross-device resume.

---

## Phase F — Evidence required before merge

For every change that this guard applies to, the implementation must ship:

- A **journey-contract unit test** covering each primary CTA route for:
  - an entitled user
  - an unentitled user
  - a signed-out / anonymous user, if the surface is public
- An **E2E test** (Playwright or equivalent) that reproduces the full end-to-end
  flow from the surface to the destination.
- An updated `AGENTS.md` or project rules file if a new loop class is
  discovered.
- A re-run of the Phase B validators showing **P0 = 0 and P1 = 0** for the
  touched journeys.

---

## Exit criteria

- All entitlement-aware routes are decided by a backend or auth source of
  truth, not by `localStorage` heuristics or hardcoded CTAs.
- No post-purchase, post-redemption, or post-grant flow routes an entitled user
  back to a paywall or the free track.
- Journey logic and persona validators pass with P0 = 0 and P1 = 0.
- MARTY / UX checks pass with P0 = 0 and P1 = 0.
- Unit and E2E tests are green.
- The remediation or intake document is committed under `.ai/intake/` or the
  equivalent intake directory for the repo.
