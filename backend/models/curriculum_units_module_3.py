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

from backend.models.curriculum import (
    ExampleBlock,
    RetrievalBlock,
    RetrievalChoice,
)
from backend.models.curriculum_units import (
    CurriculumPage,
    TelemetryGatedUnit,
)

Module3Unit = TelemetryGatedUnit


# S25.3: Module 3 re-authored as four-page lessons. Every unit's
# max_complexity is 1 (Module 3 is declarative/protective by design),
# so every page - including examples - is held at complexity=1. The
# example blocks are deliberately short and concrete to fit that
# cognitive ceiling.

UNITS_MODULE_3 = [
    Module3Unit(
        id="module3-unit-1",
        title="Claude Is Not an Authority",
        description="Reinforcing that Claude offers suggestions, not answers.",
        pages=[
            CurriculumPage(
                id="m3u1-recap",
                title="Where Module 2 left you",
                page_type="recap",
                content=[
                    "Module 2 ended with a quiet rule: you decide how Claude fits into your life.",
                    "Module 3 is the protective module. It exists to keep that rule strong, even after years of using AI.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u1-principle",
                title="A confident voice is not a correct voice",
                page_type="principle",
                principle="Claude can sound sure even when it is wrong. Sounding sure is not the same as being right.",
                content=[
                    "Claude is not a doctor, a lawyer, a teacher, or a friend.",
                    "Claude is a tool that produces words. The words can be useful. They are not the truth itself.",
                    "You are the one who knows your life. That has not changed and will not change.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u1-example",
                title="A confident-sounding wrong answer",
                page_type="example",
                content=[
                    'Here is what "confident but wrong" can look like.',
                ],
                example=ExampleBlock(
                    situation=(
                        "You ask Claude what year a book was published. "
                        "Claude answers cleanly, with a single year and no hedge."
                    ),
                    claude_says=("That book came out in 1962."),
                    takeaway=(
                        "The answer might be right. It might also be off by ten years. "
                        "The clean voice is not proof. A library catalog or the cover of "
                        "the book itself is the right place to settle it."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m3u1-retrieval",
                title="Who is the authority on what is right for you?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from the principle page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Who is the authority on what is right for you?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="You are. Claude is one voice you may consult, not the deciding one.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Claude is. It speaks with confidence, so it must know best.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude is a tool. The authority over your life is, and stays, you."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m3u2-recap",
                title="What we just settled",
                page_type="recap",
                content=[
                    "You learned that Claude can sound sure even when it is wrong.",
                    "This lesson is the next step: keeping your own thinking strong by actually using it.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u2-principle",
                title="Skills stay sharp by being used",
                page_type="principle",
                principle="Using your own judgment keeps your judgment strong.",
                content=[
                    "If Claude does the thinking every time, your own thinking gets quieter.",
                    "Sometimes that is fine. Sometimes it is the difference between a habit and a crutch.",
                    "Doing a small task yourself - a list, a reply, a calculation - is a kind of exercise.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u2-example",
                title="A small task done two ways",
                page_type="example",
                content=[
                    "Here is the same task handled two ways.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You need to add up the cost of three small items at the store. "
                        "You could ask Claude. You could also do the sum yourself."
                    ),
                    claude_says=(
                        "I can add those up for you. But you can also: take a breath, "
                        "add them in your head, and trust the answer you get."
                    ),
                    takeaway=(
                        "Some small tasks are worth doing yourself. Each one is a quiet "
                        "way of telling your mind it is still in charge."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m3u2-retrieval",
                title="Which approach keeps your skills sharp?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches the rule from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="A small task could be done by you or by Claude. Which keeps your skills sharper?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Doing the small task yourself, when you have the time.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Asking Claude to do it every time, even the small ones.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Skills stay sharp by being used. Small tasks are good practice."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m3u3-recap",
                title="The thread so far",
                page_type="recap",
                content=[
                    "You learned that using your own judgment keeps it strong.",
                    "This lesson is the second half of that idea: sometimes the best move is to use Claude less, or not at all.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u3-principle",
                title="Stepping away is a strength",
                page_type="principle",
                principle="Choosing not to use Claude is a sign of strength, not failure.",
                content=[
                    "Some afternoons, the right move is to put the screen down.",
                    "Some questions deserve quiet, or a person, or a walk.",
                    "Putting Claude aside for an hour, a day, or a week takes nothing away from what you have learned.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u3-example",
                title="A quiet afternoon without Claude",
                page_type="example",
                content=[
                    'Here is what "stepping away" can look like.',
                ],
                example=ExampleBlock(
                    situation=(
                        "It is Sunday afternoon. You had thought about asking Claude to "
                        "help plan the week, but you also feel like reading on the porch."
                    ),
                    claude_says=("(Nothing. The page stays closed.)"),
                    takeaway=(
                        "The afternoon was yours. Claude will be there next time you want it."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m3u3-retrieval",
                title="Pausing — weakness or strength?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches the rule from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="You decide not to use Claude for a week. What is true of that choice?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="It is a sign of strength: you set the pace, not the tool.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="It is a sign of failure: you should have kept practicing.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Stepping away is part of using a tool well. Nothing is lost."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m3u4-recap",
                title="What the whole course was about",
                page_type="recap",
                content=[
                    "You started this course not knowing what Claude was. You end it knowing more than most people about how to use AI well.",
                    "This last lesson is short. It is the rule that holds the rest together.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u4-principle",
                title="You remain the decision-maker",
                page_type="principle",
                principle="Claude is a tool. You are the person. The decisions are yours.",
                content=[
                    "Through every lesson, the rule has been the same: Claude offers, you decide.",
                    "That rule does not change with practice or with time. It deepens.",
                    "You are capable, you are thoughtful, and you are in charge of your own life.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m3u4-example",
                title="The shape of a healthy relationship with a tool",
                page_type="example",
                content=[
                    "Here is what the course is asking you to carry forward.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Six months from now, you are deciding whether to use Claude for "
                        "something small or to handle it yourself. You think about it for a moment."
                    ),
                    claude_says=(
                        "(Nothing — Claude is not part of this moment yet, and may not need to be.)"
                    ),
                    takeaway=(
                        "The pause itself is the point. You thought before you reached. "
                        "That is what the whole course was for."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m3u4-retrieval",
                title="Who decides?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches the rule that ties this course together.",
                ],
                retrieval=RetrievalBlock(
                    prompt="At the end of the course, who decides how Claude fits into your life?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="You do. That has been true the whole time.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Claude does, by being available whenever you open the page.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "You are the decision-maker. The course exists to keep that true."
                    ),
                ),
                complexity=1,
            ),
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
