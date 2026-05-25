# Curriculum Quality Gap Analysis — Paid vs Free Modules

**Date:** 2026-05-24
**Auditor:** Cascade (AI assistant)
**Scope:** All 5 curriculum modules (M1-M3 free, M4-M5 paid)
**Contract:** ADR 0019 / `docs/library/CONTRACT.md`
**Method:** Content depth review, pedagogical structure analysis, geragogy compliance check

---

## 1. Executive Summary

The paid modules (M4-M5) suffer from a **severe content and structural deficit** compared to the free modules (M1-M3). While the free tier delivers rich, multi-page, interactive lessons with concrete examples and retrieval quizzes, the paid tier offers only thin, single-page, declarative summaries with no interactive elements, no concrete walkthroughs, and no complexity progression.

**Overall Grade:**
- **M1-M3 (Free):** A
- **M4-M5 (Paid):** D+
- **Gap Severity:** Critical — paid customers receive substantially less pedagogical value than free users.

---

## 2. Dimension-by-Dimension Analysis

### 2.1 Page Structure & Lesson Architecture

| Dimension | M1-M3 (Free) | M4-M5 (Paid) | Gap |
|---|---|---|---|
| **Pages per unit** | 4 pages (recap → principle → example → retrieval) | 1 page (content only) | **Critical** |
| **Page type variety** | context, principle, example, retrieval, recap | None (legacy single-page) | **Critical** |
| **Phase-1 expansion** | Full adoption (Sprint 23-25) | Zero adoption | **Critical** |
| **Unit count** | 16 units (7 + 5 + 4) | 11 units (6 + 5) | — |
| **Total pages** | 64 pages | 11 pages | **5.8× deficit** |

**Assessment:** The free modules use the full four-page lesson structure (recap → principle → example → retrieval) that was carefully designed for geragogy compliance in Sprints 23-25. The paid modules never received this expansion. Each paid unit is a single page with 3 lines of content — effectively a syllabus entry, not a lesson.

---

### 2.2 Content Depth & Concrete Examples

| Dimension | M1-M3 (Free) | M4-M5 (Paid) | Gap |
|---|---|---|---|
| **Lines per page** | 4-8 lines + structured blocks | 3 lines only | **Severe** |
| **ExampleBlock usage** | Every unit has detailed situation/claude_says/takeaway | Zero ExampleBlocks | **Critical** |
| **RetrievalBlock usage** | Every unit has 2-choice quiz with explanation | Zero RetrievalBlocks | **Critical** |
| **Concrete scenarios** | Grocery lists, thank-you notes, neighbor mail, email drafts | None — only abstract descriptions | **Critical** |
| **Actionable guidance** | "Type this, then do that" | "Skills are useful" (no how-to) | **Severe** |

**Sample comparison:**

**M2 Unit 1 (Free) — "Coming Back to Claude":**
> "It has been a week since you last used Claude. You open the page and the box is empty, the way it always is. You type: 'Hello again — could you help me plan a small grocery list?' Claude says: 'Of course. Here is a short starter list, organized by the kind of meal: Breakfast: oats, milk, fruit...'"

**M4 Unit 1 (Paid) — "What a Claude Skill Is":**
> "A Claude Skill is something you teach once. It has a name and a clear purpose. Claude uses it when it knows it will help."

**Assessment:** The free content shows the learner *doing* something. The paid content *tells* the learner about something. This violates the geragogy principle of concrete-over-abstract (Fisk et al. 2009, C1).

---

### 2.3 Learning Progression & Complexity

| Dimension | M1-M3 (Free) | M4-M5 (Paid) | Gap |
|---|---|---|---|
| **Complexity range** | 1 → 2 → 3 (gradual ramp) | All complexity=1 (flat) | **Severe** |
| **max_complexity** | 1-3 per unit, ramping across modules | 2-3 (declared but unused) | **Moderate** |
| **Principle → Example → Retrieval flow** | Present in every unit | Absent | **Critical** |
| **Cumulative build** | M1 orientation → M2 sustained use → M3 long-term judgment | M4 abstract definitions → M5 more abstract definitions | **Severe** |

**Assessment:** The free track builds complexity deliberately. Module 1 is orientation (complexity 1). Module 2 introduces ongoing decisions (complexity up to 3). Module 3 consolidates judgment (all complexity 1 by design — protective). The paid track stays flat at complexity 1 with no pedagogical ramp, despite declaring higher max_complexity values.

---

### 2.4 Interactive & Assessment Elements

| Dimension | M1-M3 (Free) | M4-M5 (Paid) | Gap |
|---|---|---|---|
| **Retrieval quizzes** | 16 quizzes (100% coverage) | 0 quizzes | **Critical** |
| **Choice-based interactivity** | Binary choices with explanations | None | **Critical** |
| **Telemetry-driven gating** | ISCS stability checks on every page | ISCS checks present but content too thin to meaningfully gate | **Moderate** |
| **Self-check opportunities** | Learner reads, decides, answers | Learner only reads | **Severe** |

**Assessment:** Retrieval quizzes are the core interactive element of the Phase-1 curriculum expansion. They force the learner to make a decision and receive feedback — a critical part of the learning loop. The paid modules have zero interactivity. The learner reads three lines and presses Continue. This is not a lesson; it is a slide deck.

---

### 2.5 Topic Coverage Depth (Skills & Agents)

| Topic | M4 Coverage | M5 Coverage | Expected Depth | Gap |
|---|---|---|---|---|
| **What is a Skill/Agent** | 3 lines, abstract definition | 3 lines, abstract definition | Definition + concrete analogy | Moderate |
| **When to use one** | 3 lines, vague guidance | 3 lines, vague guidance | Decision framework + examples | Severe |
| **How to create one** | 3 lines, "Claude helps you" | N/A (M5 uses Skills) | Step-by-step walkthrough | **Critical** |
| **Naming conventions** | 3 lines, "good name explains" | N/A | Examples of good/bad names | **Critical** |
| **Testing methodology** | 3 lines, "test safely" | N/A | Concrete test cases + review process | **Critical** |
| **Trust calibration** | 3 lines, "Skills support you" | 3 lines, "agents assist" | Scenarios for when to trust vs. intervene | Severe |
| **Composition (Skills → Agent)** | N/A | 3 lines, "Claude helps assemble" | Actual composition walkthrough | **Critical** |
| **Boundary setting** | N/A | 3 lines, "you decide boundaries" | Boundary-setting exercise | Severe |
| **Human authority preservation** | Mentioned implicitly | Explicit (test passes) | Embedded in every example | Moderate |

**Assessment:** Module 4 claims to teach "Building Claude Skills" but never shows the learner how to build one. Module 5 claims to teach "Composing Agents from Skills" but never shows composition. The content is declarative ("Skills are useful") rather than procedural ("Here is how you create a Skill"). For a paid product promising advanced capabilities, this is a severe value gap.

---

### 2.6 Geragogy Compliance

| Dimension | M1-M3 (Free) | M4-M5 (Paid) | Contract Status |
|---|---|---|---|
| **Short sentences** | ✅ 8-12 words average | ✅ 6-8 words average | ✅ Both compliant |
| **Plain words** | ✅ No jargon | ✅ No jargon | ✅ Both compliant |
| **Concrete over abstract** | ✅ Strong | ❌ Weak (abstract only) | ❌ Paid violates |
| **Confidence-preserving framing** | ✅ Strong | ✅ Present | ✅ Both compliant |
| **No urgency language** | ✅ No "hurry", "act now" | ✅ No urgency language | ✅ Both compliant |
| **Human authority** | ✅ Embedded in examples | ✅ Explicit but thin | ✅ Both compliant |
| **Cognitive load** | ✅ Controlled (4 pages, gradual) | ❌ Too thin to assess meaningfully | ⚠️ Paid under-delivers |
| **Reversibility** | ✅ Retrieval allows reconsideration | ❌ No decision points | ❌ Paid lacks |

**Assessment:** The paid modules maintain the *tone* of geragogy (calm, plain, dignified) but fail on the *substance* — they are so thin that key pedagogical mechanisms (concrete examples, interactivity, reversibility) cannot function.

---

## 3. Root Cause Analysis

### Why the gap exists

1. **Content was drop-in, not authored.** Module 4 and 5 content arrived as "pre-written drops" (ADR 0017, ADR 0020). The adaptation focused on *structural* integration (endpoints, telemetry, citation grounding) not *pedagogical* depth.

2. **Phase-1 expansion never reached paid modules.** The multi-page lesson structure (recap/principle/example/retrieval) was built for M1-M3 in Sprints 23-25. M4-M5 were added in Sprints 19 and 22 *before* this expansion, and never retrofitted.

3. **Declarative scope was accepted.** ADR 0017 explicitly states: "The end-to-end Skill-creation experience... is out of scope until the Claude API vendor pass." This was interpreted as "content can be thin because interactivity comes later." But the free modules prove that rich content is possible without vendor API access.

4. **No content quality gate.** The tests check structural correctness (IDs, telemetry, urgency language, authority markers) but do not enforce pedagogical depth, page count, or ExampleBlock presence.

---

## 4. Remediation Plan

### P10: Paid Module Content Expansion (Critical Priority)

**Goal:** Bring M4-M5 to parity with M1-M3 in structure, depth, and interactivity.

**Specific tasks:**

| # | Task | Module | Effort | Acceptance |
|---|---|---|---|---|
| P10.1 | Rewrite all M4 units as 4-page lessons (recap/principle/example/retrieval) | M4 | High | Each unit has ≥4 pages with proper page_types |
| P10.2 | Add concrete ExampleBlocks to every M4 unit | M4 | High | Each example has situation/claude_says/takeaway |
| P10.3 | Add RetrievalBlocks (quizzes) to every M4 unit | M4 | Medium | Binary choices with explanations |
| P10.4 | Rewrite all M5 units as 4-page lessons | M5 | High | Same structure as M4 |
| P10.5 | Add ExampleBlocks and RetrievalBlocks to M5 | M5 | High | Same standard as M1-M3 |
| P10.6 | Add content-depth test: every unit must have ≥4 pages and ≥1 ExampleBlock | Both | Low | CI-enforced |
| P10.7 | Add complexity progression: M4 units should ramp 1→2→3 across the module | M4 | Medium | max_complexity respected in page allocation |

**Estimated effort:** 2-3 sprints (content authoring is the bottleneck, not code).

---

## 5. Gap Analysis Grid

```
┌─────────────────────────────┬────────┬────────┬────────┬─────────────────────────────┐
│ Dimension                   │ M1-M3  │ M4-M5  │ Grade  │ Gap Assessment              │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Page structure (4-page      │ ✅ 16  │ ❌ 0   │ F      │ CRITICAL — No lesson        │
│ lessons)                    │ units  │ units  │        │ architecture in paid        │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Page type variety           │ 5      │ 0      │ F      │ CRITICAL — No recap,        │
│                             │ types  │ types  │        │ principle, example,         │
│                             │        │        │        │ retrieval in paid           │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ ExampleBlocks               │ 16     │ 0      │ F      │ CRITICAL — No concrete      │
│                             │        │        │        │ scenarios in paid           │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ RetrievalBlocks (quizzes)   │ 16     │ 0      │ F      │ CRITICAL — No interactivity │
│                             │        │        │        │ or self-assessment          │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Content lines per page      │ 4-8    │ 3      │ D      │ SEVERE — Content is         │
│                             │        │        │        │ declarative, not procedural │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Complexity progression      │ 1→2→3  │ 1 only │ D      │ SEVERE — Flat learning      │
│                             │        │        │        │ curve, no challenge ramp    │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Concrete scenarios          │ Rich   │ None   │ F      │ CRITICAL — Abstract only,   │
│                             │        │        │        │ no "show me how"            │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Geragogy tone               │ ✅     │ ✅     │ A      │ Tone maintained             │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Human authority framing     │ ✅     │ ✅     │ B      │ Explicit in M5 (tested),   │
│                             │        │        │        │ implicit in M4              │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ No urgency language         │ ✅     │ ✅     │ A      │ Both clean                  │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Short sentences / plain     │ ✅     │ ✅     │ A      │ Both compliant              │
│ words                       │        │        │        │                             │
├─────────────────────────────┼────────┼────────┼────────┼─────────────────────────────┤
│ Overall pedagogical value   │ A      │ D+     │ —      │ Paid delivers ~17% of the   │
│                             │        │        │        │ learning experience per     │
│                             │        │        │        │ unit vs. free               │
└─────────────────────────────┴────────┴────────┴────────┴─────────────────────────────┘
```

---

## 6. Conclusion & Recommendation

**The paid modules are not production-ready for learner consumption.** They maintain the *voice* of the curriculum (calm, plain, dignified) but lack the *substance* — no multi-page lessons, no concrete examples, no quizzes, no complexity progression, and no actionable guidance on the very skills they claim to teach.

**Immediate recommendation:** Do not promote the paid bundle to learners until P10 (Content Expansion) is complete. The current state risks refund requests and reputational damage — a learner who finishes the rich free track and pays for the paid track will feel cheated.

**Business impact:** The menu (P7) now surfaces M4-M5 with "Locked" indicators. Learners can see the full syllabus. If they purchase and encounter 3-line slides instead of 4-page lessons, the gap between promise and delivery is stark and damaging.

**Priority:** P10 is now the highest-priority item in the paid-modules sprint. Code parity (P4-P7) is complete. Content parity (P10) is the remaining blocker.
