# 0016 - Module 3 (long-term judgment & autonomy): same adaptation pattern as Module 2

## Status

Accepted (Sprint 18).

## Context

A Module 3 drop-in was proposed: 4 declarative, dignity-preserving units intended to defend long-term judgment, prevent over-trust or dependency, and explicitly recalibrate the learner's relationship with Claude. Library-grounded as before: Carr (2009), Formosa (2012), Lövdén et al. (2010), Norman (2013), Fisk et al. (2009), Wiener (1948).

The drop-in repeated the same architectural conflict that ADR 0015 already resolved for Module 2: an endpoint that accepts a `signals` dict from the request body and passes it to a governor. ADR 0015 rejected that pattern as a violation of Rule 1 (Backend Authority).

## Decision

Module 3 lands following ADR 0015 verbatim:

- 4 units land **content-verbatim** (titles, descriptions, page text, thresholds, telemetry_requirements).
- A new `Module3Unit` in `backend/models/curriculum_units_module_3.py` mirrors `Module2Unit`: extends `CurriculumUnit` with a typed `telemetry_requirements: Dict[str, float]` field. The base model is untouched.
- Three endpoints under `/api/curriculum/module-3/`: `units`, `units/{id}`, `next`. None accept signals from the request body. Stability is derived from the running [InterfaceStateEstimator](cci:2://file:///mnt/c/Users/kimem/Noni/backend/core/interface_control/state_estimator.py:10:0-25:42).
- `telemetry_requirements` are recorded in `event_metadata` on every Module 3 ISCS decision, per ADR 0009.
- Per-learner enforcement (volatility/strain/mastery gates) remains deferred to the auth-vendor pass.
- `Module2Unit` and `Module3Unit` carry identical fields. A shared `TelemetryGatedUnit` base could collapse them, but is deliberately deferred until a Module 4 lands; the duplication is small and explicit ("Explicit Over Implicit").

## Consequences

- The Noni curriculum is now a 3-module structure: orientation/safety (Module 1) -> sustained use (Module 2) -> long-term judgment (Module 3).
- Test coverage grows from 65 -> 72 (7 new specs mirroring Module 2's invariants for Module 3).
- The architectural rule that the frontend cannot supply ISCS signals stays intact across all three modules.
- Future curriculum modules should follow ADR 0015 / 0016 unchanged: same model subclass shape, same routes, same audit-logging, same deferral on per-learner enforcement.
