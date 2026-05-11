"""Curriculum Units 2-7 data model.

Pure data. Selection of which page to render is performed by the
canonical ISCS (`backend.core.interface_control.state_selector`).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.models.curriculum import CurriculumPage


class CurriculumUnit(BaseModel):
    id: str
    title: str
    description: str
    pages: List[CurriculumPage]
    max_complexity: int
    stability_threshold: float


UNITS: List[CurriculumUnit] = [
    CurriculumUnit(
        id="unit-2",
        title="What Is Claude",
        description="Understand Claude as a supportive language assistant, not an authority.",
        pages=[
            CurriculumPage(
                id="u2-p1",
                title="What Is Claude",
                content=[
                    "Claude is a tool that responds to words.",
                    "Claude does not decide or act on its own.",
                    "You can question, change, or ignore Claude.",
                ],
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    CurriculumUnit(
        id="unit-3",
        title="How to Use Claude Safely",
        description="Practice safe, reversible interaction with Claude.",
        pages=[
            CurriculumPage(
                id="u3-p1",
                title="Asking for Help",
                content=[
                    "Ask for help using simple language.",
                    "You can always say no to a suggestion.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u3-p2",
                title="Reading and Trying Again",
                content=[
                    "Read suggestions without rushing.",
                    "Ask Claude to try again if a suggestion is unclear.",
                    "Confirm before using anything Claude proposes.",
                ],
                complexity=2,
            ),
        ],
        max_complexity=2,
        stability_threshold=1.0,
    ),
    CurriculumUnit(
        id="unit-4",
        title="Claude-Based Projects",
        description="Create meaningful, practical results with Claude.",
        pages=[
            CurriculumPage(
                id="u4-p1",
                title="A Friendly Note",
                content=["Write a friendly note to someone you care about."],
                complexity=1,
            ),
            CurriculumPage(
                id="u4-p2",
                title="A Hobby You Enjoy",
                content=[
                    "Learn about a hobby you enjoy.",
                    "Ask Claude one question at a time.",
                ],
                complexity=2,
            ),
            CurriculumPage(
                id="u4-p3",
                title="A Daily Checklist",
                content=[
                    "Create a checklist for daily life.",
                    "Review and confirm each item before saving.",
                    "Edit anything that does not feel right.",
                ],
                complexity=3,
            ),
        ],
        max_complexity=3,
        stability_threshold=0.8,
    ),
    CurriculumUnit(
        id="unit-5",
        title="Verifying Claude's Suggestions",
        description="Build the habit of checking what Claude says before acting on it.",
        pages=[
            CurriculumPage(
                id="u5-p1",
                title="Read Before You Use",
                content=[
                    "Always read what Claude writes before you use it.",
                    "Take your time. There is no rush.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u5-p2",
                title="Compare With What You Know",
                content=[
                    "Compare Claude's answer to what you already know.",
                    "If something feels off, set it aside.",
                    "Ask Claude to explain its reasoning in simple words.",
                ],
                complexity=2,
            ),
        ],
        max_complexity=2,
        stability_threshold=1.0,
    ),
    CurriculumUnit(
        id="unit-6",
        title="When to Ignore Claude",
        description="Recognize that your judgment matters more than any AI suggestion.",
        pages=[
            CurriculumPage(
                id="u6-p1",
                title="Your Judgment Comes First",
                content=[
                    "You are the decision-maker.",
                    "Claude is only a helper.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u6-p2",
                title="Signals to Pause",
                content=[
                    "Stop if anything feels rushed or unclear.",
                    "Claude can be wrong. That is normal.",
                    "Setting Claude aside is always a valid choice.",
                ],
                complexity=2,
            ),
        ],
        max_complexity=2,
        stability_threshold=1.0,
    ),
    CurriculumUnit(
        id="unit-7",
        title="Recovering from a Mistake",
        description="Mistakes are part of learning. Practice making them small and easy to undo.",
        pages=[
            CurriculumPage(
                id="u7-p1",
                title="Mistakes Are Normal",
                content=[
                    "Everyone makes mistakes when learning something new.",
                    "A mistake is information, not failure.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u7-p2",
                title="Undoing and Stepping Back",
                content=[
                    "Most actions can be undone. Take your time to find the undo step.",
                    "If something feels wrong, take a break.",
                    "Come back when you are ready. Nothing is lost by waiting.",
                ],
                complexity=2,
            ),
        ],
        max_complexity=2,
        stability_threshold=0.9,
    ),
]


def get_unit(unit_id: str) -> Optional[CurriculumUnit]:
    """Lookup helper. Returns None if unit_id is unknown."""
    for u in UNITS:
        if u.id == unit_id:
            return u
    return None


class TelemetryGatedUnit(CurriculumUnit):
    """Shared base for telemetry-gated curriculum modules (Modules 2-4+).

    Adds typed `telemetry_requirements` so per-learner gating on
    volatility / strain / mastery can be enforced once per-learner state lands.
    Until then the field is recorded in audit telemetry per ADR 0009 / 0015.
    Extracted in Sprint 20 (ADR 0018) after Module2Unit / Module3Unit /
    Module4Unit were observed to carry identical fields.
    """

    telemetry_requirements: Dict[str, float] = Field(default_factory=dict)
