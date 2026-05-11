# 0020 - Module 5 (composing Agents from Claude Skills): same adaptation pattern as Modules 2-4

## Status

Accepted (Sprint 22).

## Context

A pre-written Module 5 content drop was provided covering five units on building agents from Claude Skills: what an agent is, designing an agent's job, building step-by-step, using safely, and staying the authority. The raw drop arrived with:

1. A duplicated `CurriculumUnit` class definition.
2. A `governor.approve(candidates, signals)` endpoint where `signals` is a request-body dict, mirroring the pre-ADR-0015 anti-pattern.
3. A header citation block referencing **Carr (2009)**, **Formosa (2012)**, **Lövdén et al. (2010)**, **Norman (2013)**, **Fisk et al. (2009)**, and **Wiener (1948)**.

The closed-world contract (ADR 0019) now governs citations. Of the six header references, only Norman (2013) [B2] and Fisk et al. (2009) [C1] are on the closed reference list. Carr (2009) is the same fabricated/misattributed citation flagged in ADR 0019. Formosa (2012), Lövdén et al. (2010), and Wiener (1948) are off-list.

This decision codifies the adaptation, which is structurally identical to Modules 2/3/4 plus the new citation-grounding pass.

## Decision

1. **Use `TelemetryGatedUnit` directly via alias (ADR 0018).**
   - `Module5Unit = TelemetryGatedUnit` in `backend/models/curriculum_units_module_5.py`.
   - No new subclass. No new fields beyond `telemetry_requirements`.

2. **Preserve the five units verbatim** — same `id`, `title`, `description`, `pages.content`, `max_complexity`, `stability_threshold`, `telemetry_requirements` as the drop.

3. **Reject the drop-in's endpoint wiring (ADR 0015 enforcement).**
   - No `signals: dict` in the request body.
   - The `/module-5/units`, `/module-5/units/{id}`, and `/module-5/next` endpoints derive stability from the server-side `InterfaceStateEstimator`, mirroring Modules 2, 3, and 4.
   - `telemetry_requirements` are recorded in `event_metadata` for future per-learner enforcement (deferred to the auth/vendor pass).

4. **Re-ground citations under the closed library (ADR 0019).**

   | Drop-in citation | Status | Replacement |
   |---|---|---|
   | Carr (2009) | Off-list, likely fabricated | C1 Fisk et al. (2009) — human factors / safety |
   | Formosa (2012) | Off-list | C3 Knowles et al. (2019) — HCI and aging, autonomy |
   | Lövdén et al. (2010) | Off-list | D1 Sweller, Ayres & Kalyuga (2011) — cognitive load |
   | Norman (2013) | **On-list as B2** | Kept |
   | Fisk et al. (2009) | **On-list as C1** | Kept |
   | Wiener (1948) | Off-list | P2 IDD-2026 + C1 Fisk (2009) — human-control framing |
   | Claude Agent Skills architecture (Anthropic, 2025-2026) | Vendor technical reference | Kept as descriptive, not justificatory |

   The module's geragogy and human-authority rationale is fully covered by on-list sources. No new sources are introduced.

5. **Add a content-level human-authority test** (`test_module_5_content_preserves_human_authority`) that fails if any unit mentioning "agent" lacks at least one control marker ("review", "stop", "pause", "decide", "judgment", "in control", "you choose", "you can", "your rules", "your boundaries", "your thinking"). Module 5 is the first module where the learner's authority over an AI artifact is the central topic; the test makes that contract structural rather than stylistic.

## Consequences

- Module 5 ships behind the same backend-authoritative pattern as Modules 2-4; no new architectural surface.
- Module count grows to 5 with zero new fields and zero new endpoints beyond the standard triplet (`units` / `units/{id}` / `next`).
- The closed reference list is honored without compromise; the off-list citations from the drop are replaced with on-list equivalents that say the same thing.
- The human-authority content test makes the module's defining property — agents assist, learners decide — a CI-enforced invariant.
- If a future module introduces a structurally new kind of gating (e.g., per-step approval gates, multi-agent composition with cross-agent constraints), it gets its own subclass and its own ADR. The `TelemetryGatedUnit` base stays narrow.
- Actually running an agent end-to-end remains vendor-blocked (Claude API + auth). The module teaches *about* agents declaratively.
