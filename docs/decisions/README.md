# Architecture Decision Records (ADRs)

Numbered, immutable records of significant architectural decisions.

- Format: short Nygard-style (Status, Context, Decision, Consequences).
- Naming: `NNNN-short-title.md`, zero-padded, sequential.
- Once accepted, an ADR is not edited. Superseding decisions are written as new ADRs that reference the older one.

## Index

- [0001 — Landing flow is sequenced by user agency, not ISCS stability](./0001-landing-flow.md)
- [0002 — PostgreSQL via Docker Compose for development parity](./0002-postgres-for-dev-parity.md)
- [0003 — Vite + React 18 + TypeScript (strict) for the frontend](./0003-vite-react-typescript-strict.md)
- [0004 — Python tooling: ruff + black, pre-commit, GitHub Actions CI](./0004-tooling-stack.md)
- [0005 — Alembic migrations replace `Base.metadata.create_all()`](./0005-alembic-over-create-all.md)
