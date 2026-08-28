# Intake — Curriculum UI Simplification and Noni Brand Audit

**Date:** 2026-08-28
**Process:** v9.51
**Source:** User request (session 2026-08-28)
**Scope:** `frontend/src` curriculum/navigation labels + system-wide `Noni`/`noni` brand-reference audit

---

## Trigger

Two related pieces of feedback during the mobile-readiness pass:

1. The curriculum pages present too many navigation labels (`Lessons`, `Upgrade — Modules 4 & 5`) for the geragogy-first audience (adults 55+), increasing cognitive load.
2. A brand-name drift exists between the public product name `Mynaani` and internal references to `Noni` / `noni` scattered throughout the app, configuration, and documentation.

---

## Source Artifact

- **Type:** `SourceArtifact`
- **ID:** `user-request-2026-08-28-curriculum-rebrand`
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95

---

## Persona & Journey

- **Persona ID:** `P-older-adult-learner`
- **Persona Name:** Older adult learner (55+)
- **Needs:** Calm, uncluttered navigation; consistent, trustworthy brand identity.

- **Journey ID:** `J-curriculum-browse`
- **Journey Name:** Learner opens the curriculum / lesson area

---

## Part A — Remove `Lessons` and `Upgrade — Modules` labels from curriculum

### Gap

- **Gap ID:** `GAP-A-001`
- **Description:** The `NavBar` and `CurriculumMenu` render `Lessons`, `Your account`, `Help`, and `Upgrade — Modules 4 & 5` simultaneously. On a mobile viewport this creates a cluster of competing buttons above the primary content.
- **Rubric link:** Geragogy Contract §2, §3 — cognitive load, command-like labels, max two accents.
- **Evidence:** `frontend/src/components/NavBar.tsx` lines 90–127, `frontend/src/components/CurriculumMenu.tsx` lines 220–229.
- **extraction_method:** `rule_based`
- **confidence:** 0.90

### Decision

- **Decision ID:** `DEC-A-001`
- **Statement:** Remove the `Lessons` and `Upgrade — Modules 4 & 5` labels from the curriculum context. Keep the underlying actions accessible through a single `Menu` button or the existing module list, depending on auth state.
- **extraction_method:** `human_confirmed`
- **confidence:** 0.95

### Requirements

- **Requirement ID:** `REQ-A-001`
- **Statement:** `NavBar` must not render a `Lessons` button when the user is already on a curriculum-related page.
- **Priority:** must
- **verified_by:** `Test-A-001`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

- **Requirement ID:** `REQ-A-002`
- **Statement:** `NavBar` must not render `Upgrade — Modules 4 & 5` as a visible top-level label in the curriculum view; the purchase path may remain available through a calmer, secondary CTA.
- **Priority:** must
- **verified_by:** `Test-A-002`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

- **Requirement ID:** `REQ-A-003`
- **Statement:** Navigation must remain functional after the labels are removed (the user can still reach lessons, account, and help).
- **Priority:** must
- **verified_by:** `Test-A-003`
- **extraction_method:** `rule_based`
- **confidence:** 0.95

### Acceptance Criteria

| ID | Criterion | Method |
|---|---|---|
| AC-A-001 | `Lessons` string does not appear in `NavBar` rendered output on `/lessons` or `CurriculumMenu` | E2E text search |
| AC-A-002 | `Upgrade — Modules 4 & 5` string does not appear in `NavBar` rendered output on curriculum pages | E2E text search |
| AC-A-003 | No horizontal overflow and all remaining nav targets ≥ 48 px on mobile | `e2e/responsive.spec.ts` |
| AC-A-004 | `CurriculumMenu` still lists all modules and free lessons remain tappable | Manual QA / E2E |

---

## Part B — `Noni` / `noni` brand-reference audit

### Research Method

- **Tool:** `ripgrep` across `/home/hazbyn/Noni` respecting `.gitignore`
- **Pattern:** `Noni|noni`
- **Total distinct files with matches:** 179
- **Risk classification:** user-facing, internal implementation, infrastructure, docs/ops

### Category 1 — User-facing strings and content

| File | Lines | Issue | Suggested Action |
|---|---|---|---|
| `frontend/src/components/HowItWorksDialog.tsx` | 190, 193 | Content key `what_noni_does` is rendered as a heading | Rename API key and copy to `what_mynaani_does` or neutral `what_we_do` |
| `frontend/src/api/landing.ts` | 35 | API type `what_noni_does` | Update to match content model |
| `backend/models/landing_page.py` | 44 | Backend model `what_noni_does` | Update to match API and frontend |
| `backend/content/landing_page.py` | 29 | Content object `what_noni_does` | Update |
| `frontend/src/main.tsx` | 19, 20 | `localStorage` keys `noni_progress_v1`, `noni.mock_token` are visible in user data | Decide migration or keep internal-only; do not expose in UI |

### Category 2 — Frontend CSS class names

| File | Count | Issue | Suggested Action |
|---|---|---|---|
| `frontend/src/styles.css` | 19 | `.noni-hero`, `.noni-skip-link`, `.noni-hero__overlay`, etc. | Rename to `.mynaani-hero` / `.mynaani-skip-link` or neutral `.app-hero` |
| `frontend/src/App.tsx` | 222 | `className="noni-skip-link"` | Update after CSS rename |

### Category 3 — Internal storage, events, and identifiers

| File | Lines | Issue | Suggested Action |
|---|---|---|---|
| `frontend/src/auth/AuthProvider.tsx` | 71, 112, 113 | Custom event `noni:auth-changed` | Rename to `mynaani:auth-changed` or `app:auth-changed` |
| `frontend/src/components/AuthPendingBanner.tsx` | 67 | `RETRY_STORAGE_KEY = "noni.auth_banner_retries"` | Rename; plan migration for in-flight retries |
| `frontend/src/App.tsx` | 96 | `sessionStorage.removeItem("noni.auth_banner_retries")` | Match renamed key |
| `frontend/src/api/client.ts` | 20, 21 | `MOCK_TOKEN_KEY = "noni.mock_token"`, `MAGIC_TOKEN_KEY = "noni.magic_token"` | Rename with migration strategy |
| `frontend/src/lib/progress.ts` | 13 | `KEY = "noni_progress_v1"` | Rename with migration strategy |
| `frontend/src/largeText.ts` | 5 | `KEY = "noni_large_text"` | Rename with migration strategy |
| `frontend/src/components/ErrorBoundary.tsx` | 30 | `__noni_request_id` global | Rename to `__mynaani_request_id` or `__app_request_id` |

### Category 4 — Tests and mocks

| File | Count | Issue | Suggested Action |
|---|---|---|---|
| `frontend/src/auth/__tests__/AuthProvider.test.tsx` | 4 | Uses `noni.mock_token` in assertions | Update to new key names |
| `frontend/src/api/__tests__/auth.test.ts` | 4 | Same as above | Update |
| `frontend/src/components/__tests__/AuthPendingBanner.test.tsx` | 1 | Same as above | Update |

### Category 5 — Package, project, and infrastructure identifiers

| File | Count | Issue | Suggested Action |
|---|---|---|---|
| `package.json` (root) | 1 | `name` may be `noni` | Decide if repo-wide rename is in scope |
| `frontend/package.json` | 1 | `name` may be `noni-frontend` | Decide if npm package rename is in scope |
| `pyproject.toml` | 1 | Project name `noni` | Decide if package rename is in scope |
| `docker-compose.yml` | 5 | Service names `noni-api`, `noni-db`, etc. | In-scope only if re-branding infrastructure |
| `fly.toml` | 1 | `app` name `noni` | In-scope only if re-branding infrastructure |
| `.env.example` / `infra/.env.example` | 20+ | Variables `NONI_*` / `noni_*` | Rename if secrets/dashboards allow |
| `.github/workflows/*.yml` | 14+ | Workflow variables and names use `noni` | Update to `mynaani` or neutral `app` |

### Category 6 — Process, docs, and runbooks

| File | Count | Issue | Suggested Action |
|---|---|---|---|
| `README.md` | 1 | Text references `Noni` | Update to `Mynaani` |
| `PROCESS_V9.51_SPEC.md` | 18 | Mentions `Noni` as project | Document retention or update |
| `SPRINT.md`, `PROGRESS.md`, `CONTRIBUTING.md`, `CURRENT_STATE.md` | multiple | Text references | Update if public-facing |
| `docs/**/*`, `.ai/**/*`, `.ai/process/KNOWLEDGE_GRAPH.*` | many | Documentation, ADRs, intakes, runbooks | Update if user-facing; retain historical project name in ADRs if needed |

### Decision

- **Decision ID:** `DEC-B-001`
- **Statement:** Replace user-facing and front-end internal `noni` references with `mynaani` (or neutral `app`/`mynaani` where `mynaani` is not public-facing). Do not attempt to rename infrastructure identifiers (`docker-compose`, `fly.toml`, GitHub org, Railway project, DNS) in this pass; document those as a separate infrastructure-rebrand backlog.
- **extraction_method:** `human_confirmed`
- **confidence:** 0.90

### Requirements

- **Requirement ID:** `REQ-B-001`
- **Statement:** Replace `what_noni_does` content key with `what_mynaani_does` across the full stack (backend model, content, API, frontend types, and UI).
- **Priority:** must
- **verified_by:** `Test-B-001`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

- **Requirement ID:** `REQ-B-002`
- **Statement:** Rename front-end CSS class names from `.noni-*` to `.mynaani-*` (or `.app-*`) and update all `className` references.
- **Priority:** must
- **verified_by:** `Test-B-002`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

- **Requirement ID:** `REQ-B-003`
- **Statement:** Audit and migrate `localStorage` / `sessionStorage` keys from `noni_*` to `mynaani_*` without breaking active sessions; provide fallback/clear logic for old keys.
- **Priority:** should
- **verified_by:** `Test-B-003`
- **extraction_method:** `rule_based`
- **confidence:** 0.90

- **Requirement ID:** `REQ-B-004`
- **Statement:** Rename internal event and request-id prefixes from `noni` to `mynaani` or `app`.
- **Priority:** should
- **verified_by:** `Test-B-004`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.85

- **Requirement ID:** `REQ-B-005`
- **Statement:** Update or add an ADR documenting which `Noni` references are retained (infrastructure, repo, historical ADRs) and which are migrated.
- **Priority:** should
- **verified_by:** `Test-B-005`
- **extraction_method:** `llm_inferred`
- **confidence:** 0.80

### Acceptance Criteria

| ID | Criterion | Method |
|---|---|---|
| AC-B-001 | No `Noni`/`noni` string appears in rendered UI text or public-facing class names in the landing, curriculum, account, or paywall flows | `grep` + E2E |
| AC-B-002 | `localStorage` migration preserves existing user progress and auth tokens | Unit test + E2E |
| AC-B-003 | All Playwright and Jest tests pass after renames | CI |
| AC-B-004 | Build and bundle verification pass | `npm run build` + `verify-bundle.mjs` |

---

## Out of Scope

- Production promotion (`main` branch) is not in this intake.
- Infrastructure rename (Railway project, DNS, Docker service names, GitHub org) is deferred to a separate infrastructure-rebrand backlog.
- No changes to `CONTRACT.md` or `docs/library/CONTRACT.md` global rules.

---

## Suggested Next Action

1. Create a feature branch `feat/geragogy-curriculum-rebrand` from `staging`.
2. Part A: remove `Lessons` and `Upgrade — Modules` from `NavBar` / `CurriculumMenu` and run `e2e/responsive.spec.ts`.
3. Part B: execute the `mynaani` renames in `frontend/src` with a storage-key migration strategy, then update backend content model to match.
4. Run `npm run type-check` and `npm run build` after each group.
5. Deploy to `staging` for review.

---

## Knowledge-Graph Delta

```text
SourceArtifact:user-request-2026-08-28-curriculum-rebrand  defined_by  PROCESS_V9.51_SPEC.md
Persona:P-older-adult-learner                                part_of     Journey:J-curriculum-browse
Journey:J-curriculum-browse                                  served      Epic:EPIC-geragogy-curriculum-rebrand
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-A-001
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-A-002
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-A-003
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-B-001
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-B-002
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-B-003
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-B-004
Epic:EPIC-geragogy-curriculum-rebrand                        refined_by  Requirement:REQ-B-005
Gap:GAP-A-001                                               blocks      Requirement:REQ-A-001
Gap:GAP-A-001                                               blocks      Requirement:REQ-A-002
Gap:GAP-B-001                                               blocks      Requirement:REQ-B-001
Gap:GAP-B-002                                               blocks      Requirement:REQ-B-002
Evidence:scan-noni-rebrand-2026-08-28                        evidenced_by SourceArtifact:user-request-2026-08-28-curriculum-rebrand
Decision:DEC-A-001                                          planned_by    smiles70
Decision:DEC-B-001                                          planned_by    smiles70
```
