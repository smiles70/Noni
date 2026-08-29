# Preflight — Geragogy Curriculum Rebrand

**Process:** v9.51
**Intake:** `.ai/intake/2026-08-28-curriculum-simplification-noni-rebrand-intake.md`
**Decision:** `DEC-A-001`, `DEC-B-001`
**Target:**
- Remove `Lessons` and `Upgrade — Modules` labels from curriculum views.
- Replace front-end user-facing `Noni`/`noni` references with `Mynaani`/`mynaani` and document deferred infrastructure renames.
- Update the knowledge graph after each batch.

---

## Current State

- `staging` already contains the mobile hero art-direction feature.
- `REQ-B-001` (`what_noni_does` → `what_mynaani_does`) was already implemented directly on `staging` and deployed. It is **not** part of this preflight's work and will be treated as a pre-existing baseline.
- `.ai/intake/2026-08-28-curriculum-simplification-noni-rebrand-intake.md` is already in `staging`.

---

## Branching and Conflict-Avoidance Strategy

1. **Integration branch:** `staging`.
2. **Feature branch:** `feat/geragogy-curriculum-rebrand` cut from `staging`.
3. **Batch commits happen only on the feature branch.**
4. **No pushes to `main`.**
5. **Final merge:** `feat/geragogy-curriculum-rebrand` → `staging` only after the batch passes the `PREFLIGHT` and `BUILD` gates.
6. **No deploys on intermediate commits.**

---

## Batch Plan

### Batch 0 — Branch and commit the preflight

| Step | Action | Output |
|---|---|---|
| 0.1 | `git checkout staging` | clean `staging` |
| 0.2 | `git pull --ff-only origin staging` | up to date |
| 0.3 | `git checkout -b feat/geragogy-curriculum-rebrand` | feature branch |
| 0.4 | Commit `.ai/process/PREFLIGHT_GERAGOGY_CURRICULUM_REBRAND.md` | preflight in git |
| 0.5 | `git status` | only intended files staged |

**Gate:** `PREFLIGHT` — workspace clean, only the preflight committed, branch is `feat/geragogy-curriculum-rebrand`.

---

### Batch 1 — Remove `Lessons` and `Upgrade — Modules` labels from curriculum UI

**Scope:** `NavBar.tsx`, `CurriculumMenu.tsx`, `LessonRenderer.tsx` (comment only).

| Step | Action | Output |
|---|---|---|
| 1.1 | In `NavBar.tsx`, remove the `Lessons` button from the curriculum view and/or conditionally suppress it when `onOpenMenu` is not needed. | no `Lessons` label in curriculum NavBar |
| 1.2 | In `NavBar.tsx`, remove the `Upgrade — Modules 4 & 5` button from the free track's NavBar when on curriculum; keep `onContinuePaid` for a calmer secondary CTA if required. | no `Upgrade — Modules` label in curriculum NavBar |
| 1.3 | In `CurriculumMenu.tsx`, consider removing the `<h1>Lessons</h1>` or rephrasing to `Course overview`. | heading aligned with geragogy |
| 1.4 | Update `e2e/responsive.spec.ts` or add a targeted E2E assertion that `Lessons` and `Upgrade — Modules` do not render on `/lessons`. | test coverage |
| 1.5 | Commit changes | `feat/geragogy-curriculum-rebrand` + Part A |

**Gate:** `BUILD` — `npm run type-check`, `npm run build`; no `Lessons`/`Upgrade — Modules` strings in `dist`.

---

### Batch 2 — Rename front-end CSS classes from `.noni-*` to `.mynaani-*`

**Scope:** `frontend/src/styles.css`, `frontend/src/App.tsx`.

| Step | Action | Output |
|---|---|---|
| 2.1 | Replace all `.noni-` CSS class selectors in `styles.css` with `.mynaani-` (or neutral `.app-`). | no `.noni-*` rules |
| 2.2 | Update `App.tsx` `className="noni-skip-link"` to `mynaani-skip-link`. | class references match |
| 2.3 | Build and verify bundle | build passes |
| 2.4 | Commit changes | `feat/geragogy-curriculum-rebrand` + CSS rebrand |

**Gate:** `BUILD` + visual smoke: landing skip-link still works, no class-name regressions.

---

### Batch 3 — Rename internal storage and event keys (with migration)

**Scope:** `frontend/src/main.tsx`, `frontend/src/lib/progress.ts`, `frontend/src/largeText.ts`, `frontend/src/api/client.ts`, `frontend/src/components/App.tsx`, `frontend/src/auth/AuthProvider.tsx`, `frontend/src/components/AuthPendingBanner.tsx`, `frontend/src/components/ErrorBoundary.tsx`, and their tests.

| Step | Action | Output |
|---|---|---|
| 3.1 | Choose a new prefix, e.g. `mynaani_` and `mynaani.`. | prefix decision |
| 3.2 | Add a migration helper that reads old `noni_*` / `noni.*` keys and writes new `mynaani_*` / `mynaani.*` keys on first load, then removes the old keys. | user data preserved |
| 3.3 | Update all constant key names, event names, and `__noni_request_id` global. | no `noni` internal identifiers |
| 3.4 | Update `AuthProvider.test.tsx`, `auth.test.ts`, `AuthPendingBanner.test.tsx` to use new keys. | tests pass |
| 3.5 | Commit changes | `feat/geragogy-curriculum-rebrand` + storage/event rebrand |

**Gate:** `TEST` — `npm run test` (Vitest) passes; `localStorage` migration tested.

---

### Batch 4 — Update backend content model and tests (already partially done)

**Scope:** `backend/models/landing_page.py`, `backend/content/landing_page.py`, `backend/tests/test_landing_page.py`, `docs/api/openapi.yaml`.

| Step | Action | Output |
|---|---|---|
| 4.1 | Verify `what_noni_does` is fully replaced by `what_mynaani_does` in the backend model, content, tests, and OpenAPI. | consistent naming |
| 4.2 | Run the backend `pytest` test for landing page. | `test_landing_page.py` passes |
| 4.3 | Commit any remaining OpenAPI or test updates | `feat/geragogy-curriculum-rebrand` + backend aligned |

**Gate:** `BACKEND TEST` — `pytest backend/tests/test_landing_page.py -q` passes.

**Note:** `Batch 4` is expected to be a verification-only batch because `REQ-B-001` is already implemented. If the baseline is incomplete, this batch captures the remainder.

---

### Batch 5 — Package and project identifiers (optional, with ADR)

**Scope:** `package.json`, `frontend/package.json`, `pyproject.toml`, `.env.example`, `infra/.env.example`, `.github/workflows/*.yml`.

| Step | Action | Output |
|---|---|---|
| 5.1 | Create an ADR documenting which identifiers are renamed and which remain `noni` for infrastructure. | `docs/decisions/00XX-brand-name-migration.md` |
| 5.2 | Update package/project names if the user approves the scope. | names aligned |
| 5.3 | Update workflow variable names and `.env.example` keys. | env keys aligned |
| 5.4 | Commit changes | `feat/geragogy-curriculum-rebrand` + project identifiers |

**Gate:** `ADR` — ADR exists and is referenced from the intake.

---

### Batch 6 — Process docs and knowledge-graph update

**Scope:** `.ai/intake/...`, `.ai/process/KNOWLEDGE_GRAPH.json`, `.ai/process/KNOWLEDGE_GRAPH.md`, relevant `.ai/process/` files.

| Step | Action | Output |
|---|---|---|
| 6.1 | Update the intake to mark completed batches and acceptance criteria. | intake current |
| 6.2 | Update `KNOWLEDGE_GRAPH.json` and `KNOWLEDGE_GRAPH.md` with new `Evidence`, `Capability`, and `Test` nodes. | graph current |
| 6.3 | Commit changes | `feat/geragogy-curriculum-rebrand` + graph update |

**Gate:** `KNOWLEDGE GRAPH` — the canonical graph reflects the new `Capability` nodes.

---

### Batch 7 — Merge to `staging` and deploy

| Step | Action | Output |
|---|---|---|
| 7.1 | `git checkout staging` | on `staging` |
| 7.2 | `git merge feat/geragogy-curriculum-rebrand --no-ff` | merge commit |
| 7.3 | Push `staging` to `origin/staging` | `Deploy Staging` triggers |
| 7.4 | Wait for workflow success; note new Cloudflare preview URL. | new preview URL |
| 7.5 | Update `FRONTEND_URL` and `CORS_ORIGINS` in Railway staging. | backend allows new origin |
| 7.6 | `curl /health` and spot-check `/lessons`. | staging smoke pass |

**Gate:** `STAGING SMOKE` — `/health` 200, no `Noni`/`noni` strings in rendered UI, no `Lessons`/`Upgrade — Modules` labels in curriculum view.

---

## Rollback Plan

- **Before Batch 7:** delete `feat/geragogy-curriculum-rebrand`; `staging` and `main` are untouched.
- **After Batch 7 before `main` merge:** revert the merge commit on `staging` and re-deploy; the pre-existing `what_mynaani_does` rename will also need to be considered.
- **After `main` merge:** open a follow-up `feat/revert-noni-rebrand` branch if needed.

---

## Knowledge-Graph Delta

```text
PREFLIGHT:geragogy-curriculum-rebrand   derived_from   Intake:2026-08-28-curriculum-simplification-noni-rebrand
PREFLIGHT:geragogy-curriculum-rebrand   planned_by     smiles70
PREFLIGHT:geragogy-curriculum-rebrand   owned_by       Devin
Batch:1                                 refines        Requirement:REQ-A-001
Batch:1                                 refines        Requirement:REQ-A-002
Batch:1                                 refines        Requirement:REQ-A-003
Batch:2                                 refines        Requirement:REQ-B-002
Batch:3                                 refines        Requirement:REQ-B-003
Batch:3                                 refines        Requirement:REQ-B-004
Batch:4                                 refines        Requirement:REQ-B-001
Batch:5                                 refines        Requirement:REQ-B-005
Batch:6                                 updates        Evidence:scan-noni-rebrand-2026-08-28
Batch:7                                 verified_by    StagingSmoke
```
