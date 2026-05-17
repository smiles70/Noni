"""Curriculum Units 2-7 data model.

Pure data. Selection of which page to render is performed by the
canonical ISCS (`backend.core.interface_control.state_selector`).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.models.curriculum import (
    CurriculumPage,
    ExampleBlock,
    RetrievalBlock,
    RetrievalChoice,
)


class CurriculumUnit(BaseModel):
    id: str
    title: str
    description: str
    pages: List[CurriculumPage]
    max_complexity: int
    stability_threshold: float


UNITS: List[CurriculumUnit] = [
    # ---- Unit 1: "Meet Claude" foundation lesson (Sprint 24) ---------------
    # Authored to fill the conceptual gap before unit-2: a learner arriving
    # at the free track had no shared vocabulary for what "AI" means or
    # what "Claude" is. Four pages, all complexity=1, using the same four
    # page types unit-2 introduced. No new schema, no new components.
    CurriculumUnit(
        id="unit-1",
        title="Meet Claude",
        description="What AI is, what Claude is, and where you find it.",
        pages=[
            CurriculumPage(
                id="u1-context",
                title="What 'AI' means, in plain words",
                page_type="context",
                content=[
                    "AI is short for artificial intelligence. It means computers that can work with words, the way a person does.",
                    "You have probably used AI already, without thinking of it that way. The voice that gives directions on a phone is AI. So is the search box that finishes your sentence for you.",
                    "AI is not magic, and it is not a person. It is a tool. A useful one, but still a tool.",
                    "This first lesson is just a short introduction. There is nothing to do and nothing to remember. Read at your own pace.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u1-principle",
                title="Claude is one of many AI helpers",
                page_type="principle",
                principle="Claude is an AI helper. The company that makes Claude is called Anthropic.",
                content=[
                    "Many companies make AI helpers. Anthropic is one of them. Claude is the name of the helper they make.",
                    "You may have heard other names — for example, ChatGPT or Gemini. Those are different helpers, made by different companies. They are not Claude.",
                    "This course is about Claude. Once you are comfortable with Claude, the other helpers work in much the same way.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u1-example",
                title="What it looks like when you visit Claude",
                page_type="example",
                content=[
                    "Here is what meeting Claude for the first time looks like.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You open a web browser and go to the address claude.ai. "
                        "A page opens with a single empty box at the bottom, waiting for you to type. "
                        'You type: "Hello, Claude. I am learning about you."'
                    ),
                    claude_says=(
                        "Hello, and welcome. I am Claude, an AI assistant made by Anthropic. "
                        "I am happy to help you learn at whatever pace feels right. "
                        "If you have a question, or just want to try something, you can type it in the box below."
                    ),
                    takeaway=(
                        "Claude lives on a website. You reach it the same way you reach any "
                        "other website — by typing the address in your browser."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="u1-retrieval",
                title="Which sentence describes Claude?",
                page_type="retrieval",
                content=[
                    "Read both sentences. Pick the one that matches what you just learned.",
                    "There is no time limit. Either answer is a fine thing to think about.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Which sentence describes Claude best?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Claude is an AI helper made by Anthropic. You reach it on a website.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Claude is a small robot that lives inside your computer.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude is software, not a robot. The company called Anthropic makes it, "
                        "and you reach it on a website like claude.ai."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    # ---- Unit 2: full Phase-1 expansion exemplar ----------------------------
    # Four page types (context / principle / example / retrieval). All pages
    # are complexity=1 to respect unit.max_complexity=1, which the legacy
    # ISCS path also relies on. Authored to the geragogy guidance: short
    # sentences, concrete words, no jargon, no imperatives implying rush,
    # confidence-preserving framing. The "recap" page-type is omitted here
    # because this is the first free-track lesson — there is nothing to
    # recap. Subsequent units may begin with a recap page in Phase 2.
    CurriculumUnit(
        id="unit-2",
        title="What Is Claude",
        description="Understand Claude as a supportive language assistant, not an authority.",
        pages=[
            CurriculumPage(
                id="u2-context",
                title="What changes when you use Claude",
                page_type="context",
                content=[
                    "Claude is a writing helper. You type words, and Claude writes words back.",
                    "Claude does not see your screen. It does not press buttons. It only puts words on the page.",
                    "Nothing happens until you decide it should. You read what Claude wrote, and then you choose what to do with it.",
                    "There is no rush in this lesson. You can read each page as slowly as you like.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u2-principle",
                title="The one rule to carry with you",
                page_type="principle",
                principle="Claude offers words. You decide what to do with them.",
                content=[
                    "This is the rule the rest of the course is built on.",
                    "Claude can suggest, draft, or explain. It cannot decide for you, and it does not act on its own.",
                    "If a suggestion does not feel right, you can ignore it. Nothing is lost.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u2-example",
                title="What it might look like",
                page_type="example",
                content=[
                    "Here is a small, ordinary moment of using Claude.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You want to send a short note to a friend who has been "
                        "unwell. You ask Claude to help you find the right words."
                    ),
                    claude_says=(
                        "Here is one way to start:\n\n"
                        '  "I have been thinking about you. There is no need to write '
                        'back — I just wanted you to know."\n\n'
                        "Change anything that does not sound like you."
                    ),
                    takeaway=(
                        "Claude offered a starting point. You stay the author of the note."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="u2-retrieval",
                title="Which one matches the rule?",
                page_type="retrieval",
                content=[
                    "Read both options. Pick the one that fits the rule from the last page.",
                    "There is no time limit. Either choice is a fine answer to think about.",
                ],
                retrieval=RetrievalBlock(
                    prompt=(
                        "Claude suggests a sentence for your note. What is the next step?"
                    ),
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Read the sentence and decide whether to use it, change it, or set it aside.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Send the sentence right away because Claude wrote it.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude offers words; you decide what to do with them. "
                        "Reading first, then choosing, keeps the decision yours."
                    ),
                ),
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
