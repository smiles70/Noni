"""Curriculum Units 2-4 data model.

Pure data. Selection of which page to render is performed by the
canonical ISCS (`backend.core.interface_control.state_selector`).
"""

from typing import List, Optional
from pydantic import BaseModel

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
]


def get_unit(unit_id: str) -> Optional[CurriculumUnit]:
    """Lookup helper. Returns None if unit_id is unknown."""
    for u in UNITS:
        if u.id == unit_id:
            return u
    return None
