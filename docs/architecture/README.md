# Architecture Documents

Authoritative system, vendor, and schema diagrams for Noni. These documents are binding and are referenced from the ADRs in `docs/decisions/`.

| Document | Scope | Bound by ADRs |
|---|---|---|
| [`SYSTEM.md`](./SYSTEM.md) | Request flow, authority boundaries, contract enforcement | 0019, 0022, 0023, 0024, 0025 |
| [`VENDORS.md`](./VENDORS.md) | Third-party topology, vendor consolidation, secrets propagation | 0022, 0025 |
| [`SCHEMA.md`](./SCHEMA.md) | Full Postgres schema, indexes, RLS policies, migration ownership | 0023, 0024 |

## How to use these documents

- **When writing code:** the diagrams are normative. If code disagrees with a diagram, change the code or change the diagram in the same commit (with an ADR amendment).
- **When writing ADRs:** reference the diagrams rather than redrawing them.
- **When evaluating a proposed vendor or table:** check the consolidation principle in `VENDORS.md` and the invariants in `SYSTEM.md` and `SCHEMA.md` first.
