# Contributing to Noni

This document covers the development conventions used in this repository. Read this once before making your first commit.

## Repository conventions

- **Architecture rules are non-negotiable.** Read `ARCHITECTURE.md` first; non-compliant changes are rejected at review even if tests pass.
- **ADRs are immutable.** Once a decision is in `docs/decisions/`, it is not edited. Supersede with a new ADR.
- **Sprints close with a tag.** Each sprint ends with `git commit` + `git tag -a sprint-N-name-vK -m "..."`. The repo's `git tag` list is the durable sprint history.
- **Tracking docs live in the repo.** `PROGRESS.md`, `SPRINT.md`, and `docs/deferred-decisions.md` are the canonical state. Chat memory is not.

## Local quality gates

After cloning, run once:
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
( cd frontend && npm install )
```

Before pushing, make sure all of these pass:
```bash
ruff check backend/
black --check backend/
pytest backend/tests/ -v
( cd frontend && npm run type-check && npm run build )
```

E2E (Playwright + axe) is run separately because it needs a one-time browser install:
```bash
cd frontend
npm run test:e2e:install   # one-time, ~150 MB
npm run test:e2e
```

## Adding a curriculum unit

1. Append a `CurriculumUnit` to the `UNITS` list in `backend/models/curriculum_units.py`.
2. Each unit has at least one `CurriculumPage` with a `complexity` integer.
3. Set `max_complexity` (highest page complexity in the unit) and `stability_threshold` (ISCS gate).
4. Add tests in `backend/tests/test_curriculum_units.py`:
   - The new unit id appears in the `ids` set
   - The new unit is in the units-list response
5. The ISCS handles page selection automatically based on the running stability metric. You do not need to wire selection logic.

## Adding an architecture decision (ADR)

1. Find the next number in `docs/decisions/` (zero-padded, sequential).
2. Copy an existing ADR as a template; use Nygard format:
   - Status (Accepted / Proposed / Superseded)
   - Context (what problem and why now)
   - Decision (the chosen path)
   - Consequences (positive and negative)
3. Add an entry to `docs/decisions/README.md`.
4. Once merged, the ADR is **immutable**. Use a new ADR to supersede.

## Adding a backend endpoint

1. Pure data goes in `backend/models/` (Pydantic) or `backend/content/` (user-facing copy).
2. Endpoints go in `backend/api/routes/`.
3. Mount the router in `backend/app/main.py` with a `prefix` and `tags`.
4. Add tests in `backend/tests/`. Test for shape, contract, and any invariant the endpoint must hold.
5. If the endpoint affects schema, generate a migration: `alembic revision --autogenerate -m "describe change"`.

## Adding a frontend component

Components are **passive renderers**. They:
- Fetch from the backend in `useEffect` via the API client in `frontend/src/api/`.
- Render the response. They do not derive new state from it.
- Receive callbacks (`onBegin`, etc.) from a parent that handles view transitions.
- Use semantic HTML (`<main>`, `<header>`, `<section>`, `<nav>`, `<footer>`) and ARIA attributes where appropriate.
- Inherit the global focus-visible style; do not override it.
- Respect the `large-text` class on `<html>` (use `rem` units, not absolute pixels).

## Sprint workflow

1. Update `SPRINT.md` with the current sprint's plan and Definition of Done.
2. Work in phases; commit when each phase is in a clean state if it makes sense, otherwise one closeout commit at the end.
3. The closeout commit message should match the pattern: `Sprint N: Title - one-line summary of artifacts`.
4. Tag with `git tag -a sprint-N-shortname-vK -m "Sprint N complete"`.
5. Update `PROGRESS.md` to move the sprint from Active to Completed.
6. If new vendor / 3rd-party concerns arose, add them to `docs/deferred-decisions.md`.

## Commit hygiene

- The pre-commit hook will auto-fix many issues (formatting, trailing whitespace, end-of-file). If the commit fails for hook fixes, `git add -A` and re-commit.
- Avoid commits that mix sprint work with unrelated cleanup. Cleanup goes in its own commit.
- Commit messages are imperative present tense: "Add", "Fix", "Refactor", not "Added".

## Out of scope without an ADR

The following changes require an ADR before they can be merged:
- Adding a third-party vendor or SaaS dependency (auth, email, observability, hosting, etc.)
- Adding a major framework (Next.js, NestJS, Redux, etc.)
- Changing the database engine
- Bypassing ISCS for any UI-state decision
- Persisting any user data without explicit consent

When in doubt, draft the ADR first.
