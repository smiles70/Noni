# Sprint 17: Module 2 Curriculum - Sustained Claude Use (CLOSED)

Tag: `sprint-17-module-2-curriculum-v1`. Lands the 5 Module 2 units (sustained, real-world use of Claude over time) using the architectural patterns established in Sprints 2, 6, 9, 10. The drop-in's request-body signal pattern was explicitly rejected per Rule 1 (Backend Authority); see ADR 0015.

## Phases

- 17.1 `Module2Unit` model (sub-class of `CurriculumUnit`, adds typed `telemetry_requirements`)
- 17.2 5 units with content verbatim
- 17.3 Three new endpoints under `/api/curriculum/module-2/`
- 17.4 7 new tests (65/65 passing) including content invariants and audit-log verification
- 17.5 ADR 0015
- 17.6 Closeout
