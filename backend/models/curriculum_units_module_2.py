"""Module 2 curriculum units: sustained, real-world use of Claude over time.

Distinct from Module 1 (orientation, safety, initial calibration). Module 2
focuses on maintenance, judgment, and repeated real-world use.

Library-grounded references: Carr (2009), Formosa (2012), Lövdén et al. (2010),
Park et al. (2014), Norman (2013), Fisk et al. (2009), Wiener (1948).
See ADR 0015.
"""

from typing import Optional

from backend.models.curriculum_units import (
    CurriculumPage,
    TelemetryGatedUnit,
)


Module2Unit = TelemetryGatedUnit


def _page(unit_id: str, title: str, lines: list) -> CurriculumPage:
    return CurriculumPage(
        id=f"{unit_id}-page-1",
        title=title,
        content=lines,
        complexity=1,
    )


UNITS_MODULE_2 = [
    Module2Unit(
        id="module2-unit-1",
        title="Coming Back to Claude",
        description="Re-engaging with Claude comfortably after time away.",
        pages=[
            _page(
                "module2-unit-1",
                "Coming Back to Claude",
                [
                    "Claude works the same each time you return.",
                    "You do not need to remember anything special.",
                    "It is okay to start fresh whenever you want.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.7,
        telemetry_requirements={"volatility_max": 0.45, "strain_max": 0.45},
    ),
    Module2Unit(
        id="module2-unit-2",
        title="Using Claude for Ongoing Decisions",
        description="Using Claude repeatedly to think through everyday choices.",
        pages=[
            _page(
                "module2-unit-2",
                "Using Claude for Ongoing Decisions",
                [
                    "Claude can help you think through similar situations more than once.",
                    "You can take your time and revisit ideas.",
                    "Nothing needs to be decided right away.",
                ],
            )
        ],
        max_complexity=3,
        stability_threshold=0.65,
        telemetry_requirements={"strain_max": 0.4, "mastery_min": 0.55},
    ),
    Module2Unit(
        id="module2-unit-3",
        title="Noticing When Claude Is Helpful",
        description="Developing awareness of when Claude adds value.",
        pages=[
            _page(
                "module2-unit-3",
                "Noticing When Claude Is Helpful",
                [
                    "Claude is useful for explaining, organizing, and thinking aloud.",
                    "You may notice some moments where it helps more than others.",
                    "You are always free to stop or change direction.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.6,
        telemetry_requirements={"volatility_max": 0.4, "mastery_min": 0.6},
    ),
    Module2Unit(
        id="module2-unit-4",
        title="Noticing When Claude Is Not the Best Choice",
        description="Recognizing situations where another approach is better.",
        pages=[
            _page(
                "module2-unit-4",
                "Noticing When Claude Is Not the Best Choice",
                [
                    "Some situations are better handled by people you trust.",
                    "Claude does not replace professionals or loved ones.",
                    "Choosing not to use Claude is part of good judgment.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.6,
        telemetry_requirements={"strain_max": 0.35, "mastery_min": 0.6},
    ),
    Module2Unit(
        id="module2-unit-5",
        title="Staying in Control Over Time",
        description="Maintaining confidence, agency, and calm with repeated AI use.",
        pages=[
            _page(
                "module2-unit-5",
                "Staying in Control Over Time",
                [
                    "You decide how Claude fits into your life.",
                    "Your experience and judgment always come first.",
                    "Claude remains a tool, not an authority.",
                ],
            )
        ],
        max_complexity=2,
        stability_threshold=0.55,
        telemetry_requirements={"volatility_max": 0.35, "mastery_min": 0.65},
    ),
]


def get_module_2_unit(unit_id: str) -> Optional[Module2Unit]:
    for u in UNITS_MODULE_2:
        if u.id == unit_id:
            return u
    return None
