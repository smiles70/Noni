"""Module 5 curriculum units: composing Agents from Claude Skills.

Distinct from Modules 1-4 (orientation, sustained use, long-term judgment,
building Skills). Module 5 advances the learner from "teaching Claude one
Skill at a time" to "composing multiple Skills into a named, scoped Agent
workflow that remains under explicit human authority at every step."

Library-grounded references (closed list, see `docs/library/README.md`):
  - C1 Fisk et al. (2009) — human factors for older adults; human-in-control
        framing for agent oversight.
  - C3 Knowles et al. (2019) — HCI and aging beyond accessibility; learner
        autonomy and judgment preservation.
  - B2 Norman (2013) — mental models; agents as named, predictable roles.
  - D1 Sweller, Ayres & Kalyuga (2011) — cognitive load theory; depth via
        composition without raising intrinsic load.
  - P2 IDD-2026 — ISCS stability constraints continue to apply.
  - Claude Agent Skills architecture (Anthropic, 2025-2026) — descriptive
        technical reference for what an Agent is in this vendor context.

See ADR 0020. Content re-authored in Sprint P10 (2026-05-24) to full
Phase-1 lesson parity: four-page structure (recap / principle / example /
retrieval) with concrete scenarios and geragogy compliance.

Note: rendering Module 5 in the UI does not require Anthropic API access;
the content teaches *about* Agents declaratively. Actually composing and
running Agents end-to-end remains vendor-blocked (auth + API integration).
"""

from typing import Optional

from backend.models.curriculum_units import (
    CurriculumPage,
    ExampleBlock,
    RetrievalBlock,
    RetrievalChoice,
    TelemetryGatedUnit,
)

Module5Unit = TelemetryGatedUnit


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


UNITS_MODULE_5 = [
    # =====================================================================
    # Unit 1: What an Agent Is (Built from Skills)
    # =====================================================================
    Module5Unit(
        id="module5-unit-1",
        title="What an Agent Is (Built from Skills)",
        description="Understanding agents as structured helpers made from Skills.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m5u1-recap",
                title="Where Module 4 left you",
                page_type="recap",
                content=[
                    "Module 4 taught you about Skills. A Skill is a set of instructions you teach once. Claude remembers it and uses it at the right time.",
                    "Module 5 is about putting several Skills together to make something bigger: an Agent.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m5u1-principle",
                title="An Agent is a helper with several tricks",
                page_type="principle",
                principle="An Agent is a named helper built from one or more Skills. Each Skill is a trick the Agent knows. Together, they handle a bigger job.",
                content=[
                    "Think of a Skill as one trick. An Agent is a helper that knows several tricks and uses them together.",
                    "For example, you might have three Skills: one for meal ideas, one for grocery lists, and one for weekend plans.",
                    "An Agent called 'Weekend Planner' could use all three. It plans your meals, makes your grocery list, and suggests an outing.",
                    "You created the Skills. You created the Agent. You decide when to use it.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m5u1-example",
                title="A 'Weekend Planner' Agent",
                page_type="example",
                content=[
                    "Here is what an Agent looks like when it is made from Skills you already have.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Robert has three Skills he uses often. 'Simple Meals' suggests warm dinners. 'Friday Groceries' makes a short list. "
                        "'Weekend Outing' suggests one local event. Robert decides to combine them into a single helper."
                    ),
                    claude_says=(
                        "Robert creates an Agent called 'Weekend Planner.' He tells Claude: "
                        "'Use my Simple Meals Skill for Saturday dinner. Use my Friday Groceries Skill for the shopping list. "
                        "Use my Weekend Outing Skill for one activity on Sunday.'\n\n"
                        "Now when Robert says 'Plan my weekend,' the Agent uses all three Skills together."
                    ),
                    takeaway=(
                        "An Agent is just a way to bundle Skills. You already made the pieces. The Agent puts them together."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m5u1-retrieval",
                title="What is an Agent made of?",
                prompt="What is a Claude Agent?",
                correct_text="A named helper built from one or more Skills that work together.",
                incorrect_text="A separate person inside Claude who makes decisions for you.",
                explanation="An Agent is a bundle of Skills you created. It is not a separate person. It does not decide for you.",
            ),
        ],
        max_complexity=2,
        stability_threshold=0.65,
        telemetry_requirements={"mastery_min": 0.7, "volatility_max": 0.4},
    ),
    # =====================================================================
    # Unit 2: Designing an Agent's Job
    # =====================================================================
    Module5Unit(
        id="module5-unit-2",
        title="Designing an Agent's Job",
        description="Defining what an Agent should do — and what it should not do.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m5u2-recap",
                title="What we learned last lesson",
                page_type="recap",
                content=[
                    "Last lesson, you learned that an Agent is a helper built from Skills. It bundles several tricks into one named helper.",
                    "This lesson is about designing the Agent's job carefully: what it does, and just as important, what it does not do.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m5u2-principle",
                title="A good Agent has clear boundaries",
                page_type="principle",
                principle="Every Agent needs a clear job description. You decide what it handles and what it leaves alone. Good boundaries keep Agents safe and useful.",
                content=[
                    "An Agent without boundaries might try to do too much. That leads to confusion and mistakes.",
                    "Start with one clear job. For example, 'Help me plan my weekend.' Not 'Manage my whole life.'",
                    "Write down what the Agent should not do. For example, 'Do not suggest anything that costs money. Do not make appointments.'",
                    "Clear boundaries make the Agent predictable. You know what to expect. That builds trust.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m5u2-example",
                title="A 'Medication Reminder' Agent with strict boundaries",
                page_type="example",
                content=[
                    "Here is someone designing an Agent with very clear limits.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Margaret takes medication every morning. She wants an Agent to help her remember, but she is careful about what it should and should not do."
                    ),
                    claude_says=(
                        "Margaret designs her Agent like this:\n\n"
                        "'Your job is to remind me about my morning medication. You do not decide what medication I take. "
                        "You do not suggest changes to my schedule. You simply remind me at the time I choose.'\n\n"
                        "The Agent's job is small and specific. It reminds. It does not advise. It does not decide."
                    ),
                    takeaway=(
                        "Small, specific jobs with clear boundaries make Agents trustworthy. You know exactly what they will and will not do."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m5u2-retrieval",
                title="Which Agent is designed more safely?",
                prompt="You want an Agent to help with your daily routine. Which design is safer?",
                correct_text="An Agent with a small, specific job and clear rules about what it should not do.",
                incorrect_text="An Agent with a big, vague job like 'Help me with everything in my life.'",
                explanation="Small jobs with clear boundaries are safer. Big, vague jobs lead to confusion and overreach.",
            ),
        ],
        max_complexity=3,
        stability_threshold=0.63,
        telemetry_requirements={"mastery_min": 0.7},
    ),
    # =====================================================================
    # Unit 3: Building an Agent Step by Step
    # =====================================================================
    Module5Unit(
        id="module5-unit-3",
        title="Building an Agent Step by Step",
        description="Creating an Agent by combining Skills one piece at a time.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m5u3-recap",
                title="What we know so far",
                page_type="recap",
                content=[
                    "You know that an Agent is built from Skills. You know that a good Agent has clear boundaries.",
                    "This lesson is about the actual steps of building one: adding Skills one at a time and testing each piece.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m5u3-principle",
                title="Build one piece at a time",
                page_type="principle",
                principle="An Agent is built gradually. You add one Skill, test it, then add the next. Each step is small and reversible.",
                content=[
                    "Do not try to build the whole Agent at once. That is too much to keep track of.",
                    "Start with the most important Skill. Test it. Make sure it works the way you expect.",
                    "Then add the next Skill. Test again. If something feels off, fix it before adding more.",
                    "Building slowly keeps you in control. You see what works before you add more complexity.",
                ],
                complexity=2,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m5u3-example",
                title="Building a 'Family Event Planner' Agent",
                page_type="example",
                content=[
                    "Here is someone building an Agent one Skill at a time.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Patricia wants an Agent to help plan family gatherings. She has three Skills: 'Guest List,' 'Menu Ideas,' and 'Activity Suggestions.' "
                        "She decides to add them one at a time instead of all at once."
                    ),
                    claude_says=(
                        "Step one: Patricia adds only the 'Guest List' Skill. She tests it by asking: 'Who should I invite to Sunday dinner?' "
                        "Claude uses the Skill and suggests names. It works well.\n\n"
                        "Step two: She adds the 'Menu Ideas' Skill. She tests: 'What should I cook?' Claude suggests simple meals. "
                        "One suggestion has nuts. Patricia's grandson is allergic. She adjusts the Skill to say 'Avoid nuts.'\n\n"
                        "Step three: She adds 'Activity Suggestions.' She tests the whole Agent together. It works. She saves it as 'Family Event Planner.'"
                    ),
                    takeaway=(
                        "Each step was small and tested. A problem was caught early and fixed. The final Agent is trustworthy because it was built carefully."
                    ),
                ),
                complexity=3,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m5u3-retrieval",
                title="How do you build an Agent safely?",
                prompt="You want to build an Agent from several Skills. What is the safest way?",
                correct_text="Add one Skill at a time, test it, fix any issues, then add the next.",
                incorrect_text="Add all the Skills at once and hope everything works together.",
                explanation="Adding Skills one at a time lets you catch problems early. Building everything at once makes mistakes harder to find.",
            ),
        ],
        max_complexity=4,
        stability_threshold=0.6,
        telemetry_requirements={"strain_max": 0.35},
    ),
    # =====================================================================
    # Unit 4: Using an Agent Safely
    # =====================================================================
    Module5Unit(
        id="module5-unit-4",
        title="Using an Agent Safely",
        description="Working with Agents while staying in control.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m5u4-recap",
                title="What we built last lesson",
                page_type="recap",
                content=[
                    "You learned to build an Agent one Skill at a time. Each piece was tested before the next was added.",
                    "This lesson is about using the Agent safely: reviewing its work, pausing when needed, and staying in charge.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m5u4-principle",
                title="Review before you use",
                page_type="principle",
                principle="An Agent's suggestions are starting points, not final answers. You review them. You decide what to use, change, or set aside.",
                content=[
                    "An Agent can combine many Skills at once. That means its answers can be longer or more detailed than a single Skill.",
                    "Read the whole answer slowly. Check each part against what you expected.",
                    "If something feels wrong, pause. You can ask the Agent to explain. You can adjust a Skill. You can stop.",
                    "The Agent works for you. You do not work for the Agent.",
                ],
                complexity=2,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m5u4-example",
                title="Reviewing a weekend plan",
                page_type="example",
                content=[
                    "Here is someone reviewing an Agent's suggestions before using them.",
                ],
                example=ExampleBlock(
                    situation=(
                        "George asks his 'Weekend Planner' Agent for a plan. The Agent suggests a Saturday dinner recipe, a grocery list, and a Sunday museum visit."
                    ),
                    claude_says=(
                        "George reads the dinner recipe. It includes shrimp. His wife does not eat seafood. He asks the Agent: "
                        "'Change the Saturday dinner to something without seafood.'\n\n"
                        "The Agent adjusts. George reviews the new suggestion. It is a chicken dish. That works.\n\n"
                        "George also notices the museum is an hour away. He prefers to stay closer to home. He asks for a nearer option. The Agent suggests a local garden tour."
                    ),
                    takeaway=(
                        "George reviewed every part. He changed what did not fit. The final plan was his, not the Agent's."
                    ),
                ),
                complexity=3,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m5u4-retrieval",
                title="Who is responsible for an Agent's suggestions?",
                prompt="Your Agent suggests a plan. One part does not feel right. What do you do?",
                correct_text="You ask the Agent to change that part, or you adjust it yourself.",
                incorrect_text="You accept the whole plan because the Agent created it and must know best.",
                explanation="You are responsible for what you use. The Agent suggests. You review and decide. That is how it stays safe.",
            ),
        ],
        max_complexity=4,
        stability_threshold=0.58,
        telemetry_requirements={"volatility_max": 0.35},
    ),
    # =====================================================================
    # Unit 5: Staying the Authority
    # =====================================================================
    Module5Unit(
        id="module5-unit-5",
        title="Staying the Authority",
        description="Reinforcing dignity, judgment, and control when using Agents.",
        pages=[
            # ---- Page 1: Recap ----
            CurriculumPage(
                id="m5u5-recap",
                title="Looking back at Module 5",
                page_type="recap",
                content=[
                    "You learned what an Agent is, how to design its job, how to build it step by step, and how to use it safely.",
                    "This last lesson is about the most important rule of all: you are the authority. The Agent exists to support your thinking, not replace it.",
                ],
                complexity=1,
            ),
            # ---- Page 2: Principle ----
            CurriculumPage(
                id="m5u5-principle",
                title="Your judgment is the final word",
                page_type="principle",
                principle="Agents are powerful tools. But they are still tools. You decide when to use them, how to use them, and when to set them aside.",
                content=[
                    "An Agent can handle many tasks at once. That is convenient. It can also feel like the Agent is in charge.",
                    "It is not. You are. You can say no to any suggestion. You can stop using an Agent anytime. You can delete it.",
                    "Your life experience is something no Agent can copy. Your judgment has value that no Skill can replace.",
                    "The best use of an Agent is as a partner, not a replacement. It helps. You decide.",
                ],
                complexity=1,
            ),
            # ---- Page 3: Example ----
            CurriculumPage(
                id="m5u5-example",
                title="Choosing not to use the Agent",
                page_type="example",
                content=[
                    "Here is someone deciding that an Agent is not the right tool for a particular moment.",
                ],
                example=ExampleBlock(
                    situation=(
                        "Ruth has a 'Family Event Planner' Agent she usually likes. Her daughter calls with upsetting news. "
                        "Ruth considers asking the Agent to plan a comforting dinner, but something feels wrong about using a tool for this moment."
                    ),
                    claude_says=(
                        "Ruth decides not to use the Agent this time. She calls her sister instead. They talk for an hour. "
                        "Later, when things feel calmer, Ruth uses the Agent to plan a simple family gathering.\n\n"
                        "The Agent was not wrong. Ruth just knew that this moment needed a human connection, not a plan."
                    ),
                    takeaway=(
                        "Knowing when not to use an Agent is as important as knowing how to use it. Your judgment knows the difference."
                    ),
                ),
                complexity=2,
            ),
            # ---- Page 4: Retrieval ----
            _retrieval(
                page_id="m5u5-retrieval",
                title="Who has the final say?",
                prompt="Your Agent gives you a suggestion. You are not sure it is right. What now?",
                correct_text="You trust your own judgment. You can change, ignore, or stop using the suggestion.",
                incorrect_text="You follow the Agent's suggestion because it handles more information than you do.",
                explanation="Your judgment is the final word. The Agent handles information. You handle decisions. That is how it should be.",
            ),
        ],
        max_complexity=3,
        stability_threshold=0.55,
        telemetry_requirements={"mastery_min": 0.75, "volatility_max": 0.3},
    ),
]


def get_module_5_unit(unit_id: str) -> Optional[Module5Unit]:
    for u in UNITS_MODULE_5:
        if u.id == unit_id:
            return u
    return None
