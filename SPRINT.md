# Sprint 13: Sign-up -> First Safe Win Content (CLOSED)

Tag: `sprint-13-first-win-content-v1`. Closes the previously-deferred "Copy for Golden Flow Steps 5-7" out-of-scope item by integrating the Sign-up -> First Safe Win content drop, typed and exposed via API.

## Phases

- 13.1 `backend/content/signup_first_win.py` (verbatim per ADR 0006 separation; preserves smart-quote typography)
- 13.2 `backend/models/signup_first_win.py` (Pydantic schema; `extra="forbid"` so drift is caught at validation time)
- 13.3 `GET /api/landing/first-win` endpoint added to landing router
- 13.4 5 new tests: schema validation, endpoint shape, no-empty-strings invariant, reversibility-of-choices invariant, no-urgency-language invariant
- 13.5 README API-surface table + sprint-history row updated
- 13.6 Closeout

## Out of scope

- Frontend rendering of the new content (separate sprint when the wider sign-up flow ships)
- Real Claude integration referenced in step 5 copy ("what working with Claude feels like") — copy is generic enough to ship pre-vendor
