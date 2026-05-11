"""Module 3 curriculum units: long-term judgment, recalibration, and
autonomy with Claude.

Distinct from Module 1 (orientation/safety) and Module 2 (sustained everyday
use). Module 3 is declarative, protective, and dignity-preserving: it exists
to defend long-term judgment, prevent over-trust or dependency, and
explicitly recalibrate the learner's relationship with AI.

Library-grounded references: Carr (2009), Formosa (2012), Lövdén et al. (2010),
Norman (2013), Fisk et al. (2009), Wiener (1948). See ADR 0016.
"""

from typing import Optional


from backend.models.curriculum_units import (
    CurriculumPage,
    TelemetryGatedUnit,
)


Module3Unit = TelemetryGatedUnit


def _page(unit_id: str, title: str, lines: list) -> CurriculumPage:
    return CurriculumPage(
        id=f"{unit_id}-page-1",
        title=title,
        content=lines,
        complexity=1,
    )


UNITS_MODULE_3 = [
    Module3Unit(
        id="module3-unit-1",
        title="Claude Is Not an Authority",
        description="Reinforcing that Claude offers suggestions, not answers.",
        pages=[
            _page(
                "module3-unit-1",
                "Claude Is Not an Authority",
                [
                    "Claude can sound confident even when it is mistaken.",
                    "Claude does not replace your judgment.",
                    "You always decide what to accept or ignore.",
                ],
            )
        ],
        max_complexity=1,
        stability_threshold=0.65,
        telemetry_requirements={"volatility_max": 0.4, "mastery_min": 0.65},
    ),
    Module3Unit(
        id="module3-unit-2",
        title="Keeping Your Judgment Sharp",
        description="Maintaining personal decision-making alongside AI use.",
        pages=[
            _page(
                "module3-unit-2",
                "Keeping Your Judgment Sharp",
                [
                    "Claude can support your thinking, not replace it.",
                    "Your experience matters more than any response.",
                    "Using your own judgment keeps skills strong.",
                ],
            )
        ],
        max_complexity=1,
        stability_threshold=0.6,
        telemetry_requirements={"strain_max": 0.35, "mastery_min": 0.7},
    ),
    Module3Unit(
        id="module3-unit-3",
        title="Knowing When to Pause or Step Away",
        description="Recognizing when not using Claude is a healthy choice.",
        pages=[
            _page(
                "module3-unit-3",
                "Knowing When to Pause or Step Away",
                [
                    "Not every situation needs AI support.",
                    "It is okay to pause or stop using Claude.",
                    "Choosing when to step away is a strength.",
                ],
            )
        ],
        max_complexity=1,
        stability_threshold=0.55,
        telemetry_requirements={"volatility_max": 0.35, "mastery_min": 0.7},
    ),
    Module3Unit(
        id="module3-unit-4",
        title="You Remain the Decision-Maker",
        description="Consolidating autonomy, confidence, and dignity in AI use.",
        pages=[
            _page(
                "module3-unit-4",
                "You Remain the Decision-Maker",
                [
                    "Claude is a tool you control.",
                    "Your choices define how Claude fits into your life.",
                    "You remain capable, thoughtful, and in control.",
                ],
            )
        ],
        max_complexity=1,
        stability_threshold=0.5,
        telemetry_requirements={"volatility_max": 0.3, "mastery_min": 0.75},
    ),
]


def get_module_3_unit(unit_id: str) -> Optional[Module3Unit]:
    for u in UNITS_MODULE_3:
        if u.id == unit_id:
            return u
    return None
