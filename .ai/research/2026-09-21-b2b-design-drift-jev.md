# Research memo — B2B design drift inventory + Jev gate (PS-BID17-020)

Proportionate-scope verification memo (defect triage; deviation from the
≥20-source protocol recorded per the defect fast-path — this is a codebase
verification, not a technology decision).

## Method

1. Route inventory from `App.tsx` — communities-path surfaces mapped to
   components.
2. Scope verification via git: bid-17 commits (8a4629c + PS-BID17-001..012
   fixes) touched CaregiverPage, ForCommunitiesPage, tokens.ts, footer,
   SourcesPage only. `git show --stat` confirms.
3. Design marker census per component: `MARKETING` token refs, charcoal
   hero, proof band, uppercase register.
4. Jev gate (`jev-1.13.0`, `POST /v1/systemone`, Bearer auth): 9 typed
   questions — 7 noul, 1 choice, 1 score — state = the inventory above.
   Raw pack: `/tmp/jev-design-drift.json`.

## Jev results

Consistency scores 0.05–0.07 across all four untouched pages → drift is
real. Exclusion likely intentional (0.66 — bid-17 was a scoped phase-2).
Drift is user-visible (0.84) and forms a trust seam on the conversion
path (0.75). Recommended scope: forms-only (0.66). Severity:
moderate-trust-risk (0.83).

## Conclusion

User-visible, intentional-in-scope but genuine drift. The forms pages
(`/partners`, `/contact`) are the highest-value fix per Jev; `/c/:slug`
and `/org` have persona-structural reasons to differ (partner-branded
doorway, auth-gated ops UI). Owner scope decision required.
