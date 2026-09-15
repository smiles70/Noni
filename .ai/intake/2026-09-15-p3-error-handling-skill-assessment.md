# P3 — Analyse & assess `agents-error-handling-patterns.zip` for adoption

## Problem / ask

The user supplied `/home/h/Downloads/agents-error-handling-patterns.zip`
and asked for analysis and assessment: is this skill worth adopting into
`.devin/skills/`, and if so in what form?

## What the artifact is

The zip (5,903 B) contains exactly one file: `SKILL.md` (641 lines,
16,834 B), frontmatter `name: error-handling-patterns`. A generic,
language-agnostic error-handling playbook:

- Error philosophies: exceptions vs Result types vs error codes vs
  Option/Maybe.
- Language patterns: Python (exception hierarchy, context managers,
  retry w/ backoff), TypeScript (custom error classes, `Result<T,E>`
  union + chaining, async handling), Rust (`Result`/`Option`, `From`
  conversions), Go (explicit returns, sentinel errors, `errors.Is/As`).
- Universal patterns: circuit breaker, error aggregation
  (`AggregateError`), graceful degradation / fallback chains.
- Best practices + common pitfalls + a `process_order` worked example.

## Initial observations to verify in the assessment

1. **Dead references** — footer cites `references/*.md` (3 files),
   `assets/*.md` (2 files), and `scripts/error-analyzer.py`; none are in
   the zip. Adopting as-is ships a skill with 6 broken pointers.
2. **Overlap with existing skill** — `.devin/skills/error-taxonomy/`
   already exists but solves a *different* problem (classifying CI gate
   failures → remediation playbooks). The zip is application-code-level
   patterns. Complementary, not duplicate — but naming (`error-*`) could
   confuse; verify trigger descriptions don't collide.
3. **Stack fit** — repo is Python (FastAPI) + TypeScript (React); Rust
   and Go sections are dead weight (~30% of the file) unless kept for
   completeness. Python examples use `requests`/SQLAlchemy idioms; repo
   uses `httpx`?/SQLAlchemy — verify idioms match.
4. **Provenance / quality** — single-file generic content, consistent
   with generated/marketplace skills (skills.sh-style). Assess against
   the repo's quality bar; code samples are illustrative, not tested.
5. **Security surface** — `retry` decorator swallows exception
   *details* on final raise (re-raises `last_exception`, losing
   intermediate tracebacks); circuit-breaker example holds mutable state
   unsynchronised; fallback helper can mask outages. Any adopted code
   needs hardening notes.

## Outcome needed

1. Assessment memo (`.ai/research/` or `.ai/audit/`) covering: content
   quality, correctness of the patterns, overlap/gap vs
   `error-taxonomy` and existing codebase error handling
   (`backend/app/main.py` handlers, frontend error boundaries), dead
   references, and a recommendation: adopt as-is / adopt trimmed /
   reject / extract-into-existing-skill.
2. If adoption is recommended: where it lands (`.devin/skills/`), what
   gets trimmed or rewritten for FastAPI + React, and how the dead
   references are resolved.

## Scope / non-goals

- Assessment only — do not modify `.devin/skills/` or application code
  without a follow-up go-ahead.
- Zip lives outside the repo in `~/Downloads`; do not commit the zip.

## References

- Source artifact: `/home/h/Downloads/agents-error-handling-patterns.zip`
  → extracted `/tmp/agents-eh/SKILL.md`
- Existing skill: `.devin/skills/error-taxonomy/SKILL.md`
- Backend error handling: `backend/app/main.py` (exception handlers)
- Frontend: `frontend/src/` error boundary tests (vitest `act` warnings)
