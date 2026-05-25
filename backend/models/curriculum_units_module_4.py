"""Module 4 curriculum units: building and using Claude Skills.

Distinct from Modules 1-3 (orientation, sustained use, long-term judgment).
Module 4 moves the learner from "using Claude" to "teaching Claude once":
a Claude Skill is a named, reusable, explicitly defined instruction package
that Claude invokes when relevant.

Library-grounded references (closed list, see `docs/library/README.md`):
  - C1 Fisk et al. (2009) — human factors for older adults; concrete-over-abstract.
  - B2 Norman (2013) — mental models; named, predictable roles.
  - D1 Sweller, Ayres & Kalyuga (2011) — cognitive load theory; gradual ramp.
  - P2 IDD-2026 — ISCS stability constraints continue to apply.
  - Claude Skills architecture (Anthropic, 2025-2026) — descriptive technical reference.

See ADR 0017. Content re-authored in Sprint P10 (2026-05-24) to full
Phase-1 lesson parity: four-page structure (recap / principle / example /
retrieval) with concrete scenarios and geragogy compliance.

Note: rendering Module 4 in the UI does not require Anthropic API access;
the content teaches *about* Skills declaratively. Actually creating Skills
end-to-end remains vendor-blocked.
"""

from typing import Optional


from backend.models.curriculum_units import (
    CurriculumPage,
    ExampleBlock,
    RetrievalBlock,
    RetrievalChoice,
    TelemetryGatedUnit,
)


Module4Unit = TelemetryGatedUnit


# ---------------------------------------------------------------------------
# Helper: single-choice retrieval used by every unit in this module
# ---------------------------------------------------------------------------

def _retrieval(
    page_id: str,
    title: str,
    prompt: str,
    correct_text: str,
    incorrect_text: str,
    explanation: str,
    complexity: int = 1,
) -> CurriculumPage:
    return CurriculumPage(
        id=page_id,
        title=title,
        page_type="retrieval",
        content=[
            "Read both. Pick the one that fits the rule from this lesson.",
            "There is no time limit. Either answer is a fine thing to think about.",
        ],
        retrieval=RetrievalBlock(
            prompt=prompt,
            choices=[
                RetrievalChoice(id="a", text=correct_text),
                RetrievalChoice(id="b", text=incorrect_text),
            ],
            correct_id="a",
            explanation=explanation,
        ),
        complexity=complexity,
    )


UNITS_MODULE_4 = [
    # =====================================================================
    # Unit 1: What a Claude Skill Is
    # =====================================================================
    Module4Unit(
        id="module4-unit-1",
        title="What a Claude Skill Is",
        description="Understanding Skills as named, reusable instructions.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m4u1-recap",
                title="Where Module 3 left you",
                page_type="recap",
                content=[
                    "Module 3 ended with a quiet rule. You are the decision-maker. Claude is a tool, and you decide how it fits into your life.",
                    "Module 4 is about making Claude even more useful. You will teach it a trick you can use again and again.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m4u1-principle",
                title="A Skill is a trick you teach once",
                page_type="principle",
                principle="A Claude Skill is a set of instructions you write once. Claude remembers it and uses it whenever the right moment comes.",
                content=[
                    "Think of a Skill like teaching a dog to sit. You show it once, and after that the dog knows what to do.",
                    "A Claude Skill works the same way. You explain what you want. For example, 'Whenever I ask about meals, suggest something simple and warm.'",
                    "After that, Claude knows your preference. It uses it without you having to repeat yourself.",
                    "You can change a Skill anytime. You can stop using it. You are always in charge.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m4u1-example",
                title="A Skill for meal suggestions",
                page_type="example",
                content=[
                    "Here is what creating a Skill looks like.",
                ],
                example=ExampleBlock(
                    situation=(
                        "You often ask Claude to suggest meals. You notice Claude sometimes suggests complicated recipes "
                        "with ingredients you do not keep in the house. You decide to create a Skill called 'Simple Meals.'"
                    ),
                    claude_says=(
                        "You write: 'Whenever I ask for a meal suggestion, recommend something that uses five ingredients or fewer. "
                        "Prefer warm, familiar foods. Avoid fancy techniques.'\n\n"
                        "After that, every time you ask about meals, Claude remembers: simple, warm, familiar."
                    ),
                    takeaway=(
                        "You taught Claude once. Now it knows your preference without you repeating it."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m4u1-retrieval",
                title="Which one is a Skill?",
                prompt="What is a Claude Skill?",
                correct_text="Instructions you write once so Claude remembers them and uses them at the right time.",
                incorrect_text="A secret password that unlocks special features in Claude.",
                explanation="A Skill is reusable instructions. It is not a password or a hidden feature. It is something you create and control.",
            ),
        ],
        max_complexity=2,
        stability_threshold=0.7,
        telemetry_requirements={"mastery_min": 0.6, "volatility_max": 0.45},
    ),
    # =====================================================================
    # Unit 2: When a Skill Is Useful
    # =====================================================================
    Module4Unit(
        id="module4-unit-2",
        title="When a Skill Is Useful",
        description="Learning when a Skill helps more than repeating instructions.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m4u2-recap",
                title="What we learned last lesson",
                page_type="recap",
                content=[
                    "Last lesson, you learned that a Skill is like teaching a trick once. Claude remembers it and uses it at the right time.",
                    "This lesson is about choosing when a Skill is worth creating and when plain asking is enough.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m4u2-principle",
                title="Skills are for things you do often",
                page_type="principle",
                principle="A Skill is worth making when you find yourself asking Claude for the same kind of help more than once.",
                content=[
                    "If you ask Claude something one time, plain asking is fine. There is no need to make a Skill.",
                    "If you ask the same kind of thing every week, a Skill saves you from repeating yourself.",
                    "A good Skill feels like a habit. You use it without thinking much about it.",
                    "You choose which tasks become Skills. A few good ones are better than many you forget.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m4u2-example",
                title="A grocery list and a party plan",
                page_type="example",
                content=[
                    "Here is one person deciding what needs a Skill and what does not.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Maria asks Claude for a grocery list every Friday. She also asked Claude once to help plan her granddaughter's "
                        "birthday party. Maria wonders if either one should become a Skill."
                    ),
                    claude_says=(
                        "For the grocery list, Maria could make a Skill called 'Friday Groceries.' She could write: "
                        "'Suggest a short grocery list with foods I use often. Include one fresh vegetable.'\n\n"
                        "For the birthday party, plain asking was enough. She will not plan another party soon."
                    ),
                    takeaway=(
                        "Things you do often become Skills. Things you do once stay as plain asks."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m4u2-retrieval",
                title="Which one is a good Skill idea?",
                prompt="You have been using Claude for a month. Which task is worth making into a Skill?",
                correct_text="Something you ask Claude to help with every week, like a grocery list.",
                incorrect_text="Something you asked Claude about one time, like a party plan.",
                explanation="Skills are for repeated tasks. Plain asking is fine for things that happen once.",
            ),
        ],
        max_complexity=2,
        stability_threshold=0.68,
        telemetry_requirements={"strain_max": 0.4},
    ),
    # =====================================================================
    # Unit 3: Creating Your First Skill
    # =====================================================================
    Module4Unit(
        id="module4-unit-3",
        title="Creating Your First Skill",
        description="Building a simple Skill with Claude's help, one step at a time.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m4u3-recap",
                title="What we know so far",
                page_type="recap",
                content=[
                    "You know that a Skill is reusable instructions for something you do often. You know that not every task needs a Skill.",
                    "This lesson is about the actual steps of creating one.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m4u3-principle",
                title="You describe it. Claude helps write it.",
                page_type="principle",
                principle="Creating a Skill is a conversation. You explain what you want. Claude drafts the instructions. You review and adjust.",
                content=[
                    "You do not need to write the Skill perfectly. You only need to describe what you want in plain words.",
                    "Claude can turn your description into clear instructions.",
                    "You read what Claude wrote. If something does not sound right, you say so. Claude adjusts it.",
                    "When the instructions feel right, you save the Skill with a name you will remember.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m4u3-example",
                title="Creating a 'Weekly Letter' Skill",
                page_type="example",
                content=[
                    "Here is what creating a Skill looks like, step by step.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Every Sunday, Harold writes a short letter to his sister who lives in another state. "
                        "He asks Claude to help him find the right words. He decides to make a Skill so he does not have to explain himself every week."
                    ),
                    claude_says=(
                        "Harold says to Claude: 'I write a letter to my sister every Sunday. It is usually about my week — "
                        "something I did, something I saw, a question about her life. Could you help me make a Skill for this?'\n\n"
                        "Claude drafts instructions: 'When Harold asks for his Sunday letter, suggest a warm opening, "
                        "one detail from his week, and a gentle question about his sister's life.'\n\n"
                        "Harold reads it. He adds: 'Keep the opening short. My sister likes me to get to the point.' "
                        "Claude adjusts. Harold saves it as 'Sunday Letter.'"
                    ),
                    takeaway=(
                        "Harold described what he wanted. Claude drafted it. Harold reviewed and adjusted. The Skill is his."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m4u3-retrieval",
                title="Who writes the Skill instructions?",
                prompt="You want to create a Skill. Who does most of the writing?",
                correct_text="Claude drafts the instructions from your description. You review and adjust them.",
                incorrect_text="You must write every instruction yourself, exactly right, before Claude can use it.",
                explanation="You describe what you want in plain words. Claude turns that into instructions. You stay in control by reviewing.",
            ),
        ],
        max_complexity=3,
        stability_threshold=0.66,
        telemetry_requirements={"mastery_min": 0.65},
    ),
    # =====================================================================
    # Unit 4: Naming and Describing a Skill
    # =====================================================================
    Module4Unit(
        id="module4-unit-4",
        title="Naming and Describing a Skill",
        description="Making Skills clear, readable, and trustworthy.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m4u4-recap",
                title="Where we were",
                page_type="recap",
                content=[
                    "You learned to create a Skill by describing what you want. Claude drafts the instructions. You review and adjust.",
                    "This lesson is about giving the Skill a name and description that make it easy to find and use.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m4u4-principle",
                title="A good name explains what the Skill does",
                page_type="principle",
                principle="A Skill name should tell you what the Skill does in a few plain words. The description should explain when to use it.",
                content=[
                    "A vague name like 'My Thing' does not help. You will forget what it does.",
                    "A clear name like 'Simple Meal Suggestions' tells you exactly what to expect.",
                    "The description is the sentence you read before using the Skill. It should say when the Skill is helpful.",
                    "Clear names and descriptions build trust. You know what the Skill will do before you ask.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m4u4-example",
                title="From vague to clear",
                page_type="example",
                content=[
                    "Here is someone improving a Skill name so they can find it later.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Elena created a Skill for her garden planning. She named it 'Garden Stuff' and left the description blank. "
                        "A month later, she had five Skills and could not remember which was which."
                    ),
                    claude_says=(
                        "Elena renames the Skill 'Garden Task List.' She writes the description: "
                        "'When I ask about my garden, suggest one small task for this week based on the season.'\n\n"
                        "Now when Elena sees her list of Skills, she knows exactly what each one does."
                    ),
                    takeaway=(
                        "A clear name and description are a gift to your future self. You will thank yourself later."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m4u4-retrieval",
                title="Which name is clearer?",
                prompt="You have a Skill that suggests warm, short letters to family. Which name is better?",
                correct_text="'Family Letter Helper' with the description 'Suggests a warm, short letter to a family member.'",
                incorrect_text="'Letter Thing' with no description.",
                explanation="A clear name and description help you remember what the Skill does and when to use it.",
            ),
        ],
        max_complexity=3,
        stability_threshold=0.64,
        telemetry_requirements={"volatility_max": 0.4},
    ),
    # =====================================================================
    # Unit 5: Testing and Refining a Skill
    # =====================================================================
    Module4Unit(
        id="module4-unit-5",
        title="Testing and Refining a Skill",
        description="Checking that a Skill behaves the way you expect, and adjusting it.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m4u5-recap",
                title="What we built last lesson",
                page_type="recap",
                content=[
                    "You learned that a good Skill has a clear name and description. That makes it easy to find and understand.",
                    "This lesson is about trying the Skill and improving it based on what you notice.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m4u5-principle",
                title="Try it, notice, adjust",
                page_type="principle",
                principle="A new Skill is a first draft. You try it, notice what works and what does not, and adjust the instructions.",
                content=[
                    "The first version of a Skill is rarely perfect. That is normal and expected.",
                    "Use the Skill a few times. Pay attention to what Claude says.",
                    "If the answers are too long, you can ask for shorter ones. If they miss the point, explain what you meant.",
                    "Adjusting a Skill is not failure. It is part of making something useful.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m4u5-example",
                title="A gift idea Skill that needed work",
                page_type="example",
                content=[
                    "Here is someone noticing that their Skill needs adjustment.",
                ],
                example=ExampleBlock(
                    situation=(
                        "James created a Skill called 'Gift Ideas.' He wrote: 'Suggest a gift for a family member.' "
                        "He tried it for his wife's birthday. Claude suggested a tablet. James knew his wife prefers books."
                    ),
                    claude_says=(
                        "James adjusts the Skill. He adds: 'Prefer practical gifts. Avoid electronics unless the person specifically likes them.'\n\n"
                        "The next time he uses the Skill for his grandson, Claude suggests a gardening kit. "
                        "That is much closer to what James had in mind."
                    ),
                    takeaway=(
                        "The first version taught James what was missing. The second version worked better because he paid attention."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m4u5-retrieval",
                title="What do you do when a Skill is not quite right?",
                prompt="You try a new Skill and the answer feels off. What now?",
                correct_text="Notice what felt wrong, adjust the Skill instructions, and try again.",
                incorrect_text="Decide the Skill does not work and delete it forever.",
                explanation="Adjusting a Skill is normal. The first version is a draft. You improve it by noticing and changing.",
            ),
        ],
        max_complexity=3,
        stability_threshold=0.62,
        telemetry_requirements={"strain_max": 0.35},
    ),
    # =====================================================================
    # Unit 6: Trusting a Skill Over Time
    # =====================================================================
    Module4Unit(
        id="module4-unit-6",
        title="Trusting a Skill Over Time",
        description="Using Skills confidently while staying in control.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m4u6-recap",
                title="Looking back at Module 4",
                page_type="recap",
                content=[
                    "You learned what a Skill is, when to make one, how to create it, how to name it, and how to improve it.",
                    "This last lesson is about living with a Skill over time: trusting it, reviewing it, and staying in charge.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m4u6-principle",
                title="A Skill is a helper, not a replacement",
                page_type="principle",
                principle="A Skill supports your thinking. It does not replace your judgment. You decide when to use it, change it, or stop using it.",
                content=[
                    "A Skill you created is yours. It works for you, not the other way around.",
                    "Over time, your needs may change. A Skill that was helpful last year may need updating this year.",
                    "You can review your Skills whenever you like. You can change them. You can stop using them.",
                    "Trusting a Skill does not mean handing over control. It means the Skill has earned your confidence.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m4u6-example",
                title="A Skill that needed a seasonal update",
                page_type="example",
                content=[
                    "Here is someone reviewing a Skill that has been helpful but now needs a small change.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Dorothy created a Skill called 'Weekend Outing Ideas' last spring. It suggested walks, garden visits, and outdoor markets. "
                        "Now it is winter. The suggestions still mention outdoor events even when the weather is cold."
                    ),
                    claude_says=(
                        "Dorothy opens her Skill and adds: 'In cold weather, suggest indoor activities like museums, craft fairs, or cozy cafes.'\n\n"
                        "The Skill now adapts to the season. Dorothy kept what worked and added what was missing."
                    ),
                    takeaway=(
                        "A Skill is not permanent. It grows with you. Reviewing it from time to time keeps it useful."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m4u6-retrieval",
                title="Who stays in charge of a Skill?",
                prompt="You have been using a Skill for six months. Who decides if it still fits your life?",
                correct_text="You do. You can review, change, or stop using the Skill anytime.",
                incorrect_text="The Skill decides for itself when it is no longer useful.",
                explanation="A Skill is a tool you created and control. It does not make decisions about itself. You do.",
            ),
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
