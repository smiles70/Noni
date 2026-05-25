"""Module 2 curriculum units: sustained, real-world use of Claude over time.

Distinct from Module 1 (orientation, safety, initial calibration). Module 2
focuses on maintenance, judgment, and repeated real-world use.

Library-grounded references: Carr (2009), Formosa (2012), Lövdén et al. (2010),
Park et al. (2014), Norman (2013), Fisk et al. (2009), Wiener (1948).
See ADR 0015.
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

Module2Unit = TelemetryGatedUnit


# S25.2: Module 2 re-authored as four-page lessons mirroring Module 1.
# Each unit: recap -> principle -> example -> retrieval. All page
# complexities respect the unit's max_complexity ceiling so the legacy
# ISCS single-page route still has admissible pages.

UNITS_MODULE_2 = [
    Module2Unit(
        id="module2-unit-1",
        title="Coming Back to Claude",
        description="Re-engaging with Claude comfortably after time away.",
        pages=[
            CurriculumPage(
                id="m2u1-recap",
                title="Where Module 1 left you",
                page_type="recap",
                content=[
                    "Module 1 left you with a quiet rule: Claude offers words, and you decide what to do with them.",
                    "Module 2 is about what happens later — when you come back to Claude after a day, a week, or longer.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u1-principle",
                title="Claude does not remember you",
                page_type="principle",
                principle="Each time you return, Claude begins fresh. There is nothing to catch up on.",
                content=[
                    "Claude does not keep a memory of past conversations the way a friend does.",
                    "That can sound strange at first, but it is also a kindness: nothing follows you between visits.",
                    "You can pick up a new topic, or a familiar one, without explaining yourself.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u1-example",
                title="Returning after a week away",
                page_type="example",
                content=[
                    "Here is what coming back to Claude looks like.",
                ],
                example=ExampleBlock(
                    situation=(
                        "It has been a week since you last used Claude. You open the page and the box is empty, "
                        'the way it always is. You type: "Hello again — could you help me plan a small grocery list?"'
                    ),
                    claude_says=(
                        "Of course. Here is a short starter list, organized by the kind of meal:\n\n"
                        "  Breakfast: oats, milk, fruit.\n"
                        "  Lunch: bread, cheese, soup.\n"
                        "  Dinner: a vegetable, a starch, a small portion of protein.\n\n"
                        "Tell me what you usually keep on hand, and I can adjust this."
                    ),
                    takeaway=(
                        "Claude met you where you were. The week away did not matter."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="m2u1-retrieval",
                title="Which is true about coming back?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches what you just learned.",
                ],
                retrieval=RetrievalBlock(
                    prompt="What should you do when you return to Claude after a long break?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Just type what you need today. Claude will start fresh with you.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Carefully remind Claude of every past conversation before asking anything new.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude does not keep a memory between sessions. Each visit starts clean."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m2u2-recap",
                title="What we settled last lesson",
                page_type="recap",
                content=[
                    "You learned that Claude starts fresh each time you come back.",
                    "This lesson is about returning on purpose — using Claude as a steady thinking aid across the week.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u2-principle",
                title="Claude is a thinking aid, not a decider",
                page_type="principle",
                principle="Claude can help you think through the same kind of choice more than once. The choice stays yours.",
                content=[
                    "Some decisions come back every week: what to eat, when to call a friend, how to fill an afternoon.",
                    "You can talk these over with Claude as often as you like. The next answer is not bound by the last one.",
                    "Nothing here has to be settled today. The conversation waits for you.",
                ],
                complexity=2,
            ),
            CurriculumPage(
                id="m2u2-example",
                title="Planning the same meal, two weeks apart",
                page_type="example",
                content=[
                    "Here is the same person asking the same kind of question, twice.",
                ],
                example=ExampleBlock(
                    situation=(
                        'On a Monday you ask Claude: "Could you help me plan a simple supper for tonight?" '
                        "Two weeks later, on another Monday, you ask the same thing again."
                    ),
                    claude_says=(
                        "Of course. Here is one calm option: a baked potato with butter, "
                        "a soft-boiled egg, and a small green salad. If you want something "
                        "warmer, I can suggest a soup instead. Either way, only what sounds "
                        "good to you tonight."
                    ),
                    takeaway=(
                        "The same question can be asked again. Each time, you get a starting point "
                        "and the decision still belongs to you."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="m2u2-retrieval",
                title="Which use of Claude keeps the decision yours?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the principle from the last page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="You use Claude weekly to help plan a meal. Which approach fits the lesson?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Ask Claude for a starting idea, then choose what actually goes on the plate.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Cook exactly what Claude suggests, every time, without changes.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude is a thinking aid. The starting idea is useful; the choice is still yours."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m2u3-recap",
                title="Where we are in Module 2",
                page_type="recap",
                content=[
                    "You have learned that Claude starts fresh each visit, and that you can use it as a steady thinking aid over time.",
                    "This lesson is about paying attention — noticing which kinds of tasks Claude actually helps with.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u3-principle",
                title="Claude shines at three quiet jobs",
                page_type="principle",
                principle="Claude is most useful for explaining, organizing, and thinking aloud.",
                content=[
                    "Explaining: turning something complicated into shorter words.",
                    "Organizing: putting a jumble of ideas into a list, an order, or a plan.",
                    "Thinking aloud: helping you hear what you already half-believe.",
                    "Outside of these, Claude can still help — but the help is less reliable.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u3-example",
                title="A task that suits Claude, and one that does not",
                page_type="example",
                content=[
                    "Here are two requests that look similar and land very differently.",
                ],
                example=ExampleBlock(
                    situation=(
                        'Request A: "Could you help me organize a short calendar reminder for '
                        "my granddaughter's recital?\"\n\n"
                        'Request B: "Could you write a personal eulogy for my husband?"'
                    ),
                    claude_says=(
                        "For A, I can offer something clean and clear:\n"
                        "  Saturday, 3:00 PM — Lila's recital, school auditorium.\n\n"
                        "For B, I can help shape phrases if you would like, but the heart of a eulogy "
                        "is yours to write. Anything I draft would be a placeholder for your own words."
                    ),
                    takeaway=(
                        "Organizing a reminder suits Claude well. Carrying personal meaning is "
                        "still your job — Claude can hand you words, but not feeling."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="m2u3-retrieval",
                title="Which task suits Claude best?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one Claude is most reliably helpful with.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Which task is Claude best suited to help with?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Organizing a list of errands into the order that makes sense.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Writing the heartfelt center of a personal letter for you.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Organizing is one of the quiet jobs Claude does well. The heart of a letter is yours."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m2u4-recap",
                title="The flip side of last lesson",
                page_type="recap",
                content=[
                    "Last lesson you learned what Claude is best at: explaining, organizing, thinking aloud.",
                    "This lesson is the flip side — knowing when not to ask Claude at all.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u4-principle",
                title="Some questions belong to people, not AI",
                page_type="principle",
                principle="A doctor, a trusted friend, or a quiet moment alone is sometimes the right answer.",
                content=[
                    "Claude does not know your body, your history, or the room you are sitting in.",
                    "For matters of health, money, or grief, a person who knows you is almost always the better first stop.",
                    "Choosing not to ask Claude is not a failure of the tool. It is a sign you understand what the tool is for.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u4-example",
                title="A question to keep for a person",
                page_type="example",
                content=[
                    "Here is a question Claude can answer — and shouldn't be the only one to.",
                ],
                example=ExampleBlock(
                    situation=(
                        'You ask Claude: "My hand has been feeling numb in the morning. '
                        'What could be causing this?"'
                    ),
                    claude_says=(
                        "There are several common reasons people describe a sensation like that, "
                        "but I am not the right place to settle it. A doctor — even a short phone "
                        "call to your usual one — is who I would want telling you what to do next."
                    ),
                    takeaway=(
                        "Claude pointed you toward a person. That is the right shape of help for "
                        "this kind of question."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="m2u4-retrieval",
                title="Which question is better for a person?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that belongs to a person who knows you.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Which question is better asked of a person you trust, not Claude?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text='"Should I be worried about a new pain in my chest?"',
                        ),
                        RetrievalChoice(
                            id="b",
                            text='"Can you organize my weekly errands into a tidy list?"',
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Health questions belong with a person who can see you. Errands are a fine "
                        "job for Claude."
                    ),
                ),
                complexity=1,
            ),
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
            CurriculumPage(
                id="m2u5-recap",
                title="What Module 2 was about",
                page_type="recap",
                content=[
                    "Module 2 has been about steady, repeated use of Claude over weeks and months.",
                    "This last lesson is the rule that ties the others together.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u5-principle",
                title="You decide how Claude fits into your life",
                page_type="principle",
                principle="Claude is a tool. You decide how often, for what, and whether at all.",
                content=[
                    "Some people will use Claude every day. Some will use it once a month. Both are fine.",
                    "Your experience and judgment came before Claude, and they will outlast it.",
                    "If a habit with Claude starts to feel like a chore, that is information. You can change it.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m2u5-example",
                title="One learner's quiet pace",
                page_type="example",
                content=[
                    'Here is what "staying in control" looks like for one person.',
                ],
                example=ExampleBlock(
                    situation=(
                        "After a few months of using Claude, you notice you only really reach for it "
                        "on Sunday evenings, when you plan the week. The rest of the time, you do "
                        "not miss it."
                    ),
                    claude_says=(
                        "(There is nothing for Claude to say here — this is a moment of you "
                        "noticing your own rhythm.)"
                    ),
                    takeaway=(
                        "A weekly visit is a fine relationship with a tool. You are in charge "
                        "of the rhythm."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="m2u5-retrieval",
                title="Who decides how much Claude to use?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches the rule from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Who decides how much Claude belongs in your life?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="You do, based on what is useful and comfortable for you.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Claude does, by being available whenever you open the page.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude is a tool. The pace and the purpose are yours to set."
                    ),
                ),
                complexity=1,
            ),
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
