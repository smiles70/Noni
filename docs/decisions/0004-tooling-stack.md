# 0004 — Python tooling: ruff + black, pre-commit, GitHub Actions CI

## Status

Accepted (Sprint 4).

## Context

Without enforced quality gates, format and lint drift accumulates and review attention shifts to whitespace. Three modern Python tooling baselines:

- ruff alone (lint + format via `ruff format`)
- black + ruff (separate format and lint)
- isort + black + flake8 + mypy (legacy combination)

## Decision

- **ruff** for linting (`ruff check`).
- **black** for formatting (we keep black to minimize churn from existing usage; ruff-format is a future option per ADR-XXXX when written).
- **mypy** for type-checking, run in CI only (too slow for pre-commit on every save).
- **pre-commit** framework hooks ruff + black + standard hooks (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`) on every commit.
- **GitHub Actions** runs the full quality matrix (ruff, black --check, alembic upgrade, pytest) plus frontend (type-check, build) on every push and PR to `main`.
- Frontend pre-commit hooks (prettier/tsc) deferred to a later sprint to keep local commits fast.

## Consequences

- Bad-format commits are blocked locally before reaching CI.
- CI is the canonical truth for "is this branch shippable".
- New contributors must `pre-commit install` once after clone (documented in README).
- Tooling versions are pinned in `.pre-commit-config.yaml`; bump deliberately.
