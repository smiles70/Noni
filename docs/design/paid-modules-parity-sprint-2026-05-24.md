# Sprint Plan — Paid Modules (M4 + M5) Parity with Free Tier

**Date opened:** 2026-05-24
**Status:** Planned. **Do not execute** without explicit approval.
**Predecessors:**
  - ADR 0017 (Module 4 — Claude Skills)
  - ADR 0020 (Module 5 — Claude Agents from Skills)
  - ADR 0021 (Pricing & Tiering)
  - `docs/design/frontend-auth-geragogy-sprint-2026-05-18.md`
**Authority:** `docs/library/CONTRACT.md` (P1) and
`docs/library/IDD-2026-cognitively-protective-iscs.md` (P2),
adopted by ADR 0019.

---

## 1. Why this sprint exists

A 2026-05-24 audit confirmed that the paid tier (Modules 4 + 5) does
**not** match the free tier (Modules 1–3) in design or interaction
density. The paywall is wired correctly; the post-purchase surface is
not. Concretely:

| Capability                                            | Free (M1–M3) | Paid (M4–M5) |
| ----------------------------------------------------- | ------------ | ------------ |
| Multi-page lesson (`LessonResponse.pages`)            | ✅ 1–5 pages | ❌ 1 page (`ApprovedUnit.ui_state`) |
| Page types (recap / context / principle / example / retrieval) | ✅ all five  | 🟡 type permits, no loader delivers |
| Retrieval question + telemetry                        | ✅           | ❌ `RetrievalChoiceRecord.module: 1|2|3` |
| Resume / progress within a unit                       | ✅ `pageIdx` | ❌ no renderer to resume |
| Previous button across pages and units                | ✅           | ❌           |
| Indicator: "Module X · Lesson Y of N · Page Z of M"   | ✅           | ❌           |
| Renderer mounted in the React tree                    | ✅           | ❌ `loadPaidUnit` has tests but **zero callers** |
| Menu of paid modules                                  | ➖ free only | ❌ "intentionally absent" per `api/curriculum.ts:200-202` |

The geragogy contract grades the free path **A+** and the paid path
**F (incomplete)** — not for contract violations but because the
surface does not yet exist. An 80-year-old who pays for "Modules 4 &
5" and lands on a single-page render after a multi-page free
experience will feel cheated regardless of content quality.

This sprint closes the parity gap. It does **not** alter pricing,
entitlement plumbing, content authoring, or curriculum substance —
all of those remain governed by ADRs 0017, 0020, 0021.

---

## 2. Non-goals

- Authoring new lesson content for M4/M5. Content is owned by the
  curriculum sprints under ADR 0017 / 0020.
- Changing the entitlement gate. The 402 paywall handshake in
  `loadPaidUnit` is correct and stays.
- Adding any new V1 component. Every parity item reuses existing
  CONTRACT §I.D inventory entries.
- Changing free-tier behaviour. Free path is the reference; paid path
  must conform to it, not the other way around.

---

## 3. Inventory of planned changes

Each row is a discrete, independently verifiable work item. Order is
not strict but later rows depend on earlier ones; an executor should
treat P1 → P9 as a topological sort.

| #   | Item | Contract / ADR anchor | Current state | Target state | Files touched | Acceptance check | Risk / blocker |
| --- | ---- | --------------------- | ------------- | ------------ | ------------- | ---------------- | -------------- |
| **P1** | **Backend: paid lesson endpoint** | ADR 0017 §3, ADR 0020 §3 | Only `/api/curriculum/module-{4,5}/units/{id}` exists (single page, gated by 402). | Add `/api/curriculum/module-{4,5}/units/{id}/lesson` returning `LessonResponse` (multi-page) with the same 402 paywall handshake. | `backend/api/routes/curriculum.py`, `backend/services/curriculum_loader.py` | `curl -H 'Authorization: Bearer …' /api/curriculum/module-4/units/module4-unit-1/lesson` returns either 402 with `billing.purchase_required` or 200 with `pages: CurriculumPage[]`. New pytest under `backend/tests/test_paid_lesson_endpoint.py`. | None — mirrors the free `/lesson` endpoint exactly. |
| **P2** | **Backend: paid retrieval telemetry** | ADR 0009 (rich audit telemetry); CONTRACT §IV.B telemetry-only | `POST /api/curriculum/retrieval-choice` accepts `module: 1|2|3|4|5` already on the wire but the type is fenced on the frontend. Verify backend accepts and persists. | Backend explicitly accepts `module: int in {1..5}`; pytest covers a paid retrieval choice round-tripping into the audit table. | `backend/api/routes/curriculum.py`, `backend/models/audit.py` (verify schema), `backend/tests/test_retrieval_choice.py` | Pytest: POST with `module: 4` returns 200 and an audit row exists. | If schema enforces `module<=3` anywhere, this becomes a migration (low risk — additive). |
| **P3** | **Frontend API: widen the type fences** | CONTRACT §VII (predictability); ADR 0021 (pricing/tiering) | `api/curriculum.ts:143-149` types `LessonResponse.module: 1|2|3`. `:174-176` types `RetrievalChoiceRecord.module: 1|2|3`. `:117-134` provides `loadFreeUnit` only. | (a) Widen `LessonResponse.module` and `RetrievalChoiceRecord.module` to `1|2|3|4|5`. (b) Add `loadPaidLesson(module: 4|5, unitId)` that returns `LoadLessonResult = ok | paywall | error` mirroring `loadPaidUnit`'s discriminated shape. | `frontend/src/api/curriculum.ts`, `frontend/src/api/__tests__/curriculum.test.ts` | New unit tests cover paid 200 / 402 / 500 paths exactly as `loadPaidUnit` does. Existing free tests still pass. | None. |
| **P4** | **Frontend: extract `LessonRenderer` core** | CONTRACT §I.D (one renderer surface per state); §VII reversibility | `CurriculumRenderer.tsx` hardcodes `FREE_SEQUENCE` and calls `loadFreeLesson` directly. The Indicator, Previous button, resume logic, retrieval flow, RenderGuard proposal are all interleaved with free-only state. | Extract a `LessonRenderer` that takes (a) an ordered `sequence` of `{module, unitId}`, (b) a `loadLesson(module, unitId)` function returning `LoadLessonResult`, (c) callbacks `onSequenceComplete`. All UX (Indicator, Previous, retrieval, resume, BlockedLoad, PendingBanner, proposal accounting) lives in this core. `CurriculumRenderer` becomes a thin wrapper that supplies `FREE_SEQUENCE` + `loadFreeLesson` adapted to `LoadLessonResult`. | `frontend/src/components/curriculum/LessonRenderer.tsx` (new), `frontend/src/components/CurriculumRenderer.tsx` (slimmed), `frontend/src/components/curriculum/PageTypes.tsx` (no change expected) | Visual + interactive parity — free flow is byte-identical to today after the refactor. Playwright recordings of M1U1 → M1U2 transitions match pre-refactor. | Refactor risk; mitigated by leaving `CurriculumRenderer` as the only public entrypoint and shipping P4 alone before P5. |
| **P5** | **Frontend: `PaidLessonRenderer` wrapper** | ADR 0017, 0020; CONTRACT §I.D | No paid renderer exists in the tree. | New `PaidLessonRenderer` constructed analogously to the free wrapper: provides a hard-coded `PAID_SEQUENCE` (M4 then M5 unit IDs), wraps `loadPaidLesson` to surface `paywall` results to App.tsx, otherwise delegates to `LessonRenderer` (P4). | `frontend/src/components/PaidLessonRenderer.tsx` (new), `frontend/src/App.tsx` (route + entitlement guard) | Manual: with a fake `entitlement_active=true` user, navigating to the paid view shows M4U1 page 1 of N with the same Indicator + Previous + retrieval pattern as free. Without entitlement, `loadPaidLesson` → `paywall` and App routes to `PaywallPage`. | Entitlement gate must be re-checked on every page boundary in case it lapses mid-session — `loadPaidLesson` already does this, so the renderer just observes `kind: "paywall"` and routes out gracefully. |
| **P6** | **Resume across paid + free** | CONTRACT §VII confidence-preserving | `lib/progress.ts` already types `Progress.module: 1..5`. `FREE_SEQUENCE` covers 1–3. There is no `PAID_SEQUENCE`. The renderer's `findIndex` on saved progress will return -1 for a paid module and silently send the user back to M1U1. | Add `PAID_SEQUENCE` constant. `LessonRenderer` (from P4) accepts the active sequence; resume falls back to the head of the *active* sequence, not the global head. Free→paid handoff after purchase resumes at M4U1P1 with no localStorage cross-talk. | `frontend/src/lib/progress.ts`, `frontend/src/components/PaidLessonRenderer.tsx`, unit tests in `lib/__tests__/progress.test.ts` | Unit: write paid progress, reload, assert resume position; write free progress, switch to paid, assert paid resume independent. | None. |
| **P7** | **Curriculum menu surfaces paid modules** | CONTRACT §III state transparency; ADR 0021 (pricing) | `api/curriculum.ts:200-202`: *"Modules 4+ are paid and intentionally absent from the payload; do not infer their presence from the menu UI."* That comment will become stale. | Backend `/api/curriculum/menu` returns paid modules with a `gated: true` flag and a `unlock_action: "upgrade"` discriminator. `CurriculumMenu` renders them visibly but with a muted treatment + a "Modules 4 & 5 — unlock to begin" affordance that delegates to `onContinuePaid`. | `backend/api/routes/curriculum.py` (menu builder), `frontend/src/api/curriculum.ts` (`MenuModule.gated?: boolean`), `frontend/src/components/CurriculumMenu.tsx` | Manual: signed-out user sees the gated section with the upgrade affordance; signed-in entitled user sees them as enterable. Render-guard proposal accounting updated for the +1 highlighted recommendation if any. | If business prefers paid modules stay hidden until purchase, this item is dropped — flag for product decision before execution. |
| **P8** | **Renderer-side telemetry parity** | ADR 0009 | `recordRetrievalChoice` is called from the free renderer's `handleChoice`. After P3 widens the type and P4 extracts the core, paid retrieval choices flow through the same call automatically — verify, don't reinvent. | Smoke test: choose a retrieval answer in M4U1, observe an audit row with `module=4` in the DB. No new code if P3+P4 are clean. | (verification only) | Manual smoke + a Playwright spec under `frontend/tests/e2e/curriculum/paid-retrieval.spec.ts`. | None. |
| **P9** | **Geragogy parity audit re-run** | CONTRACT §V self-check; this sprint's premise | Audit chart in chat 2026-05-24 lists 8 ❌ for paid. | Re-run the chart after P1–P8. Every ❌ becomes ✅ or 🟡 with explicit justification. The paid grade lifts from F to ≥ A. | `docs/audits/paid-modules-parity-2026-MM-DD.md` (new) | New audit doc committed alongside the PR closing the sprint. | None. |

---

## 4. Closing the chart — explicit ❌ → ✅ map

| Audit row (2026-05-24)              | Closes via | Becomes |
| ----------------------------------- | ---------- | ------- |
| Multi-page lesson                   | P1 + P3 + P4 | ✅ |
| Page types (5 kinds)                | P1 (server delivers them) + reused PageTypes.tsx | ✅ |
| Retrieval question + telemetry      | P2 + P3 + P8 | ✅ |
| Resume / progress within unit       | P4 + P6 | ✅ |
| Previous button across pages        | P4 (inherited) | ✅ |
| Indicator                           | P4 (inherited) | ✅ |
| Renderer in tree                    | P5 | ✅ |
| Menu lists paid                     | P7 | ✅ (or 🟡 if product opts out — documented) |

---

## 5. Acceptance suite

The sprint is complete when every item below holds:

1. `pytest backend/tests/test_paid_lesson_endpoint.py -v` — green.
2. `pytest backend/tests/test_retrieval_choice.py -v` — green for M4 + M5 cases.
3. `npm test --prefix frontend` — `loadPaidLesson` unit tests green;
   widened `RetrievalChoiceRecord.module` type compiles.
4. Manual: signed-in entitled user navigates Free M3U-last → Continue
   → lands directly on M4U1P1 (no detour through paywall) with the
   exact same NavBar, Indicator format, and Previous button pattern
   as free.
5. Manual: signed-in non-entitled user attempting M4 hits the paywall
   handshake; after purchase, lands on M4U1P1 with identical UX.
6. Manual: refresh on M4U2P3 → resume at M4U2P3 (P6).
7. New audit doc `docs/audits/paid-modules-parity-2026-MM-DD.md`
   shows the chart with no ❌ remaining and the paid grade at ≥ A.
8. Production smoke (`bash infra/scripts/smoke-prod.sh`) passes,
   including the existing login scenarios script.

---

## 6. Governance

- **No new V1 components.** Every parity item reuses Heading, Body,
  Button, Card, Field, List, Divider, Indicator, ConfirmDialog,
  PendingBanner, BlockedNotice. If an executor finds themselves
  reaching for something else, stop and open an ADR per CONTRACT §VI.
- **No content changes.** Lesson body strings, retrieval prompts,
  examples are owned by ADRs 0017 / 0020 and the curriculum-authoring
  process. This sprint touches plumbing and UX, not pedagogy.
- **No pricing changes.** ADR 0021 governs.
- **Per CONTRACT §VI**, this document does not modify the contract.
  No allowance for new colors, motion durations, spacing values,
  components, or copy patterns is requested or implied.

---

## 7. Out-of-scope follow-ups (track separately)

- Per-unit completion ticks in the menu (lifts `CurriculumMenu` to
  A+, not strictly needed for parity).
- Paid-side analytics dashboard.
- Bulk-import tool for new paid lessons (orthogonal to renderer).
- Localisation of paid copy (out of scope; free isn't localised
  either).

---

## 8. Open questions for product / approval

1. **Menu visibility (P7):** show paid modules as gated entries, or
   keep them hidden until purchase? Default proposal: show with
   muted-amber affordance.
2. **Sequence ordering for M5 vs M4:** strict M4 → M5, or allow the
   user to begin either after purchase? Default proposal: strict
   M4 → M5 (mirrors free's strict ordering).
3. **Free → paid handoff:** after the last free unit, auto-route to
   the paywall (current behaviour) or to a celebratory bridge page
   that names what they just finished and previews M4? Default
   proposal: preserve current behaviour; add a bridge page in a
   later sprint if engagement data warrants it.

---

## 9. Status tracking

This document is a plan, not a journal. The PR(s) closing each work
item should reference the row id (P1…P9) in the commit message and
update the chart in §4 only as part of the final audit doc in §3 P9.
