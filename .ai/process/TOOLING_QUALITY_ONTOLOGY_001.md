# TOOLING-QUALITY-001 Ontology

## Entities

- `SourceArtifact`: `SRC-AURA-REPORT` is the Aura Code Intelligence SARIF analysis.
- `Requirement`: `REQ-TQ-001` through `REQ-TQ-008` map to the 8 gaps.
- `Capability`: `CAP-TQ-001` (Node version), `CAP-TQ-002` (Prettier), `CAP-TQ-003` (ESLint), `CAP-TQ-004` (Coverage), `CAP-TQ-005` (Circular), `CAP-TQ-006` (Dead code), `CAP-TQ-007` (Complexity), `CAP-TQ-008` (License), `CAP-TQ-009` (Husky), `CAP-TQ-010` (README).
- `Decision`: `DEC-TQ-001` — close the 8 gaps in a single Phase 0 tooling pass.
- `Evidence`: `EVI-TQ-BUILD` is the passing build after changes.

## Traceability

- `SRC-AURA-REPORT` `evidenced_by` `EVI-AURA-001`.
- `EVI-AURA-001` `defines` `DEC-TQ-001`.
- `DEC-TQ-001` `owns` `CAP-TQ-001..010`.
