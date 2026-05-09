# Noni

A geragogy-grounded AI learning system for older adults.

---

## 1. Project Purpose

Noni provides structured, respectful learning experiences designed specifically for older adults. The system prioritizes **cognitive safety**, **dignity**, and **autonomy** over speed or engagement metrics.

The design philosophy centers on:
- **Predictable experiences**: no surprises, no sudden changes
- **User-controlled pacing**: learners set their own rhythm
- **Reversible progress**: any advancement can be undone
- **Cognitive load management**: complexity is introduced gradually and explicitly

---

## 2. Technology Stack Rationale

### Backend
- **Python 3.12+** — type hints, modern async support, current enterprise default
- **FastAPI** — performance, automatic API documentation, Pydantic integration
- **Pydantic** — runtime validation, clear data contracts
- **SQLAlchemy + Alembic** — battle-tested ORM with reviewable schema migrations
- **PostgreSQL 15** — ACID compliance, audit trail support, dev/prod parity via Docker

### Frontend
- **React 18 + TypeScript (strict)** — component boundaries, compile-time safety
- **Vite** — modern bundler, fast HMR
- **Passive rendering only** — no business logic, no client-side state machines

### Tooling
- **ruff + black** — lint + format
- **pre-commit** — local quality gate before every commit
- **Alembic** — schema migrations (replaces `Base.metadata.create_all()`)
- **Playwright + axe-playwright** — end-to-end and automated WCAG 2.1 AA checks
- **GitHub Actions** — CI on push/PR (Postgres service container, full test matrix)

### Explicit Non-Choices
- No serverless orchestration (complexity hiding leads to unpredictable behavior)
- No frontend-controlled state (authority must reside in auditable backend code)
- No NoSQL defaults (ACID required for user progress)
- No growth frameworks (premature abstraction creates technical debt)
- No vendor decisions yet — see `docs/deferred-decisions.md`

---

## 3. Architectural Principles

### Backend Authority
All progression decisions live in backend code. The frontend never determines user state, advancement, or completion.

### Content as Data
Learning content is data, not logic. Content blocks define what to present; the Interface State Control System (ISCS) decides when and how.

### Reversibility
All user advancement is reversible. A learner can return to any previous state without penalty or data loss.

### Explicit Over Implicit
No automated actions without explicit review. No hidden state changes. No surprise transitions.

### Calm Experience Design
No countdown timers. No urgency framing. No gamification pressure. No interruption-based notifications. Clear, consistent navigation.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the complete non-negotiable rules.

---

## 4. Geragogy Grounding

Noni is built on principles of geragogy (learning theory for older adults):

- Respect for autonomy: learners control their journey
- Acknowledgment of experience: content honors life experience and wisdom
- Cognitive pacing: information presented in digestible segments
- Error tolerance: mistakes are learning opportunities, not failures
- Accessibility by design: not an add-on, but a foundational requirement

---

## 5. Non-Goals

This system explicitly does **NOT**:

- Optimize for "daily active users" or engagement metrics
- Use gamification, leaderboards, or competitive elements
- Employ dark patterns (infinite scroll, variable rewards, social pressure)
- Make automated decisions about user advancement without explicit review
- Store or process data without clear user benefit and consent
- Prioritize feature velocity over stability and safety

---

## 6. Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (for local Postgres)

### Backend

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate         # Linux/macOS/WSL
# .\venv\Scripts\Activate.ps1    # Windows PowerShell

# 2. Install backend deps
pip install fastapi 'uvicorn[standard]' pydantic pydantic-settings \
    sqlalchemy psycopg2-binary numpy python-dotenv httpx \
    pytest black ruff mypy alembic pre-commit

# 3. Configure environment
cp .env.example .env
# Edit .env if you change DATABASE_URL

# 4. Start Postgres
docker compose up -d db

# 5. Run schema migrations
alembic upgrade head

# 6. Install pre-commit hook (one-time)
pre-commit install

# 7. Run the API
uvicorn backend.app.main:app --reload
```

### Frontend

```bash
cd frontend

# 1. Install deps
npm install

# 2. Run dev server (proxies API at 127.0.0.1:8000)
npm run dev
```

The landing page is served at `http://127.0.0.1:5173/`. Click **Begin calmly** to advance to the curriculum view.


### Run the whole stack in Docker

```bash
docker compose up --build
```

This boots Postgres, the backend (with migrations applied on startup), and an nginx-served frontend. Open `http://localhost:5173/`. See ADR 0010 for the container strategy.

### Verification

```bash
# Health check
curl http://127.0.0.1:8000/health

# Backend tests
pytest backend/tests/ -v

# Frontend type-check + build
cd frontend && npm run type-check && npm run build
```

---

## 7. Governance Philosophy

### Backend Authority
The **Interface State Control System** (`backend/core/interface_control/`) is the single source of truth for all user-facing UI state. No frontend code may:
- Modify user progression state
- Determine advancement eligibility
- Store authoritative user data

### User Dignity
Every feature is evaluated against these questions:
- Does this respect the user's autonomy?
- Does this protect cognitive safety?
- Is this calm and predictable?
- Can the user undo this action?

### Audit and Maintainability
All state changes are:
- Persisted as durable telemetry events (Postgres)
- Reversible
- Reviewable via `GET /api/telemetry/export` (JSON or CSV)
- Tested with explicit expectations

---

## 8. Architectural Rules (Non-Negotiable)

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the complete rules. Key principles:

1. **Backend Authority** — all state decisions in backend code
2. **Frontend Passivity** — frontend renders, backend governs
3. **Content/Data Separation** — content is data, logic is code
4. **Reversibility** — all advancement can be undone
5. **No Urgency** — no timers, pressure, or artificial scarcity
6. **No Dark Patterns** — no psychological manipulation
7. **Explicit Review** — no automated state changes without human review
8. **Cognitive Safety First** — design respects older adult cognitive needs

---

## 9. Project Structure

```
backend/
  app/                       FastAPI application entry (main.py)
  core/
    config.py                Pydantic-settings configuration
    database.py              SQLAlchemy engine + session + run_migrations()
    interface_control/       ISCS: state_estimator, stability_metric, state_selector
    geragogy_engine/         Geragogy signal model (mastery / strain / load)
    diagnostic_engine/       Program-graph diagnostic signals
    nlu_engine/              Simple intent interpreter
    claude_engine/           Mock Claude client (real client deferred)
    projects/                Geragogy-aligned project catalog
  models/                    Pydantic + SQLAlchemy models (curriculum, landing, telemetry, user, agent)
  api/routes/                FastAPI routers (curriculum, signals, landing, telemetry_export)
  content/                   User-facing copy (landing_page.py)
  services/                  Persistence services (telemetry.py)
  tests/                     pytest suite (49 tests)

frontend/
  src/
    api/                     ISCS + landing API clients
    components/              Passive React renderers (LandingPage, CurriculumRenderer)
    styles.css               Global focus-visible, larger-text, reduced-motion rules
    largeText.ts             localStorage-persisted larger-text toggle
    main.tsx, App.tsx        Boot + view-toggle root
  e2e/                       Playwright + axe-playwright specs
  playwright.config.ts

alembic/
  env.py                     Reads DATABASE_URL from settings
  versions/                  Schema migrations (baseline at 4a978b4c94cf)

docs/
  flows/                     Canonical product specs (golden-landing-flow.md)
  decisions/                 Architecture Decision Records (0001-0008)
  deferred-decisions.md      Vendor decisions held for a single later pass

.github/workflows/ci.yml     Backend lint+test (with Postgres) + frontend type-check+build
.pre-commit-config.yaml      ruff + black + hygiene hooks
docker-compose.yml           Local Postgres
ARCHITECTURE.md              Non-negotiable architectural rules
PROGRESS.md, SPRINT.md       Tracking docs
```

---

## 10. Development Workflow

### Quality gates (run on every commit)
```bash
# Already automatic via pre-commit:
ruff check backend/
black backend/
# Plus: trim trailing whitespace, end-of-file fixer, check-yaml, large-file guard
```

### Full CI parity locally
```bash
ruff check backend/
black --check backend/
alembic upgrade head
pytest backend/tests/ -v
( cd frontend && npm run type-check && npm run build )
```

### End-to-end tests (one-time setup)
```bash
cd frontend
npm run test:e2e:install   # downloads ~150 MB of browser binaries (one time)
npm run test:e2e           # runs all 4 specs including WCAG 2.1 AA scan
```

### Adding an architecture decision
1. Copy an existing entry in `docs/decisions/`
2. Number it sequentially (zero-padded, e.g. `0009-...md`)
3. Use the Nygard format: Status / Context / Decision / Consequences
4. Update `docs/decisions/README.md` index
5. ADRs are immutable once accepted; supersede with a new ADR

### Adding a curriculum unit
1. Append a new `CurriculumUnit` to `UNITS` in `backend/models/curriculum_units.py`
2. Add tests verifying its structure in `backend/tests/test_curriculum_units.py`
3. The ISCS will gate page selection automatically based on `max_complexity` and `stability_threshold`

---

## 11. API Surface

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/` | Service banner |
| GET | `/api/curriculum/what-is-ai` | First curriculum experience (Sprint 1) |
| GET | `/api/curriculum/units` | All curriculum units (2–7) |
| GET | `/api/curriculum/units/{id}` | One unit, ISCS-approved page |
| GET | `/api/curriculum/next-unit` | ISCS recommendation for next unit |
| POST | `/api/signals/user-action` | Record a user-originated signal |
| POST | `/api/signals/telemetry` | Record a telemetry event |
| GET | `/api/landing/steps` | All 8 Golden Flow steps (conceptual model) |
| GET | `/api/landing/steps/{id}` | One Golden Flow step |
| GET | `/api/landing/page` | User-facing landing-page copy |
| GET | `/api/telemetry/export` | Telemetry dump (JSON) |
| GET | `/api/telemetry/export.csv` | Telemetry dump (CSV) |

---

## 12. Architecture Decisions

ADR index: [`docs/decisions/README.md`](./docs/decisions/README.md). Currently 0001 through 0008 covering landing flow architecture, Postgres choice, frontend stack, tooling, Alembic, content separation, accessibility, and E2E.

---

## 13. Sprint History

| Tag | Sprint |
|---|---|
| `sprint-closeout-v1` | Progress Closeout — foundations, Postgres, tests, frontend, lint/format |
| `sprint-2-curriculum-v1` | Curriculum Expansion — Units 2–4 via ISCS |
| `sprint-3-landing-contract-v1` | Golden Landing Flow contract — spec doc, ADR 0001, model, routes |
| `sprint-4-engineering-foundations-v1` | Engineering Foundations — pre-commit, CI, Alembic, ADRs 0002–0005 |
| `sprint-5-landing-copy-v1` | Landing Copy + Page Rendering — content module, endpoint, ADR 0006 |
| `sprint-6-hardening-coverage-v1` | Hardening & Coverage — Units 5–7, telemetry export, a11y, Playwright + axe |
| `sprint-7-docs-onboarding-v1` | Documentation & Developer Onboarding |
| `sprint-8-ci-e2e-v1` | CI Playwright Integration |
| `sprint-9-curriculum-a11y-v1` | Curriculum View Accessibility Polish |
| `sprint-10-telemetry-richness-v1` | Telemetry Signal Richness |
| `sprint-11-containers-v1` | Containerization (this sprint) |

---

## 14. Deferred Decisions

See [`docs/deferred-decisions.md`](./docs/deferred-decisions.md) for the bundle of third-party / vendor decisions held for a single later pass: authentication, real Claude API, email provider, observability, hosting, CDN, payments.

---

## License

Proprietary — Noni Engineering Team

---

*Built with respect for the humans who will use it.*
