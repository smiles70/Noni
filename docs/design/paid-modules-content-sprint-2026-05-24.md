# Paid Modules Content Sprint (P10): M4-M5 Curriculum Authoring

**Date:** 2026-05-24
**Status:** Sprint plan — ready for approval
**Scope:** Full content rewrite of M4 (Skills) and M5 (Agents) to achieve parity with M1-M3
**Source material assessed:** Anthropic Skilljar (https://anthropic.skilljar.com/)

---

## 1. Source Material Assessment: Anthropic Skilljar

### 1.1 Courses Reviewed

| Course | URL | Relevance to Noni | Adaptability |
|---|---|---|---|
| **Introduction to agent skills** | /introduction-to-agent-skills | **Direct M4 map** — covers Skills creation, configuration, sharing, troubleshooting | Moderate — structure is sound, content is too technical |
| **Introduction to subagents** | /introduction-to-subagents | **Direct M5 map** — covers subagent creation, design, delegation | Moderate — concepts align, examples are developer-only |
| **Introduction to Claude Cowork** | /introduction-to-claude-cowork | **Supplementary** — broader Skills/Plugins/Workflows context | Low — too broad, enterprise-focused |
| **Claude 101** | /claude-101 | **Supplementary** — foundational Claude concepts | Low — overlaps with M1-M2 |
| **AI Fluency: Framework & Foundations** | /ai-fluency-framework-foundations | **Pedagogical reference** — AI collaboration framework | Low — abstract, not concrete |

### 1.2 What Can Be Adapted from Skilljar

#### ✅ Adaptable (with significant rewriting)

1. **Conceptual structure:** The curriculum organization is pedagogically sound:
   - Skills: What → Create → Configure → Compare → Share → Troubleshoot
   - Subagents: What → Create → Design → Use Effectively
   - This maps well to our recap → principle → example → retrieval flow.

2. **Core concepts:** The fundamental ideas are technically correct and transferable:
   - Skills = reusable instructions that Claude applies automatically
   - Subagents = delegated tasks with isolated context and clean return
   - Progressive disclosure = organizing complexity so it arrives gradually

3. **Error patterns and edge cases:** The troubleshooting content covers real issues (skills that won't trigger, priority conflicts) that can be reframed as judgment exercises.

4. **Value proposition framing:** The "About this course" sections contain clear explanations of *why* Skills/Subagents matter — useful for our principle pages.

#### ❌ Not Adaptable (requires original authoring)

1. **Technical implementation details:**
   - CLI commands (`/agents`, terminal access)
   - Markdown syntax (`SKILL.md` frontmatter)
   - Repository commits, enterprise managed settings
   - Tool restrictions (`allowed-tools`)
   - **Why:** Our audience uses Claude via web browser, not CLI. Technical details are irrelevant and intimidating.

2. **Developer-focused examples:**
   - Code review, documentation generation
   - File system access, repository management
   - "Context window efficiency"
   - **Why:** Not relatable to everyday life of older adults.

3. **Tone and register:**
   - Skilljar: "spin up a separate context window", "wire Skills into custom subagents"
   - Noni: "Claude can learn a trick you teach it once"
   - **Why:** Geragogy contract requires plain words, short sentences, no jargon.

4. **Concrete scenarios for our audience:**
   - Skilljar has none for older adults.
   - Noni needs: grocery lists, letters to grandchildren, medical appointment prep, hobby research.
   - **Why:** Concrete-over-abstract is a geragogy requirement (Fisk et al. 2009, C1).

### 1.3 Adaptation Strategy

| Skilljar Element | Noni Equivalent | Effort |
|---|---|---|
| "SKILL.md frontmatter" | "Giving your Skill a name and purpose" | Rewrite |
| "context window efficiency" | "Keeping instructions short so Claude remembers" | Rewrite |
| "allowed-tools restrictions" | "Deciding what Claude is allowed to do with your Skill" | Rewrite |
| "repository commits" | "Saving your Skill where you can find it" | Rewrite |
| "/agents command" | "Asking Claude to handle a task in its own space" | Rewrite |
| "structured output formats" | "Telling Claude how you want the answer to look" | Rewrite |
| "obstacle reporting" | "What to do when Claude gets stuck" | Rewrite |
| Code review example | Letter-writing helper example | Replace |
| Documentation generation | Recipe organizer example | Replace |

---

## 2. Sprint Plan: P10 Content Expansion

### 2.1 Sprint Goal

Rewrite all 11 paid units (M4: 6 units, M5: 5 units) as full 4-page lessons (recap → principle → example → retrieval) with concrete scenarios, actionable guidance, and geragogy-compliant language.

### 2.2 Sprint Structure

**Duration:** 3 sprints (content authoring is the bottleneck)
**Team:** 1 content author + reviewer (can be AI-assisted)
**Output:** 44 curriculum pages (11 units × 4 pages), 11 retrieval quizzes

### 2.3 Work Breakdown

#### Sprint 10-A: Module 4 Foundation (Units 1-3)

| Task | Unit | Description | Acceptance |
|---|---|---|---|
| P10-A.1 | M4-U1 | "What a Claude Skill Is" — 4-page rewrite with concrete analogy (teaching a dog a trick) | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-A.2 | M4-U2 | "When a Skill Is Useful" — scenarios where Skills help vs. where plain asking is enough | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-A.3 | M4-U3 | "Creating Your First Skill" — step-by-step walkthrough using Claude's web interface | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |

#### Sprint 10-B: Module 4 Completion (Units 4-6)

| Task | Unit | Description | Acceptance |
|---|---|---|---|
| P10-B.1 | M4-U4 | "Naming and Describing a Skill" — how to write clear instructions Claude can follow | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-B.2 | M4-U5 | "Testing and Refining a Skill" — trying the Skill, noticing what works, adjusting | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-B.3 | M4-U6 | "Trusting a Skill Over Time" — when to keep using a Skill, when to stop or change it | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |

#### Sprint 10-C: Module 5 Full (Units 1-5)

| Task | Unit | Description | Acceptance |
|---|---|---|---|
| P10-C.1 | M5-U1 | "What an Agent Is (Built from Skills)" — analogy: Skill = one trick, Agent = a helper who knows several tricks | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-C.2 | M5-U2 | "Designing an Agent's Job" — deciding what the Agent should do and what it should not do | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-C.3 | M5-U3 | "Building an Agent Step by Step" — combining Skills into a named helper, one piece at a time | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-C.4 | M5-U4 | "Using an Agent Safely" — reviewing the Agent's work, pausing, staying in charge | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |
| P10-C.5 | M5-U5 | "Staying the Authority" — consolidation: you decide when and how Agents are used | 4 pages, 1 ExampleBlock, 1 RetrievalBlock |

### 2.4 Content Standards (Per-Page Checklist)

Every page must pass:

- [ ] **Geragogy tone:** Calm, plain, dignified. No urgency. No jargon.
- [ ] **Short sentences:** Average ≤10 words per sentence.
- [ ] **Concrete over abstract:** Every principle page must be paired with a concrete example.
- [ ] **Learner-addressing:** Uses "you" throughout.
- [ ] **Confidence-preserving:** No blame, no failure framing. Mistakes are information.
- [ ] **Human authority:** Every example reinforces that the learner decides.
- [ ] **Reversibility:** Every action shown can be undone or adjusted.
- [ ] **Complexity match:** Page complexity ≤ unit max_complexity.

### 2.5 ExampleBlock Requirements

Every ExampleBlock must contain:
- **situation:** A relatable everyday scenario (not technical, not work-related unless the learner's hobby)
- **claude_says:** Realistic, calm, helpful response
- **takeaway:** One-sentence reinforcement of the principle

**Allowed scenario domains:**
- Letter/email writing to family
- Recipe organization and meal planning
- Hobby research (gardening, genealogy, crafts)
- Medical appointment preparation
- Travel planning
- Gift shopping
- Home maintenance schedules
- Memory aids and reminders

**Forbidden scenario domains:**
- Software development
- Code review
- Terminal/CLI usage
- Repository management
- API integration
- Enterprise workflows

### 2.6 RetrievalBlock Requirements

Every RetrievalBlock must contain:
- **prompt:** One clear question about the unit's principle
- **choices:** Exactly 2 options (binary decision — geragogy-compliant)
- **correct_id:** The answer that preserves learner agency and judgment
- **explanation:** One sentence explaining why the correct answer is right

**Pattern:** The correct answer always reinforces that the learner decides. The incorrect answer always shows over-reliance on Claude or surrendering judgment.

---

## 3. Sample Unit Rewrite: M4-U1 "What a Claude Skill Is"

### Current (D+ grade — single page)

```python
CurriculumPage(
    id="module4-unit-1-page-1",
    title="What a Claude Skill Is",
    content=[
        "A Claude Skill is something you teach once.",
        "It has a name and a clear purpose.",
        "Claude uses it when it knows it will help.",
    ],
    complexity=1,
)
```

### Proposed (A grade — 4 pages)

```python
# ---- Page 1: Recap ----
CurriculumPage(
    id="m4u1-recap",
    title="Where Module 3 left you",
    page_type="recap",
    content=[
        "Module 3 ended with a quiet rule: you are the decision-maker. Claude is a tool, and you decide how it fits into your life.",
        "Module 4 is about making Claude even more useful — by teaching it a trick you can use again and again.",
    ],
    complexity=1,
)

# ---- Page 2: Principle ----
CurriculumPage(
    id="m4u1-principle",
    title="A Skill is a trick you teach once",
    page_type="principle",
    principle="A Claude Skill is a set of instructions you write once. Claude remembers it and uses it whenever the right moment comes.",
    content=[
        "Think of a Skill like teaching a dog to sit. You show it once, and after that the dog knows what to do.",
        "A Claude Skill works the same way. You explain what you want — for example, 'Whenever I ask about meals, suggest something simple and warm.'",
        "After that, Claude knows your preference and uses it without you having to repeat yourself.",
        "You can change a Skill anytime. You can stop using it. You are always in charge.",
    ],
    complexity=1,
)

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
)

# ---- Page 4: Retrieval ----
CurriculumPage(
    id="m4u1-retrieval",
    title="Which one is a Skill?",
    page_type="retrieval",
    content=[
        "Read both. Pick the one that matches what a Skill does.",
    ],
    retrieval=RetrievalBlock(
        prompt="What is a Claude Skill?",
        choices=[
            RetrievalChoice(
                id="a",
                text="Instructions you write once so Claude remembers them and uses them at the right time.",
            ),
            RetrievalChoice(
                id="b",
                text="A secret password that unlocks special features in Claude.",
            ),
        ],
        correct_id="a",
        explanation=(
            "A Skill is reusable instructions. It is not a password or a hidden feature. It is something you create and control."
        ),
    ),
    complexity=1,
)
```

---

## 4. Complexity Ramping Plan

| Unit | max_complexity | Rationale |
|---|---|---|
| M4-U1 | 2 | Introduction — keep it simple |
| M4-U2 | 2 | When to use Skills — still introductory |
| M4-U3 | 3 | Creating a Skill — first hands-on, slightly more complex |
| M4-U4 | 3 | Naming and describing — requires more judgment |
| M4-U5 | 3 | Testing and refining — iterative thinking |
| M4-U6 | 3 | Trust over time — synthesis of M4 |
| M5-U1 | 2 | Introduction to Agents — new concept, keep simple |
| M5-U2 | 3 | Designing an Agent's job — requires planning |
| M5-U3 | 4 | Building step by step — most complex unit |
| M5-U4 | 4 | Using safely — oversight and judgment |
| M5-U5 | 3 | Staying the Authority — consolidation, reduce complexity |

---

## 5. Dependency Chain

```
P10-A (M4-U1..U3) ──► P10-B (M4-U4..U6) ──► P10-C (M5-U1..U5)
     │                    │                    │
     └─ Requires ────────┘                    │
          M4 concepts before M5               │
                                               │
          └─ Requires ─────────────────────────┘
               M4 complete before M5 starts
```

M5 depends on M4 because Agents are "built from Skills." The learner must understand Skills before composition.

---

## 6. Test Updates Required

| Test File | Change |
|---|---|
| `test_curriculum_module_4.py` | Update `EXPECTED_IDS` page counts; add content-depth checks |
| `test_curriculum_module_5.py` | Update `EXPECTED_IDS` page counts; expand human-authority markers |
| `test_paid_lesson_endpoint.py` | Update expected page counts in shape parity checks |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Content authoring takes longer than 3 sprints | Medium | High | Start with P10-A; ship M4 first, M5 second |
| Examples feel condescending to some learners | Low | Medium | Review group test with 2-3 target-age users |
| Skill/Agent features change before content ships | Low | Medium | Content is declarative; adapts to any interface |
| Paid bundle already live when content is thin | High | Critical | **Do not promote until P10 complete** — gate in code |

---

## 8. Approval Checklist

Before this sprint begins:

- [ ] Stakeholder approves scenario domains (gardening, letters, recipes, etc.)
- [ ] Stakeholder approves the "dog trick" analogy for Skills (or suggests alternative)
- [ ] Stakeholder confirms: do not promote paid bundle until P10 complete
- [ ] Content author assigned (AI or human)
- [ ] Reviewer assigned (human — geragogy compliance check)

---

## 9. Reference: Skilljar Material Map

```
Skilljar "Introduction to agent skills" ──► Noni Module 4
├── What are skills?               ──► M4-U1: What a Claude Skill Is
├── Creating your first skill      ──► M4-U3: Creating Your First Skill
├── Configuration and multi-file   ──► M4-U4: Naming and Describing a Skill
├── Skills vs. other features      ──► M4-U2: When a Skill Is Useful
├── Sharing skills                 ──► M4-U5: Testing and Refining a Skill (partial)
└── Troubleshooting skills         ──► M4-U6: Trusting a Skill Over Time (partial)

Skilljar "Introduction to subagents" ──► Noni Module 5
├── What are subagents?            ──► M5-U1: What an Agent Is (Built from Skills)
├── Creating a subagent            ──► M5-U3: Building an Agent Step by Step
├── Designing effective subagents  ──► M5-U2: Designing an Agent's Job
└── Using subagents effectively    ──► M5-U4: Using an Agent Safely + M5-U5: Staying the Authority
```
