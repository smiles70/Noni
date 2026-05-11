"""Module 5 curriculum units: composing Agents from Claude Skills.

Distinct from Modules 1-4 (orientation, sustained use, long-term judgment,
building Skills). Module 5 advances the learner from "teaching Claude one
Skill at a time" to "composing multiple Skills into a named, scoped Agent
workflow that remains under explicit human authority at every step."

Library-grounded references (closed list, see `docs/library/README.md`):
  - C1 Fisk et al. (2009) — human factors for older adults; human-in-control
        framing for agent oversight.
  - C3 Knowles et al. (2019) — HCI and aging beyond accessibility; learner
        autonomy and judgment preservation.
  - B2 Norman (2013) — mental models; agents as named, predictable roles.
  - D1 Sweller, Ayres & Kalyuga (2011) — cognitive load theory; depth via
        composition without raising intrinsic load.
  - P2 IDD-2026 — ISCS stability constraints continue to apply.
  - Claude Agent Skills architecture (Anthropic, 2025-2026) — descriptive
        technical reference for what an Agent is in this vendor context.

See ADR 0020. Citations re-grounded under ADR 0019 (closed-world contract).

Note: rendering Module 5 in the UI does not require Anthropic API access;
the content teaches *about* Agents declaratively. Actually composing and
running Agents end-to-end remains vendor-blocked (auth + API integration).
"""

from typing import Optional


from backend.models.curriculum_units import (
    CurriculumPage,
    TelemetryGatedUnit,
)


Module5Unit = TelemetryGatedUnit


def _page(unit_id: str, title: str, lines: list) -> CurriculumPage:
    return CurriculumPage(
        id=f"{unit_id}-page-1",
        title=title,
        content=lines,
        complexity=1,
    )


UNITS_MODULE_5 = [
    Module5Unit(
        id="module5-unit-1",
        title="What an Agent Is (Built from Skills)",
        description="Understanding agents as structured roles made from Skills.",
        pages=[
            _page(
                "module5-unit-1",
                "What an Agent Is (Built from Skills)",
                [
                    "An agent is a role you define for Claude.",
                    "Agents are built from one or more Skills.",
                    "Agents follow your rules and instructions.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.65,
        telemetry_requirements={"mastery_min": 0.7, "volatility_max": 0.4},
    ),
    Module5Unit(
        id="module5-unit-2",
        title="Designing an Agent's Job",
        description="Defining what an agent should do — and what it should not do.",
        pages=[
            _page(
                "module5-unit-2",
                "Designing an Agent's Job",
                [
                    "Every agent needs a clear job.",
                    "You decide the agent's boundaries.",
                    "Good limits make agents safer and more useful.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.63,
        telemetry_requirements={"mastery_min": 0.7},
    ),
    Module5Unit(
        id="module5-unit-3",
        title="Building an Agent Step by Step",
        description="Creating an agent by combining Skills carefully.",
        pages=[
            _page(
                "module5-unit-3",
                "Building an Agent Step by Step",
                [
                    "Agents are created gradually.",
                    "Claude helps you assemble Skills.",
                    "You review and adjust each part.",
                ],
            )
        ],
        max_complexity=4,
        stability_threshold=0.6,
        telemetry_requirements={"strain_max": 0.35},
    ),
    Module5Unit(
        id="module5-unit-4",
        title="Using an Agent Safely",
        description="Working with agents while staying in control.",
        pages=[
            _page(
                "module5-unit-4",
                "Using an Agent Safely",
                [
                    "Agents assist, they do not decide.",
                    "You can pause or stop an agent anytime.",
                    "You always review the agent's output.",
                ],
            )
        ],
        max_complexity=4,
        stability_threshold=0.58,
        telemetry_requirements={"volatility_max": 0.35},
    ),
    Module5Unit(
        id="module5-unit-5",
        title="Staying the Authority",
        description="Reinforcing dignity, judgment, and control when using agents.",
        pages=[
            _page(
                "module5-unit-5",
                "Staying the Authority",
                [
                    "Agents exist to support your thinking.",
                    "Your judgment comes first.",
                    "You choose when and how agents are used.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.55,
        telemetry_requirements={"mastery_min": 0.75, "volatility_max": 0.3},
    ),
]


def get_module_5_unit(unit_id: str) -> Optional[Module5Unit]:
    for u in UNITS_MODULE_5:
        if u.id == unit_id:
            return u
    return None
