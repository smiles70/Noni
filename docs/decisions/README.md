# Architecture Decision Records (ADRs)

Numbered, immutable records of significant architectural decisions.

- Format: short Nygard-style (Status, Context, Decision, Consequences).
- Naming: `NNNN-short-title.md`, zero-padded, sequential.
- Once accepted, an ADR is not edited. Superseding decisions are written as new ADRs that reference the older one.

## Index

- [0001 - Landing flow is sequenced by user agency, not ISCS stability](./0001-landing-flow.md)
- [0002 - PostgreSQL via Docker Compose for development parity](./0002-postgres-for-dev-parity.md)
- [0003 - Vite + React 18 + TypeScript (strict) for the frontend](./0003-vite-react-typescript-strict.md)
- [0004 - Python tooling: ruff + black, pre-commit, GitHub Actions CI](./0004-tooling-stack.md)
- [0005 - Alembic migrations replace `Base.metadata.create_all()`](./0005-alembic-over-create-all.md)
- [0006 - Landing-page content is stored separately from the Golden Flow step model](./0006-landing-content-separate-from-flow-model.md)
- [0007 - Accessibility approach: WCAG 2.1 AA via axe + visible focus + larger-text mode](./0007-accessibility-approach.md)
- [0008 - End-to-end and accessibility verification via Playwright + axe-playwright](./0008-e2e-playwright-axe.md)
- [0009 - Rich audit telemetry: promote ISCS decision variables to columns](./0009-rich-audit-telemetry.md)
- [0010 - Container strategy: multi-stage Dockerfiles + compose for local parity](./0010-container-strategy.md)
- [0011 - Cross-browser E2E: chromium + firefox + webkit on every CI run](./0011-cross-browser-e2e.md)
- [0012 - Pinned Python dependencies via requirements files](./0012-pinned-dependencies.md)
- [0013 - Bundle-size budget enforced in CI](./0013-bundle-size-budget.md)
- [0014 - Mobile device emulation in the E2E matrix](./0014-mobile-device-e2e.md)
- [0015 - Module 2 multi-dimensional ISCS gating: data shape kept, request-body signals rejected](./0015-module-2-multi-dim-iscs.md)
