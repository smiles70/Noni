"""Module 0 curriculum units: a calm, plain-language introduction to AI.

Module 0 is the primer that sits before Module 1 ("Meet Claude"). It
exists so a learner who has never heard the word "AI" used carefully
arrives at Module 1 with shared vocabulary and a non-anxious mental
model.

Pedagogical reference: the structure (six chapters covering "what AI
is", "how it figures things out", "where it already lives", "how it
learns from examples", "how today's helpers work", "what it means for
daily life") follows the public outline of the Elements of AI MOOC
(University of Helsinki + MinnaLearn). The text below is original;
no content is copied. Every example is grounded in a lived, geragogy-
appropriate moment.

Voice: identical to Module 1 (no jargon, no urgency, no fear framing).
Page schema: identical to Modules 1-3 (recap / context / principle /
example / retrieval). Plain CurriculumUnit (not TelemetryGatedUnit) —
the primer is intentionally ungated.
"""

from typing import Optional

from backend.models.curriculum import (
    ExampleBlock,
    RetrievalBlock,
    RetrievalChoice,
)
from backend.models.curriculum_units import (
    CurriculumPage,
    CurriculumUnit,
)


UNITS_MODULE_0 = [
    CurriculumUnit(
        id="module0-unit-1",
        title="What people mean when they say AI",
        description="A plain-language introduction to what AI actually is.",
        pages=[
            CurriculumPage(
                id="m0u1-context",
                title="A word you have been hearing",
                page_type="context",
                content=[
                    "AI is a word you have probably heard in the news, in advertisements, or from family. It sounds new, but the idea has been around since the 1950s.",
                    "AI is short for artificial intelligence. It means computers that can work with words and patterns, the way a person does — but only in narrow ways.",
                    "You have very likely used AI already, without thinking of it that way. The voice that gives directions on a phone is AI. So is the box that finishes your sentence when you search for something.",
                    "Read at your own pace. There is nothing to memorize.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u1-principle",
                title="AI is a kind of program, not a person",
                page_type="principle",
                principle="AI is a name for computers that handle words and patterns.",
                content=[
                    "AI is not magic. It is not a person. It is a useful kind of program.",
                    "The name has been around for many decades. What is new is how good these programs have gotten with everyday language.",
                    "When someone says \"the AI thinks\" or \"the AI feels\", they are using a shortcut. The program does not think and does not feel. It produces words.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u1-example",
                title="A familiar moment of AI",
                page_type="example",
                content=[
                    "Here is a small, ordinary moment that is actually AI.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You ask your phone for directions to the doctor's office. "
                        "A voice answers in spoken English."
                    ),
                    claude_says=(
                        "The shortest route is along Maple Street. "
                        "There is some traffic, so it may take ten extra minutes."
                    ),
                    takeaway=(
                        "That voice is one kind of AI. The first lesson of this short "
                        "module is just to notice that you have already been using it for years."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m0u1-retrieval",
                title="Which sentence describes AI?",
                page_type="retrieval",
                content=[
                    "Read both sentences. Pick the one that fits what you just learned.",
                    "There is no time limit. Either answer is a fine thing to think about.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Which sentence best describes what AI is?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="AI is a name for computers that work with words and patterns. You may have used it without thinking of it that way.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="AI is a single, all-knowing computer that thinks the way a person does.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "AI is a category of programs, not one program — and not a person. "
                        "Many ordinary things you already use are AI in this sense."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    CurriculumUnit(
        id="module0-unit-2",
        title="How AI tries to figure things out",
        description="The simple idea behind how AI programs reach an answer.",
        pages=[
            CurriculumPage(
                id="m0u2-recap",
                title="Where the last lesson left you",
                page_type="recap",
                content=[
                    "Last lesson you learned that AI is a name for computers that work with words and patterns.",
                    "This lesson is about how those programs actually try to work something out — like the shortest route, or the right word to use in a note.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u2-principle",
                title="AI works by trying many possibilities",
                page_type="principle",
                principle="AI works by trying many possibilities very quickly and keeping the ones that fit.",
                content=[
                    "When a program is asked for the shortest route, it does not simply know the answer. It tries many routes very fast, compares them, and keeps the shortest.",
                    "The cleverness is in the speed of trying, not in deep understanding.",
                    "This is closer to a librarian sorting cards into piles than to a person sitting in thought.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u2-example",
                title="Trying a few short titles",
                page_type="example",
                content=[
                    "Here is what \"trying many possibilities\" can look like for words instead of routes.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You wrote a short poem about your garden, and you ask Claude "
                        "to suggest a few possible titles."
                    ),
                    claude_says=(
                        "Here are three short options:\n\n"
                        "  The Quiet Garden.\n"
                        "  After the Rain.\n"
                        "  A Slow Morning.\n\n"
                        "Pick whichever fits the poem you wrote."
                    ),
                    takeaway=(
                        "Claude tried many short titles, kept a few that seemed fitting, "
                        "and offered them to you. It did not understand the poem the way you do — "
                        "it noticed patterns and offered suggestions."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m0u2-retrieval",
                title="How does AI usually arrive at an answer?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from the principle page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="How does an AI program usually arrive at an answer?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="It tries many possibilities very quickly and keeps the ones that fit best.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="It thinks the way a person thinks, with feelings and memories.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "The cleverness is in the speed of trying. There are no feelings, "
                        "no memories — only patterns."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    CurriculumUnit(
        id="module0-unit-3",
        title="Where you might already see AI",
        description="The quiet places AI is already part of ordinary life.",
        pages=[
            CurriculumPage(
                id="m0u3-recap",
                title="What we settled last time",
                page_type="recap",
                content=[
                    "You learned that AI works by trying many possibilities very quickly.",
                    "This lesson is about where this is happening already, in things you may already use without naming it AI.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u3-principle",
                title="AI is already a quiet part of many tools",
                page_type="principle",
                principle="AI is already a quiet part of many ordinary tools.",
                content=[
                    "GPS suggests driving routes. Email sorts spam into a separate folder. The camera on your phone groups pictures by who is in them.",
                    "The TV remote that listens for spoken commands is using AI. So is the search box that finishes your sentence as you type.",
                    "None of these announce themselves as \"AI\". They simply work.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u3-example",
                title="A photo album, sorted on its own",
                page_type="example",
                content=[
                    "Here is one of the quietest places AI shows up.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You take a photograph of your grandchildren at a birthday party. "
                        "The next day, your phone has grouped all the pictures from that "
                        "day into an album labeled \"Birthday\"."
                    ),
                    claude_says=(
                        "(Nothing — Claude is not part of this. The phone's photo program "
                        "did the sorting on its own, using AI that recognizes faces and dates.)"
                    ),
                    takeaway=(
                        "The phone did the work without being asked. That kind of quiet AI "
                        "has been in your life for a while."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m0u3-retrieval",
                title="Which of these uses AI?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one most likely to be using AI behind the scenes.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Which of these is most likely using AI behind the scenes?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="An email program that automatically moves junk mail into a separate folder.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="A pencil sharpening itself when you turn the handle.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Sorting mail is a pattern-recognition job — exactly what AI does. "
                        "A pencil sharpener is a simple machine, no AI involved."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    CurriculumUnit(
        id="module0-unit-4",
        title="How a computer learns by example",
        description="Where the patterns AI uses come from: many, many examples.",
        pages=[
            CurriculumPage(
                id="m0u4-recap",
                title="Where we are in Module 0",
                page_type="recap",
                content=[
                    "You saw AI quietly at work in everyday things — sorting mail, grouping photos, suggesting routes.",
                    "This lesson is about where the patterns AI uses actually come from. The answer is examples — many, many examples.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u4-principle",
                title="A computer learns the way a child does",
                page_type="principle",
                principle="A computer learns by being shown examples, the way a child does.",
                content=[
                    "Show a child enough pictures of dogs, and after a while they begin to recognize a dog they have never seen before.",
                    "AI works the same way — except the showing happens at huge scale, with millions of examples.",
                    "Nothing about that idea is strange. It is the same kind of learning a person has been doing their whole life.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u4-example",
                title="How a child learned the word 'dog'",
                page_type="example",
                content=[
                    "Here is a familiar moment that is the same shape as how AI learns.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You think back to how a grandchild first learned the word \"dog\". "
                        "Picture books. Pointing at the neighbor's terrier. The dog at the park. "
                        "After a while, the child knew."
                    ),
                    claude_says=(
                        "(Nothing — this is a moment of you noticing how learning by example "
                        "works. AI does the same thing, only with many more examples and "
                        "much faster.)"
                    ),
                    takeaway=(
                        "Learning from examples is a familiar idea. AI is not strange in this "
                        "way. It just does it at a scale a person could not."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m0u4-retrieval",
                title="How does a computer learn to recognize a cat?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="How does a computer 'learn' to recognize a cat in a picture?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="It is shown many pictures of cats, and slowly notices what they have in common.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Someone writes a list of every possible kind of cat into the program.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Lists like that would never finish. Learning from examples is what "
                        "makes AI workable for messy real things like pictures and sentences."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    CurriculumUnit(
        id="module0-unit-5",
        title="The idea behind today's AI helpers",
        description="A glimpse of how modern AI helpers turn learning into useful answers.",
        pages=[
            CurriculumPage(
                id="m0u5-recap",
                title="What we built last lesson",
                page_type="recap",
                content=[
                    "You learned that AI learns from many examples, the way a child does.",
                    "This lesson is a glimpse of how today's AI helpers — like the kind that can write a sentence back to you — turn that learning into useful answers.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u5-principle",
                title="Many small steps, each one a little clearer",
                page_type="principle",
                principle="Modern AI passes information through many small steps, and each step makes the answer a little clearer.",
                content=[
                    "Imagine a bucket brigade — a line of people passing buckets along.",
                    "Each person hands a slightly cleaner version of the message to the next. By the end, what started as a tangled question has become a clear answer.",
                    "That chain of small steps is what people sometimes call a \"neural network\". The name sounds technical; the idea is simple.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u5-example",
                title="A short answer, built from small steps",
                page_type="example",
                content=[
                    "Here is a small moment with a modern AI helper.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You type a question into Claude: \"What is a gentle activity for a "
                        "Sunday afternoon?\""
                    ),
                    claude_says=(
                        "Some quiet ideas:\n\n"
                        "  A slow walk around the block.\n"
                        "  A long phone call with someone you have been meaning to reach.\n"
                        "  An hour with a book and a cup of tea.\n\n"
                        "Pick whichever fits your mood today."
                    ),
                    takeaway=(
                        "The answer did not come from one big leap. It came from many small "
                        "steps inside the program — each step refining what came before, "
                        "until something readable came out."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m0u5-retrieval",
                title="How is a modern AI answer built?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="What is the rough idea behind how today's AI helpers produce an answer?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Information passes through many small steps, getting clearer at each one.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="The program looks the answer up in a giant printed dictionary.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "There is no dictionary. The answer is built up in pieces, step by "
                        "step, inside the program."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
    CurriculumUnit(
        id="module0-unit-6",
        title="What this means for your daily life",
        description="A calm closing thought before you meet a specific AI helper.",
        pages=[
            CurriculumPage(
                id="m0u6-recap",
                title="What Module 0 was about",
                page_type="recap",
                content=[
                    "Across this short module, you learned what AI is, how it works, where you already see it, how it learns, and the rough idea behind today's AI helpers.",
                    "This last lesson is the one that ties the others to you.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u6-principle",
                title="A quiet helper, not a stranger taking over",
                page_type="principle",
                principle="AI in your life is a quiet helper, not a stranger taking over.",
                content=[
                    "AI does not decide things for you. It offers — directions, words, suggestions, sorting.",
                    "You decide what to do with what it offers. That has been true your whole life with every tool, and it is true with this one too.",
                    "Nothing about your daily life has to change unless you want it to.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="m0u6-example",
                title="The shape of a calm relationship with AI",
                page_type="example",
                content=[
                    "Here is what a calm relationship with AI can look like, six months from now.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You are sending a birthday card to a grandchild. You start to write, "
                        "and you think for a moment about asking Claude for a fresh phrase. "
                        "You decide to write it yourself instead."
                    ),
                    claude_says=(
                        "(Nothing — Claude was not part of this moment. You chose to write "
                        "the card in your own words.)"
                    ),
                    takeaway=(
                        "The AI was available. You chose not to use it this time. That is "
                        "exactly the relationship a person should have with a tool: it serves "
                        "you, not the other way around."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="m0u6-retrieval",
                title="What is the right way to think about AI?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="What is the right way to think about AI in your daily life?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="It is a tool you can choose to use, or not, on your own terms.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="It is a force that will run my life whether I want it to or not.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "AI is a tool. The pace, the purpose, and the choice are all yours. "
                        "The next module introduces one specific AI helper, called Claude, "
                        "and shows you how to start using it calmly."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=1.2,
    ),
]


def get_module_0_unit(unit_id: str) -> Optional[CurriculumUnit]:
    """Lookup helper for Module 0 units. Returns None if id is unknown."""
    for u in UNITS_MODULE_0:
        if u.id == unit_id:
            return u
    return None
