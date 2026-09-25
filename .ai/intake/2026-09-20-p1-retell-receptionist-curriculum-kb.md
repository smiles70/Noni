# PS-020 — Retell receptionist: curriculum not in knowledge base

**Date:** 2026-09-20 · **Status:** intake — implementation plan below
**Reporter:** owner · **Persona:** learner + caregiver (phone line)
**Skill check:** retell_apply.py pattern governs; no UI surface → geragogy
n/a; persona isolation per ADR-0032 (learner-facing content — voice KB only)

## Problem statement

The voice receptionist (`agent_83c72268174e906ec2ed82a564`, "MyNaani
Receptionist") cannot help a caller who is stuck on a specific unit or
question — her knowledge base contains only site/topic docs, none of the
actual curriculum content.

## Root cause (verified via Retell API)

- Receptionist LLM `llm_1b76092d677b0df6aa0017b1e242` has KB
  `knowledge_base_3bee30aa46d414e4` ("mynaani-voice-v2") attached.
- That KB contains 10 docs: about-mynaani, accessibility-tech,
  accounts-signin, contact, course-structure, gifting, organizations,
  pricing-purchasing, privacy-data, what-is-not-published.
- `course-structure.md` (1.4KB) is an outline only — no unit text,
  no retrieval questions, no worked examples.
- **No doc contains curriculum content.** Confirmed, not assumed.

## Curriculum corpus location

- `backend/models/curriculum_units_module_{0,2,3,4,5}.py` +
  `curriculum_units.py` (module 1) — ~3,360 lines of structured
  `CurriculumUnit` → `CurriculumPage` (context/principle/example/
  recap/retrieval) with `RetrievalChoice` Q&A blocks.
- All content is code-owned → extraction must be generated, never
  hand-copied (single source of truth).

## Design

1. **Generator** — `scripts/curriculum_to_kb.py`: imports the unit
   models, emits `retell/kb/curriculum/module-N.md` — per unit:
   title, description, each page's title + content, and for retrieval
   pages the question, the choices, the correct answer, and the
   explanation. Deterministic output committed to the repo (reviewable
   diff when curriculum changes).
2. **Uploader** — `scripts/retell_apply_curriculum.py` following the
   `retell_apply.py` idempotent pattern: creates dedicated KB
   `mynaani-curriculum-v1`, uploads the generated docs, attaches it to
   the receptionist LLM's `knowledge_base_ids` alongside (not
   replacing) `mynaani-voice-v2`.
3. **Prompt section** — receptionist `general_prompt` gains a
   "Helping with a lesson" block: identify which unit the caller is on,
   retrieve the relevant content, explain in plain language, and —
   critically — **guide retrieval questions rather than read out the
   answer** (see edge cases).

## Edge cases

- **Answer spoiling (highest risk):** retrieval pages contain the
  correct answers. Verbatim exposure would let the receptionist just
  hand out quiz answers, defeating the retrieval practice. Mitigation:
  prompt instruction to coach rather than reveal + retrieval docs mark
  correct answers in a clearly-labeled "correct answer (do not read
  verbatim — guide the caller)" section.
- **KB size:** ~3.4k lines of Python → roughly 150–200KB of markdown
  across ~6 docs — well under Retell per-source limits; splitting per
  module also keeps retrieval scoped.
- **Isolation:** facility + gift chat agents untouched; the curriculum
  KB attaches ONLY to the receptionist voice LLM. Chat widgets stay
  marketing-scoped per ADR-0032.
- **Drift:** curriculum edits without regenerating KB docs → stale
  answers. Mitigation: generator is deterministic; a CI check can diff
  regenerated output vs committed files.
- **Scope creep on calls:** prompt keeps receptionist's job as "help
  the caller find their footing, point back to the unit" — she is not
  a tutor delivering the lesson over the phone.

## Acceptance

- [ ] Generated `retell/kb/curriculum/module-*.md` committed
- [ ] `mynaani-curriculum-v1` KB exists, sources uploaded, attached to
      receptionist LLM (verified via list-knowledge-bases + get-retell-llm)
- [ ] Prompt updated with lesson-help section
- [ ] Test call: ask receptionist a real unit question → she answers
      from curriculum; ask a retrieval question → she guides, doesn't spoil
- [ ] Graph episode + RESUME updated

## Guardrails (triple-checked against live Retell API 2026-09-20)

- **Egress allowlist**: httpx wrapper whitelists (method,path) —
  GET list/get-*, POST create-knowledge-base, POST
  add-knowledge-base-sources/{curriculum-kb}, PATCH
  update-retell-llm/{receptionist-llm}. Any other call raises
  pre-flight. No DELETE verb exists in code AND egress blocks it.
- **Write-target pin**: receptionist LLM id
  `llm_1b76092d677b0df6aa0017b1e242` hardcoded + agent_name asserted.
- **Must-not-change set** (post-run refetch + assert unchanged):
  llm_99732214ed81ba8f26d3ea56772a (callbacks, shared staging+prod),
  llm_a524945938fe49cc66f346d1ce52 (assistant),
  llm_e9ed15195e3e52a257f4964625ef (facility chat),
  llm_13c7c67388fef34803a41180c0db (gift chat).
- **Read-modify-write only**: PATCH is partial-field; kb list =
  fetched ∪ new; prompt = fetched + appended `## Helping with a lesson`
  (marker-guarded, idempotent).
- **Idempotent-by-inspection**: KB-by-name, source-by-title,
  attached-id, prompt-marker — re-runs are no-ops.
- **Snapshots**: pre/post LLM+agent configs dumped to
  .ai/audit/retell-curriculum/; diff printed; snapshot is the rollback
  file.
- **--apply required**: default is dry-run; bare run prints intent only.
- **Endpoint probe**: create-knowledge-base returns 400 on empty body —
  endpoint confirmed live without side effects.
- **Graph constraint**: CON-BID17-K5 (~50 interactions/mo shared Retell
  budget) — prompt instructs concise answers that point back to the
  unit; owner to watch Retell usage post-launch.

## Applied (2026-09-20, owner-approved)

- `mynaani-curriculum-v1` created: `knowledge_base_1dcee504e7c01fc7`
  with all 6 module docs (verified via get-knowledge-base).
- Attached to receptionist LLM alongside `mynaani-voice-v2`
  (`knowledge_base_ids` = union).
- `## Helping with a lesson` appended to `general_prompt` (marked,
  idempotent).
- Isolation tripwire PASSED — the four non-target LLMs unchanged.
- Snapshots: `.ai/audit/retell-curriculum/{pre,post}-state.json`.
- API fix learned: `create-knowledge-base` is form-encoded and requires
  ≥1 source at creation (first doc rides the create call).

## Remaining

- [ ] Owner test call: web call `call_440a7bab496b5f614c9ea8c2cdb`
  (join page: AGENCY_BIDS/receptionist-test-call.html?t=<access_token>,
  token ~10min TTL — regenerate via create-web-call if expired) or dial
  1-877-409-4144. Ask a unit question → expect curriculum-grounded
  answer; ask a practice question → expect coaching, not the answer.
