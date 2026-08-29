# Preflight — Mobile Hero Card Transparency

**Process:** v9.51
**Intake:** `.ai/intake/2026-08-29-hero-card-transparency-intake.md`
**Decision:** `DEC-001`
**Target:** Change the mobile hero card `backgroundColor` in `LandingPage.tsx` to `rgba(250, 250, 248, 0.5)` and verify build.

---

## Current State

- `staging` contains the completed geragogy rebrand and Railway deploy fix.
- `main` has been promoted and the production deploy is green.
- `.ai/intake/2026-08-29-hero-card-transparency-intake.md` is committed to `staging`.

---

## Branching Strategy

1. **Integration branch:** `staging`.
2. **Feature branch:** `feat/hero-card-transparency` cut from `staging`.
3. **No pushes to `main`.**
4. **Final merge:** `feat/hero-card-transparency` → `staging` only.

---

## Batch Plan

### Batch 0 — Branch and commit the preflight

| Step | Action | Output |
|---|---|---|
| 0.1 | `git checkout staging` | on `staging` |
| 0.2 | `git pull --ff-only origin staging` | up to date |
| 0.3 | `git checkout -b feat/hero-card-transparency` | feature branch |
| 0.4 | Commit `PREFLIGHT_HERO_CARD_TRANSPARENCY.md` | preflight in git |

---

### Batch 1 — Change mobile hero card transparency

| Step | Action | Output |
|---|---|---|
| 1.1 | In `frontend/src/components/LandingPage.tsx`, change mobile `cardStyle` `backgroundColor` from `rgba(250, 250, 248, 0.65)` to `rgba(250, 250, 248, 0.5)` | code change |
| 1.2 | Run `npm run type-check` and `npm run build` | pass |
| 1.3 | Commit | `feat/hero-card-transparency` |

---

### Batch 2 — Merge to `staging` and deploy

| Step | Action | Output |
|---|---|---|
| 2.1 | `git checkout staging` | on `staging` |
| 2.2 | `git merge feat/hero-card-transparency --no-ff` | merge commit |
| 2.3 | Push `staging` | `Deploy Staging` triggers |
| 2.4 | Verify deploy green and new preview URL | green run |

---

## Rollback Plan

- Before Batch 2: delete `feat/hero-card-transparency`; `staging` and `main` are untouched.
- After Batch 2: revert the merge commit on `staging` if needed.

---

## Knowledge-Graph Delta

```text
PREFLIGHT:hero-card-transparency   derived_from   Intake:2026-08-29-hero-card-transparency
PREFLIGHT:hero-card-transparency   planned_by     smiles70
PREFLIGHT:hero-card-transparency   owned_by       Devin
Batch:1                            refines        Requirement:REQ-001
Batch:1                            refines        Requirement:REQ-002
Batch:2                            verified_by    StagingSmoke
```
