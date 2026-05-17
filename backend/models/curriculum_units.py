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
    # ---- Unit 3: re-authored as a four-page lesson (Sprint 23 completion) --
    # First unit to use the `recap` page_type — the carried-over thread from
    # the previous lesson. max_complexity=2 preserved so the legacy ISCS path
    # still has admissible pages.
    CurriculumUnit(
        id="unit-3",
        title="How to Use Claude Safely",
        description="Practice safe, reversible interaction with Claude.",
        pages=[
            CurriculumPage(
                id="u3-recap",
                title="Where we were",
                page_type="recap",
                content=[
                    "Last lesson, you met Claude: an AI helper that offers words, and leaves the decisions to you.",
                    "This lesson is about how to ask Claude for help in a way that keeps things calm and reversible.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u3-principle",
                title="Ask in plain words",
                page_type="principle",
                principle="You can ask Claude the same way you would ask a friend.",
                content=[
                    "Claude is built to understand everyday language. There are no special commands to learn.",
                    "Short, plain sentences work best. If a request is unclear, you can ask again with different words.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u3-example",
                title="A small ask",
                page_type="example",
                content=[
                    "Here is what a plain-words ask might look like.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You want a short thank-you note for a neighbor who brought in your mail. "
                        'You type: "Can you help me write a short thank-you to a neighbor who picked up my mail?"'
                    ),
                    claude_says=(
                        "Of course. Here is one short version:\n\n"
                        '  "Thank you so much for bringing my mail in. It meant a lot."\n\n'
                        "I can make it warmer, shorter, or more formal if you would like."
                    ),
                    takeaway=(
                        "A plain question got a plain answer, with an open door to change it."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="u3-retrieval",
                title="Which way of asking works?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits how Claude expects to be asked.",
                ],
                retrieval=RetrievalBlock(
                    prompt="What is the best way to ask Claude for help?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="In plain words, the same way you would ask a friend.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Using a special code or command that only Claude knows.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Claude was made to understand everyday language. No codes or commands are needed."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=2,
        stability_threshold=1.0,
    ),
    # ---- Unit 4: small-steps lesson (max_complexity=3 preserved) -----------
    CurriculumUnit(
        id="unit-4",
        title="Claude-Based Projects",
        description="Create meaningful, practical results with Claude, one step at a time.",
        pages=[
            CurriculumPage(
                id="u4-recap",
                title="What we know so far",
                page_type="recap",
                content=[
                    "You can ask Claude in plain words, and Claude offers something back for you to use, change, or set aside.",
                    "This lesson is about doing something with that — a small project, taken one step at a time.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u4-principle",
                title="One question at a time",
                page_type="principle",
                principle="One question at a time. Each answer is a step you can choose to take.",
                content=[
                    "Asking for everything at once gets a tangled answer.",
                    "Asking one small question at a time gives you a chance to read, think, and decide before the next step.",
                    "There is no rush. The project waits for you.",
                ],
                complexity=2,
            ),
            CurriculumPage(
                id="u4-example",
                title="A note, one step at a time",
                page_type="example",
                content=[
                    "Here is the same small project, broken into steps.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You want to write a short letter to a grandchild. You start by asking Claude: "
                        '"What is a friendly way to begin a letter to my grandchild?"'
                    ),
                    claude_says=(
                        "Here is one warm opening:\n\n"
                        '  "Dear Sam, I have been thinking about you this week, and I wanted to write."\n\n'
                        "When you are ready, you can tell me what you would like to say next."
                    ),
                    takeaway=(
                        "Claude answered one step. The next step waits until you decide what it should be."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="u4-retrieval",
                title="Which way of working is steadier?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from the principle page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="You want to write a letter with Claude. What is the steadier way?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Ask one small question, read the answer, then decide what to ask next.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Ask for the whole letter, the envelope, and the stamp choice all at once.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Small steps keep you in control. Each answer is a moment to pause and decide."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=3,
        stability_threshold=0.8,
    ),
    # ---- Unit 5: verifying / pacing ---------------------------------------
    CurriculumUnit(
        id="unit-5",
        title="Verifying Claude's Suggestions",
        description="Build the habit of checking what Claude says before acting on it.",
        pages=[
            CurriculumPage(
                id="u5-recap",
                title="What we built last lesson",
                page_type="recap",
                content=[
                    "You learned to take a project one small step at a time, with Claude offering each step and you choosing the next.",
                    "This lesson is about the moment right after Claude answers: reading carefully before using anything.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u5-principle",
                title="Read before you use",
                page_type="principle",
                principle="Read what Claude wrote before you use it. There is no rush.",
                content=[
                    "Claude can sound very sure, even when it is wrong.",
                    "Reading the answer first — slowly — is the simplest way to keep mistakes small.",
                    "If something feels off, you can set it aside. Nothing is lost by waiting.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u5-example",
                title="Spotting something that feels off",
                page_type="example",
                content=[
                    "Sometimes a Claude answer almost works, but one piece feels wrong.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You ask Claude when a holiday falls this year. Claude answers confidently, "
                        "but the date is one you do not remember being right."
                    ),
                    claude_says=(
                        "This year, that holiday falls on a Tuesday in the middle of the month."
                    ),
                    takeaway=(
                        "When something feels off, set it aside and check it the way you always have — "
                        "a calendar, a friend, a familiar source. Claude is one voice, not the final word."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="u5-retrieval",
                title="Which response keeps you in control?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from the principle page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Claude gives you an answer that sounds confident. What now?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Read it through. If something feels off, set it aside and check elsewhere.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Use it right away — Claude sounded sure, so it must be right.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Sounding sure is not the same as being right. Reading first keeps the decision yours."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=2,
        stability_threshold=1.0,
    ),
    # ---- Unit 6: judgment & ignoring Claude --------------------------------
    CurriculumUnit(
        id="unit-6",
        title="When to Ignore Claude",
        description="Your judgment matters more than any AI suggestion.",
        pages=[
            CurriculumPage(
                id="u6-recap",
                title="What we practiced last lesson",
                page_type="recap",
                content=[
                    "You practiced reading Claude's answers carefully and setting aside anything that felt off.",
                    "This lesson goes one step further: how to ignore a suggestion entirely, with no regret.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u6-principle",
                title="Your judgment is the final word",
                page_type="principle",
                principle="Claude offers; you decide. Setting Claude aside is always a fine choice.",
                content=[
                    "Claude does not have feelings. Ignoring a suggestion costs nothing.",
                    "If a suggestion does not sound like you, it probably is not for you.",
                    "Your way of saying things has value the AI cannot match.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u6-example",
                title="A suggestion you can let go",
                page_type="example",
                content=[
                    "Here is a small moment of saying no to a suggestion.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You ask Claude to help reply to a friend's email. The draft is fine, but it sounds "
                        "more formal than how you usually write."
                    ),
                    claude_says=(
                        "Dear Margaret,\n\n"
                        "Thank you for your kind correspondence. I trust this message finds you in good health.\n\n"
                        "Warm regards."
                    ),
                    takeaway=(
                        "You can ignore the draft and write it your own way. Saying no to a suggestion "
                        "is part of using Claude well."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="u6-retrieval",
                title="Which choice keeps your voice?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits the rule from the principle page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Claude gives you a draft that does not sound like you. What now?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Set the draft aside and write it the way you would normally.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Use the draft as-is, because Claude wrote it and must know best.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Your way of writing has value Claude cannot copy. Ignoring a draft is a fine choice."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=2,
        stability_threshold=1.0,
    ),
    # ---- Unit 7: recovery from mistakes ------------------------------------
    CurriculumUnit(
        id="unit-7",
        title="Recovering from a Mistake",
        description="Mistakes are part of learning. Practice making them small and easy to undo.",
        pages=[
            CurriculumPage(
                id="u7-recap",
                title="Looking back at the free track",
                page_type="recap",
                content=[
                    "You have learned to ask in plain words, take small steps, read carefully, and ignore what does not fit.",
                    "This last lesson is about what to do when something goes wrong anyway. Spoiler: it is usually a small thing.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u7-principle",
                title="Mistakes are information, not failure",
                page_type="principle",
                principle="A mistake is information. It tells you something to do differently next time.",
                content=[
                    "Everyone makes mistakes when learning something new. That has been true your whole life.",
                    "Most actions with Claude can be undone, walked back, or simply ignored.",
                    "Time is on your side. Nothing here has to be solved in a hurry.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="u7-example",
                title="Undoing a step that did not fit",
                page_type="example",
                content=[
                    "Here is a small mistake, and what undoing it looks like.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You used a Claude suggestion in an email and sent it. Reading it back later, "
                        "the wording does not sound like you. You wish you had changed it first."
                    ),
                    claude_says=(
                        'You can send a short follow-up: "I wanted to add a line in my own words — '
                        'thank you again, and I meant every word."'
                    ),
                    takeaway=(
                        "Even a sent message can be softened by a second one. Most things can be undone, "
                        "or at least gently corrected."
                    ),
                ),
                complexity=2,
            ),
            CurriculumPage(
                id="u7-retrieval",
                title="Which response fits the rule?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches the rule from the principle page.",
                ],
                retrieval=RetrievalBlock(
                    prompt="Something with Claude did not go the way you hoped. What now?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="Take a breath, look at the small thing that went wrong, and try a different step.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Decide you are not cut out for this, and stop.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Mistakes are part of learning anything new. They are small, and you have time."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=2,
        stability_threshold=0.9,
    ),
]


# ===== Bridge units (S25.4 + S25.5) =====================================
# Optional, menu-only side lessons. Held in a SEPARATE list so:
#   - they never appear in /api/curriculum/next-unit's linear walk,
#   - they never appear in /api/curriculum/units (the main catalog),
#   - get_unit() still finds them, so the existing /units/{id}/lesson
#     endpoint serves them with no other changes.
#
# Authoring constraint: keep factual claims minimal and verifiable. These
# lessons describe other companies' products and Anthropic's own product
# surface; over-specific claims age badly.

BRIDGE_UNITS: List[CurriculumUnit] = [
    CurriculumUnit(
        id="bridge-compare",
        title="How Claude compares to other AI helpers",
        description="An optional side lesson if you have heard of ChatGPT or Gemini.",
        pages=[
            CurriculumPage(
                id="bc-context",
                title="Why this side lesson exists",
                page_type="context",
                content=[
                    "This is an optional lesson. Open it if you have heard the names ChatGPT or Gemini and wonder how they relate to Claude.",
                    "It is short. It will not change anything else in the course.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="bc-principle",
                title="Three helpers, the same family",
                page_type="principle",
                principle="Claude, ChatGPT, and Gemini are three AI helpers made by three different companies. They work in similar ways.",
                content=[
                    "Claude is made by Anthropic. ChatGPT is made by OpenAI. Gemini is made by Google.",
                    'They are all what people call "large language model" assistants. They take in your words and produce words in reply.',
                    "What you learn here about Claude — that it is a tool, that you decide, that confident voices are not always right — carries over to the others.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="bc-example",
                title="The same question, three places",
                page_type="example",
                content=[
                    "Here is the same question, asked of all three.",
                ],
                example=ExampleBlock(
                    situation=(
                        'You ask each helper: "Could you give me a short list of '
                        'ideas for a quiet weekend?"'
                    ),
                    claude_says=(
                        "All three would answer with a short list of ideas. The "
                        "lists would not be identical, but they would have the "
                        "same shape: a few suggestions, no pressure, room for you "
                        "to choose."
                    ),
                    takeaway=(
                        "The product names are different. The shape of the help is "
                        "much the same. The same rule applies: you decide what is "
                        "useful."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="bc-retrieval",
                title="Which is true about other AI helpers?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that fits this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="What is true about ChatGPT and Gemini, compared to Claude?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="They are similar tools made by different companies. The same rules of judgment apply.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="They are completely different things, and what you learn about Claude does not apply to them.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "All three are AI helpers in the same family. The names differ, the principles do not."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=0.9,
    ),
    CurriculumUnit(
        id="bridge-where-claude-lives",
        title="Where Claude lives in real life",
        description="A short, practical side lesson about claude.ai and your privacy.",
        pages=[
            CurriculumPage(
                id="bwcl-context",
                title="The practical side",
                page_type="context",
                content=[
                    "This side lesson is about the practical questions: where Claude actually lives, what it costs to start, and who can see your conversations.",
                    "It will not take long.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="bwcl-principle",
                title="A web page, a free start, a private account",
                page_type="principle",
                principle="Claude lives on a web page called claude.ai. There is a free way to begin. Your conversations are tied to your account.",
                content=[
                    "You reach Claude by typing claude.ai into your web browser. There is nothing to install.",
                    "Anthropic, the company that makes Claude, offers a free tier so you can begin without paying.",
                    "When you sign in, your past conversations are saved in your account so you can find them again. They are tied to your sign-in.",
                ],
                complexity=1,
            ),
            CurriculumPage(
                id="bwcl-example",
                title="What signing in for the first time looks like",
                page_type="example",
                content=[
                    "Here is what most people see the first time they visit.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You type claude.ai into your browser. The page shows a "
                        "sign-in box. You can use an email address you already have."
                    ),
                    claude_says=(
                        "Welcome. Once you are signed in, you will see a writing "
                        "box. Type whatever you would like to ask, and I will reply. "
                        "Your past conversations will be saved on the left."
                    ),
                    takeaway=(
                        "There is nothing to download. The page is the whole tool. "
                        "Your account holds your history; it is not shared."
                    ),
                ),
                complexity=1,
            ),
            CurriculumPage(
                id="bwcl-retrieval",
                title="Who can see your saved conversations?",
                page_type="retrieval",
                content=[
                    "Read both. Pick the one that matches the principle from this lesson.",
                ],
                retrieval=RetrievalBlock(
                    prompt="When you are signed in to claude.ai, who sees the conversations you have saved?",
                    choices=[
                        RetrievalChoice(
                            id="a",
                            text="They are tied to your account. They are not shared with other users.",
                        ),
                        RetrievalChoice(
                            id="b",
                            text="Everyone who visits claude.ai can read them.",
                        ),
                    ],
                    correct_id="a",
                    explanation=(
                        "Your conversations belong to your sign-in. Other users do not see them."
                    ),
                ),
                complexity=1,
            ),
        ],
        max_complexity=1,
        stability_threshold=0.9,
    ),
]


def get_unit(unit_id: str) -> Optional[CurriculumUnit]:
    """Lookup helper. Returns None if unit_id is unknown.

    Searches the linear UNITS catalog first, then BRIDGE_UNITS. This
    means /units/{id}/lesson can serve bridge units with no other
    changes, while /next-unit and /units (catalog) still see only the
    linear sequence.
    """
    for u in UNITS:
        if u.id == unit_id:
            return u
    for u in BRIDGE_UNITS:
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
