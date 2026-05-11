"""Module 4 curriculum units: building and using Claude Skills.

Distinct from Modules 1-3 (orientation, sustained use, long-term judgment).
Module 4 moves the learner from "using Claude" to "teaching Claude once":
a Claude Skill is a named, reusable, explicitly defined instruction package
that Claude invokes when relevant.

Library-grounded references: Carr (2009), Formosa (2012), Craik & Salthouse
(2008), Lovden et al. (2010), Norman (2013), Fisk et al. (2009), Papert
(1980); Claude Skills architecture (Anthropic, 2025-2026). See ADR 0017.

Note: rendering Module 4 in the UI does not require Anthropic API access;
the content teaches *about* Skills declaratively. Actually creating Skills
end-to-end remains vendor-blocked.
"""

from typing import Dict, Optional

from pydantic import Field

from backend.models.curriculum_units import (
    CurriculumPage,
    CurriculumUnit as BaseCurriculumUnit,
)


class Module4Unit(BaseCurriculumUnit):
    """Module 4 unit. Mirrors Module2Unit / Module3Unit's telemetry-gated
    shape; per-learner enforcement deferred to the auth-vendor pass per
    ADR 0015 / 0016 / 0017."""

    telemetry_requirements: Dict[str, float] = Field(default_factory=dict)


def _page(unit_id: str, title: str, lines: list) -> CurriculumPage:
    return CurriculumPage(
        id=f"{unit_id}-page-1",
        title=title,
        content=lines,
        complexity=1,
    )


UNITS_MODULE_4 = [
    Module4Unit(
        id="module4-unit-1",
        title="What a Claude Skill Is",
        description="Understanding Skills as named, reusable instructions.",
        pages=[
            _page(
                "module4-unit-1",
                "What a Claude Skill Is",
                [
                    "A Claude Skill is something you teach once.",
                    "It has a name and a clear purpose.",
                    "Claude uses it when it knows it will help.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.7,
        telemetry_requirements={"mastery_min": 0.6, "volatility_max": 0.45},
    ),
    Module4Unit(
        id="module4-unit-2",
        title="When a Skill Is Useful",
        description="Learning when a Skill helps more than repeating instructions.",
        pages=[
            _page(
                "module4-unit-2",
                "When a Skill Is Useful",
                [
                    "Skills are useful for things you do often.",
                    "They reduce the need to explain yourself again.",
                    "Not everything needs to be a Skill.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.68,
        telemetry_requirements={"strain_max": 0.4},
    ),
    Module4Unit(
        id="module4-unit-3",
        title="Creating Your First Skill",
        description="Building a simple Skill with Claude's help.",
        pages=[
            _page(
                "module4-unit-3",
                "Creating Your First Skill",
                [
                    "Claude can help you create a Skill step by step.",
                    "You explain what you want the Skill to do.",
                    "Claude writes the Skill instructions for review.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.66,
        telemetry_requirements={"mastery_min": 0.65},
    ),
    Module4Unit(
        id="module4-unit-4",
        title="Naming and Describing a Skill",
        description="Making Skills clear, readable, and trustworthy.",
        pages=[
            _page(
                "module4-unit-4",
                "Naming and Describing a Skill",
                [
                    "A good name explains what the Skill does.",
                    "A good description explains when it should be used.",
                    "Clear Skill names build confidence.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.64,
        telemetry_requirements={"volatility_max": 0.4},
    ),
    Module4Unit(
        id="module4-unit-5",
        title="Testing and Refining a Skill",
        description="Checking that a Skill behaves the way you expect.",
        pages=[
            _page(
                "module4-unit-5",
                "Testing and Refining a Skill",
                [
                    "Skills can be tested safely.",
                    "You can adjust the instructions anytime.",
                    "Nothing is permanent or automatic.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.62,
        telemetry_requirements={"strain_max": 0.35},
    ),
    Module4Unit(
        id="module4-unit-6",
        title="Trusting a Skill Over Time",
        description="Using Skills confidently while staying in control.",
        pages=[
            _page(
                "module4-unit-6",
                "Trusting a Skill Over Time",
                [
                    "Skills support you, not replace you.",
                    "You can stop using a Skill at any time.",
                    "You remain the decision-maker.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.6,
        telemetry_requirements={"mastery_min": 0.7},
    ),
]


def get_module_4_unit(unit_id: str) -> Optional[Module4Unit]:
    for u in UNITS_MODULE_4:
        if u.id == unit_id:
            return u
    return None
