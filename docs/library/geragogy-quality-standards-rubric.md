# Geragogy-Grounded Digital Learning Quality Standards Rubric

> **Status:** Draft v1 — filtered from the closed-world reference library and five expert resources.  
> **Purpose:** Standardized assessment rubric for digital curriculum quality aimed at older adult learners.  
> **Dominant Framework:** Geragogy. All dimensions are grounded in principles of older adult learning, cognitive aging, and dignity-centered design.

---

## I. Design Philosophy

This rubric treats **geragogy** as the primary lens through which all quality dimensions are assessed. The five expert resources (Quality Matters, OECD, UNESCO, Gates & Wilson-Menzfeld, Formosa & Fragoso) are filtered through geragogy principles drawn from the closed library:

- **C1** — Fisk et al. (2009): Human factors, cognitive aging, perceptual/motor changes, environmental design for older adults.
- **C3** — Knowles et al. (2019): HCI and aging beyond accessibility; autonomy, judgment preservation, identity.
- **C4** — Lazar, Brewer & Knowles (2025): The "critical turn" in HCI and aging; dignity, structural barriers, emotional experience of technology.
- **C5** — AARP & OATS (2021): Age-inclusive design as a practical discipline; self-efficacy, trust, and safety.
- **D1** — Sweller, Ayres & Kalyuga (2011): Cognitive Load Theory; intrinsic, extraneous, and germane load management.
- **B2** — Norman (2013): Mental models, affordances, and the design of understandable systems.

These are filtered through the **Cognitively Protective Interface Design Contract** (`CONTRACT.md`), which mandates: predictability, confidence preservation, spatial stability, cognitive load containment, dignity, and reversibility.

**New methodology sources (added v2):**
- **A1** — Sweller, van Merriënboer & Paas (2019): Updated Cognitive Load Theory; element interactivity, worked-example effect, expertise reversal.
- **A2** — Clark & Mayer (2016): Evidence-based multimedia learning principles (segmenting, pre-training, personalization, coherence).
- **A3** — Merrill (2002): First Principles of Instruction — task-centered, activation, demonstration, application, integration.
- **A4** — van Merriënboer & Kirschner (2018): 4C/ID model for complex skills — whole-task sequencing, supportive/procedural information.
- **A5** — Kalyuga (2012): Worked-example effect as a technical instructional-design principle for novices.

---

## II. Quality Dimensions

Each dimension is scored on a four-level scale:

| Level | Label | Meaning |
|-------|-------|---------|
| 4 | **Excellent** | Exceeds geragogy standards; demonstrates mastery of older-adult-centered design |
| 3 | **Proficient** | Meets all geragogy standards; no deficiencies |
| 2 | **Developing** | Partially meets standards; one or more areas need improvement |
| 1 | **Insufficient** | Fails to meet basic geragogy standards; redesign required |

---

## Dimension 1: Cognitive Load Containment

> *Grounded in: D1 (Cognitive Load Theory), C1 (perceptual/cognitive aging), CONTRACT.md Section I-G (motion suppression), Section V.10 (cognitive load preservation)*

**Geragogy Principle:** Older learners experience greater difficulty managing divided attention, working memory decline, and novelty-induced load. The curriculum must actively reduce extraneous cognitive load and manage intrinsic load through careful pacing.

| Score | Criteria |
|-------|----------|
| **4** | One idea per screen. No concurrent animations, alerts, or status changes. Content complexity ramps smoothly (max 1 level change per unit). Every element earns its place. |
| **3** | Content is chunked appropriately. Minimal on-screen distractions. Complexity progression is visible to the learner. |
| **2** | Some screens contain multiple competing ideas. Occasional visual or motion distractions. Complexity jumps without warning. |
| **1** | Dense, information-heavy screens. Concurrent animations, pop-ups, or alerts. Complexity unpredictable or overwhelming. |

**Evidence to look for:**
- Single-focus principle per page (C1; D1)
- No bounce, spring, or attention-drawing motion (CONTRACT.md)
- Progressive disclosure: advanced options hidden by default (CONTRACT.md)
- ≤5 primary actionable elements at any moment (CONTRACT.md)
- Complexity values explicit and monotonically increasing per module

**Cross-reference to expert resources:**
- **QM Standard 1.5** (Course Overview), **Standard 2** (Learning Objectives) — alignment with clear, chunked learning goals.
- **A1 (Sweller et al., 2019)** — Element interactivity drives intrinsic cognitive load; single-focus pages reduce interactivity.
- **A5 (Kalyuga, 2012)** — Worked-example effect: studying complete examples is more efficient for novices than problem-solving; the 4-page structure with ExampleBlock embodies this.
- **Gates & Wilson-Menzfeld** — Negative perceptions of aging are heightened when learners feel overwhelmed; cognitive overload reinforces "technology is not for me."
- **Formosa & Fragoso** — Quality assessment must account for "cognitive changes" as a distinct quality variable.

---

## Dimension 2: Learner Agency & Human Authority

> *Grounded in: C3 (autonomy, judgment preservation), C1 (human-in-control framing), CONTRACT.md Section III (state transparency), Section VII (dignity, reversibility)*

**Geragogy Principle:** Older adult learners must be positioned as the decision-makers at every stage. The technology (and the curriculum teaching it) exists to support their judgment, not replace it. Reversibility must be explicit and always available.

| Score | Criteria |
|-------|----------|
| **4** | Every unit explicitly reinforces that the learner decides, reviews, changes, or stops. No suggestion of algorithmic authority. Reversible actions clearly labeled. No urgency language anywhere. |
| **3** | Learner control is stated in principles and examples. Reversibility is available but not always explicitly named. No urgency language. |
| **2** | Learner control is implied but not stated. Some actions are irreversible without warning. Occasional urgency framing. |
| **1** | The curriculum positions the tool (AI, agent, skill) as the expert. Learner is passive. Irreversible actions unmarked. Urgency or FOMO present. |

**Evidence to look for:**
- Pronouns: "You decide," "You review," "You choose" (C3)
- Principle statements name the learner as the authority
- Retrieval choices frame wrong answers as "fine things to think about" — no penalty, no shame
- Every state-changing action uses standard confirmation phrasing (CONTRACT.md III)
- No "hurry," "urgent," "limited time," "act now," "expires" (CONTRACT.md III)

**Cross-reference to expert resources:**
- **OECD Digital Education Outlook** — Governance frameworks that center student agency over platform control.
- **UNESCO Pillar 1** (Inclusive and equitable) — learner agency as an equity principle.
- **Gates & Wilson-Menzfeld** — Empowerment is the implicit thread of geragogy; programs that succeed embody learner agency even when not explicitly labeled.
- **Formosa & Fragoso** — "Your judgment comes first" is the foundational geragogy stance; quality standards must test for it explicitly.

---

## Dimension 3: Language, Legibility & Cognitive Legibility

> *Grounded in: C1 (perceptual aging, reading comfort), C5 (age-inclusive design), CONTRACT.md Section I-C (typography), Section III (language rules)*

**Geragogy Principle:** Older adults benefit from high-contrast, well-spaced text; short sentences; plain vocabulary; and concrete over abstract explanations. The language must preserve dignity — never patronizing, never overly technical.

| Score | Criteria |
|-------|----------|
| **4** | Short sentences (≤15 words average). Plain, familiar vocabulary. Concrete scenarios only. No jargon without immediate plain explanation. Minimum 16px font, 1.5–1.7 line height. No all-caps. Headings ≤1.4× body. |
| **3** | Mostly short sentences. Minimal jargon. Scenarios are relatable. Typography meets contract minimums. |
| **2** | Some long or complex sentences. Occasional unexplained jargon. Some abstract explanations. Typography partially compliant. |
| **1** | Dense, academic, or technical language. Abstract principles without concrete grounding. Typography below contract minimums. |

**Evidence to look for:**
- Sentence length distribution (sample 10 sentences per unit)
- Presence of everyday scenarios (gardening, family letters, meals, medication) vs. work/technical scenarios
- Jargon density: terms like "API," "prompt engineering," "LLM" are absent or explained in plain language
- Typography: 16px+ base, 1.5–1.7 line-height, humanist sans-serif (CONTRACT.md)
- Maximum 3 text levels visible simultaneously (CONTRACT.md)

**Cross-reference to expert resources:**
- **QM Standard 4** (Instructional Materials) — materials must support readability and accessibility.
- **A2 (Clark & Mayer, 2016)** — Coherence principle: eliminate extraneous words; personalization principle: conversational tone enhances learning.
- **C5 (AARP/OATS)** — Age-inclusive design explicitly calls for larger fonts, higher contrast, and plain language.
- **Formosa & Fragoso** — Quality instruction for older adults must account for perceptual changes as a design variable, not an afterthought.

---

## Dimension 4: Confidence Preservation & Emotional Safety

> *Grounded in: C4 (dignity, emotional experience of technology), C5 (self-efficacy, trust), Gates & Wilson-Menzfeld (negative perceptions of aging), CONTRACT.md Section VII (confidence preservation)*

**Geragogy Principle:** Older adult learners often carry negative perceptions about their own capacity to learn technology. The curriculum must actively build self-efficacy, never test it. Errors are system states, not user failures. Learning is framed as exploration, not performance.

| Score | Criteria |
|-------|----------|
| **4** | Retrieval questions have no time limit. Wrong answers are framed positively. No scoring or leaderboard. Progress is private. Learner is praised for reviewing, not just completing. Mistakes are positioned as useful data. |
| **3** | Retrieval is low-stakes. No time pressure. Progress tracking is quiet. Learner generally feels safe to explore. |
| **2** | Some retrieval elements feel test-like. Progress visible to others or comparative. Occasional "correct/incorrect" framing that feels evaluative. |
| **1** | Gamified scoring, badges, leaderboards. Timed quizzes. Public progress. Language implies the learner "failed" or "got it wrong." |

**Evidence to look for:**
- Retrieval blocks: "There is no time limit. Either answer is a fine thing to think about."
- No points, stars, scores, streaks, or leaderboards
- Error messages: "This will change [X]. You can continue or go back." (CONTRACT.md)
- No alarmist, blame-oriented, or urgency phrasing (CONTRACT.md III)
- Examples celebrate thoughtful review and adjustment, not speed or correctness

**Cross-reference to expert resources:**
- **A2 (Clark & Mayer, 2016)** — Segmenting principle: break content into learner-controlled segments; no time pressure respects learner pacing.
- **Gates & Wilson-Menzfeld** — "Negative perceptions of aging" is the dominant barrier to engagement; curricula that feel evaluative reinforce this barrier.
- **C4 (Lazar, Brewer & Knowles)** — The "critical turn" in HCI demands that we treat dignity and emotional experience as first-class design requirements.
- **C5 (AARP/OATS)** — Self-efficacy and trust are foundational to age-inclusive technology adoption.
- **Formosa & Fragoso** — "Emotional dimension of technology learning" is a quality variable that must be assessed, not assumed.

---

## Dimension 5: Progressive Disclosure & Pacing

> *Grounded in: D1 (Cognitive Load Theory — managing intrinsic load), B2 (mental models), CONTRACT.md Section I-F (interaction density), Section IV (UI state envelopes)*

**Geragogy Principle:** Older learners build mental models more slowly and benefit from predictable, gradual exposure. The curriculum must never present advanced concepts before foundational ones are secure. Each unit should feel like a natural next step, not a leap.

| Score | Criteria |
|-------|----------|
| **4** | Four-page structure (recap → principle → example → retrieval) is consistent across all units. Complexity increases by ≤1 per unit. Each module begins with a bridge from the previous. No surprises in structure or pacing. |
| **3** | Structure is mostly consistent. Complexity generally increases. Some modules bridge well. Learner can predict what comes next. |
| **2** | Inconsistent page counts or types per unit. Complexity jumps. Some modules feel disconnected from prior learning. |
| **1** | Random structure. No visible progression. Complexity unpredictable. Learner cannot form a stable mental model of the learning journey. |

**Evidence to look for:**
- Every unit has: recap, principle, example, retrieval (4 pages minimum)
- `complexity` and `max_complexity` values are explicit in the data model
- Module 4: complexity 1 → 3 across 6 units
- Module 5: complexity 1 → 4 across 5 units
- Recap pages explicitly reference prior module/unit learning
- Principle pages state the rule in one sentence before elaborating

**Cross-reference to expert resources:**
- **QM Standard 2** (Learning Objectives) — objectives must be sequenced and measurable.
- **A1 (Sweller et al., 2019)** — Expertise reversal effect: as expertise grows, worked examples can impede learning — justifies the complexity ramp (Module 1 all examples → Module 5 more independent reasoning).
- **A3 (Merrill, 2002)** — First Principles: activation (recap), demonstration (example), application (retrieval) — the 4-page structure is a complete instructional episode.
- **A4 (van Merriënboer & Kirschner, 2018)** — Whole-task sequencing: start with simple complete versions, then increase complexity — validates Module 1→5 progression.
- **D1 (Sweller et al.)** — Intrinsic cognitive load must be managed through element interactivity and sequencing.
- **B2 (Norman)** — Stable mental models require predictable, consistent structure.
- **Formosa & Fragoso** — Older adults' "life experience as prior knowledge" must be leveraged through explicit bridging and sequencing.

---

## Dimension 6: Concrete Over Abstract

> *Grounded in: B2 (mental models — concrete affordances are easier to learn), C1 (familiarity reduces cognitive load), CONTRACT.md (no abstract without concrete)*

**Geragogy Principle:** Abstract concepts ("agents," "skills," "algorithms") are difficult for any learner without concrete grounding. For older adults, this is amplified by reduced fluid intelligence and stronger reliance on crystallized knowledge. Every abstract idea must be anchored in an everyday, relatable scenario.

| Score | Criteria |
|-------|----------|
| **4** | Every principle is paired with a concrete scenario (meals, letters, gardening, family events, medication). No technical or work-related examples. Scenarios use named, relatable characters in familiar settings. |
| **3** | Most principles have concrete examples. A few abstract explanations stand alone. Scenarios are generally relatable. |
| **2** | Some principles lack concrete grounding. Examples are occasionally technical (work, coding, business). Scenarios feel generic. |
| **1** | Heavy abstraction. Technical examples dominate. Scenarios are developer-focused or workplace-focused. |

**Evidence to look for:**
- ExampleBlock `situation` field: everyday contexts only (family, home, health, hobbies)
- No references to CLI commands, markdown syntax, API keys, repositories, or code
- Named characters with human contexts (Harold, Maria, Dorothy, James)
- Takeaways tie the concrete scenario back to the learner's own life

**Cross-reference to expert resources:**
- **A3 (Merrill, 2002)** — Task-centered principle: instruction must be anchored in real-world tasks — validates everyday scenarios (meals, letters, family events).
- **A4 (van Merriënboer & Kirschner, 2018)** — Whole-task sequencing requires complete, concrete tasks at every level — abstract decomposition alone is insufficient for novices.
- **A5 (Kalyuga, 2012)** — Worked examples provide concrete, step-by-step demonstrations that are superior to abstract rule statements for novice learners.
- **B2 (Norman)** — Mental models are built from concrete, familiar experiences; abstract design without concrete analogies fails older learners disproportionately.
- **C1 (Fisk et al.)** — Familiarity reduces perceptual and cognitive load; novel contexts increase both.
- **Gates & Wilson-Menzfeld** — "Value of technology" is learned through personal relevance; abstract utility is insufficient.

---

## Dimension 7: Reversibility & Safety

> *Grounded in: CONTRACT.md Section I-F (irreversible action limits), Section III (confirmation gating), Section VII (reversibility)*

**Geragogy Principle:** Older adult learners are more cautious about technology because they fear breaking something or losing work. The curriculum must explicitly demonstrate that every choice can be undone, every setting can be changed, and the learner is never trapped.

| Score | Criteria |
|-------|----------|
| **4** | Every unit mentions that the learner can change, stop, or delete what they created. No permanent actions without confirmation. The curriculum itself models reversibility (go back, review, try again). |
| **3** | Reversibility is stated in principles. Some examples show changing or stopping. Confirmation for major actions. |
| **2** | Reversibility implied but not explicit. Some actions feel final. Limited "go back" affordances. |
| **1** | Curriculum implies actions are permanent. No confirmation gates. Learner feels locked in or exposed. |

**Evidence to look for:**
- Principle content includes: "You can change a Skill anytime. You can stop using it." (Module 4)
- "You can say no to any suggestion. You can stop using an Agent anytime. You can delete it." (Module 5)
- Standard confirmation phrasing pattern used consistently (CONTRACT.md III)
- ≤1 irreversible action visible at any time (CONTRACT.md I-F)

**Cross-reference to expert resources:**
- **OECD Digital Education Outlook** — Data governance and safety as a pillar of digital education quality.
- **UNESCO Pillar 4** (Data and technology governance) — safety, privacy, and learner control as governance requirements.
- **C5 (AARP/OATS)** — Trust is foundational; reversibility is a primary trust signal.

---

## Dimension 8: Personal Value & Life Relevance

> *Grounded in: Gates & Wilson-Menzfeld (value of technology theme), C3 (identity and meaning), C5 (self-efficacy through relevance)*

**Geragogy Principle:** Older adults engage with technology when they perceive *personal value* — not abstract utility, not social pressure, not novelty. The curriculum must connect every concept to outcomes the learner actually cares about: family connection, health, hobbies, independence, dignity.

| Score | Criteria |
|-------|----------|
| **4** | Every example and principle connects to a personally meaningful outcome (writing to family, remembering medication, planning gatherings, staying independent). The learner can see "this is for me." |
| **3** | Most examples connect to personal value. Some connections are implied rather than explicit. Learner generally sees relevance. |
| **2** | Some examples feel generic or utility-focused. Personal value is occasionally present but not emphasized. |
| **1** | Examples are technical or productivity-focused. No clear personal relevance. Learner could reasonably ask "why would I use this?" |

**Evidence to look for:**
- Example scenarios: family letters, meal planning, medication reminders, weekend outings — not work tasks
- Principle statements answer "why does this matter to me?" not just "what is this?"
- Retrieval questions frame choices around the learner's own life decisions
- No examples about "increasing productivity," "streamlining workflows," or "scaling operations"

**Cross-reference to expert resources:**
- **Gates & Wilson-Menzfeld** — "Value of technology" is the strongest predictor of engagement in older adult digital skills programs; curricula must make this value explicit.
- **C3 (Knowles et al.)** — Identity and meaning are central to HCI and aging; technology learning must connect to identity preservation or enhancement.
- **Formosa & Fragoso** — Older adult education quality must account for "life experience as prior knowledge" — the curriculum should leverage this, not ignore it.

---

## III. Scoring & Grading

### Module Grade Calculation

For each module, score all 8 dimensions. Sum the scores. Maximum possible: 32.

| Total Score | Grade | Interpretation |
|-------------|-------|-----------------|
| 28–32 | **A** | Exemplary geragogy-centered curriculum. Ready for learners. |
| 24–27 | **B** | Strong geragogy foundation. Minor improvements recommended. |
| 20–23 | **C** | Acceptable. Several dimensions need attention. Review before release. |
| 16–19 | **D** | Weak geragogy alignment. Significant redesign required. |
| 8–15 | **F** | Fails basic geragogy standards. Not suitable for older adult learners. |
| <8 | — | Catastrophic failure. Curriculum should not exist in this form. |

### Dimension-Level Threshold

Any dimension scoring **1** automatically caps the module grade at **D**, regardless of other scores. A curriculum that fails a single dimension at the basic level is not ready for older adult learners.

### Paid vs. Free Module Parity

Per Sprint P10, paid modules (Module 4, Module 5) must achieve the same grade as free modules (Module 1–3). A grade gap between free and paid modules is a policy violation and blocks promotion.

---

## IV. Audit Process

### Step 1: Sample
Select 2 units per module (first and last) for deep assessment.

### Step 2: Evidence Collection
For each dimension, collect:
- Direct quotes from curriculum content
- Screenshots or data-model excerpts
- Test output (pytest assertions)

### Step 3: Score
Apply the rubric criteria independently. Two assessors recommended. Disagreements resolved by third assessor or senior geragogy reviewer.

### Step 4: Report
Document: dimension scores, total score, grade, specific deficiencies, remediation plan.

### Step 5: Regression Test
After remediation, re-run full test suite and re-audit sampled units.

---

## V. References

### Closed Library (Authoritative)
- **C1** — Fisk, A. D., Rogers, W. A., Charness, N., Czaja, S. J., & Sharit, J. (2009). *Designing for Older Adults: Principles and Creative Human Factors Approaches*. CRC Press.
- **C3** — Knowles, B., Hanson, V. L., Rogers, Y., Piper, A. M., Waycott, J., & Davies, N. (2019). HCI and aging: Beyond accessibility. *CHI 2019*.
- **C4** — Lazar, A., Brewer, R., & Knowles, B. (2025). HCI and older adults: The critical turn and what comes next. *Foundations and Trends in HCI*, 19(2), 112–212.
- **C5** — AARP & Older Adults Technology Services (2021). *Age-Inclusive Technology Design: A Practical Guide*. AARP.
- **D1** — Sweller, J., Ayres, P., & Kalyuga, S. (2011). *Cognitive Load Theory*. Springer.
- **B2** — Norman, D. A. (2013). *The Design of Everyday Things*. Basic Books.
- **P1** — `docs/library/CONTRACT.md` — Cognitively Protective Interface Design, Rendering, and Governance Contract.
- **P2** — `docs/library/IDD-2026-cognitively-protective-iscs.md` — Invention Disclosure Document.

### Expert Resource Library (Contextual)
- **Q1** — Quality Matters. (2023). *Higher Education Rubric Standards (7th ed.)*. MarylandOnline, Inc.
- **O1** — OECD. (2023). *Digital Education Outlook 2023*. OECD Publishing.
- **U1** — UNESCO. (2024). *Six Pillars for the Digital Transformation of Education*. UNESCO.
- **G1** — Gates, J. R., & Wilson-Menzfeld, G. (2022). What role does geragogy play in the delivery of digital skills programs for middle and older age adults? *IJERPH*, 19(15), 9147.
- **F1** — Formosa, M., & Fragoso, A. (2025). Bridging geragogy and pedagogy: Towards a learning-sciences-based approach to older adults' education. *Educational Gerontology*.

### Teaching Methodology & Content Depth (New v2)
- **A1** — Sweller, J., van Merriënboer, J. J. G., & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. *Educational Psychology Review*, *31*(2), 261–292.
- **A2** — Clark, R. C., & Mayer, R. E. (2016). *e-Learning and the science of instruction: Proven guidelines for consumers and designers of multimedia learning* (4th ed.). Wiley.
- **A3** — Merrill, M. D. (2002). First principles of instruction. *Educational Technology Research and Development*, *50*(3), 43–59.
- **A4** — van Merriënboer, J. J. G., & Kirschner, P. A. (2018). *Ten steps to complex learning: A systematic approach to four-component instructional design* (3rd ed.). Routledge.
- **A5** — Kalyuga, S. (2012). Instructional benefits of attending to worked examples in solving problems. *Educational Psychology*, *32*(1), 1–12.

---

*Document updated: 2026-05-25* (v2: added teaching methodology sources A1–A5)*  
*Purpose: Noni Curriculum Quality Assessment — Geragogy-Grounded Rubric*  
*Adoption: Requires ADR per `CONTRACT.md` Section VI*
