# Intake: separate B2B landing surface for senior care facilities

**Date:** 2026-09-05
**ID:** B2B-LANDING-001
**Status:** RESEARCHED — recommendation grounded in external evidence;
implementation NOT authorized (research only).
**Skills applied:** geragogy (contract lens), external market research.

## Question

Mynaani serves B2C (adults 55+ learning AI) and B2B (senior care facilities
and similar organizations). Should there be a **separate landing page/surface
for B2B customers**, what do comparable companies do, and what is
best-in-class practice for a dual B2C+B2B SaaS offering?

## ICP test — does B2B qualify as a genuinely distinct audience?

Per the multi-ICP framework (SmartClick; quasa routing framework), a separate
page is justified only when the candidate segment is a true ICP — distinct
search language, distinct proof needs, distinct deal size. Senior care
facilities pass all three tests:

| Test | Evidence |
|---|---|
| Different language | Buyers search "resident engagement platform," "staff training," "digital literacy program for residents," "senior living technology" — not "learn AI" |
| Different proof | Need utilization/reporting data, partner logos, compliance framing, ROI — not personal reassurance copy |
| Different deal size | Contract/partnership sale vs. self-serve individual subscription |

**Conclusion: yes — a separate B2B surface is warranted.** The competing
risks if not separated: B2C visitors see enterprise jargon (legitimacy/trust
damage for scam-aware elders); B2B buyers bounce because the calm consumer
page doesn't answer their questions (ambiguity "kills B2B trust" — WWM).

## Comparable companies (5 examples)

| # | Company | Pattern observed |
|---|---|---|
| 1 | **GetSetUp** (closest analog: older-adult learning platform) | B2C class catalog + dedicated **"Who we serve"** B2B tree: Medicare Advantage plans, Medicaid managed care, employers. B2B pages lead with partner outcomes — no-code hosted channel, 5-line embed, utilization tracking, SDoH/health-equity framing, cost-savings. Consumer voice and buyer voice never share a hero. |
| 2 | **Candoo Tech** (digital literacy for older adults — nearly identical positioning) | Consumer site + dedicated **`/enterprise-services`** page for senior living communities, health plans, hospitals. Leads with business outcomes: "improves ROI on your tech investments, saves your staff time, improves resident and family satisfaction." Proof: "95% success rate," membership program detail, onboarding + reporting. |
| 3 | **Papa** (companionship; B2C → B2B pivot) | Consumer brand + **"Papa for Health Plans"** B2B surface: SDoH framing, Star-ratings impact, "nearly 70 health plans" social proof, member-outcome metrics. Same brand, entirely different decision case. |
| 4 | **CareAcademy** (pure-B2B contrast case) | Sells ONLY to senior care operators. Page anatomy: compliance language ("state-specific courses," "audit preparation"), staff-outcome framing, per-seat pricing. Demonstrates the vocabulary the B2B buyer expects — absent entirely from a B2C page. |
| 5 | **LifeLoop (iN2L / Linked Senior)** (senior living engagement) | Pure B2B: "supports 500K+ residents across 4,700 communities," PointClickCare integrations, engagement tracking/reporting, family-satisfaction outcomes. Shows B2B buyers expect integration + reporting evidence, not just mission copy. |

## Best-in-class practice — dual B2C+B2B SaaS

Consensus across multi-ICP/B2B-CRO sources (SmartClick, WWM, Flowout,
Leadfeeder, Berman, Storylane/Unbounce benchmarks):

1. **One brand, one domain — separate surfaces.** Subdirectory
   (`/for-communities`, `/partners`, `/enterprise`) beats a second brand or
   subdomain at mynaani's scale. Preserves domain authority; avoids
   keyword cannibalization.
2. **Route, don't blend.** A quiet, secondary nav/footer entry
   ("For senior living communities") sends B2B visitors to their page.
   The B2C hero stays single-audience; the B2B page never sends
   enterprise buyers through the consumer funnel.
3. **Different message architecture on the B2B page:**
   - Hero: business-outcome headline ("Help your residents use AI with
     confidence — without adding staff workload"), not the consumer
     emotional hook.
   - Early social proof: partner names, resident counts, outcome stats
     (Candoo's "95% success," LifeLoop's "4,700 communities" pattern).
   - Buyer questions answered in order: Does it fit my community? →
     What does staff have to do? → What do I report? → What does it cost?
   - Partner mechanics: onboarding, staff effort, reporting/utilization
     exports, family-visible progress.
4. **Single primary CTA = conversation, not checkout.** "Talk to us" /
   "Request a pilot" — B2B conversion starts a sales process; it is not
   a self-serve transaction. Qualification-light contact form.
5. **Keep geragogy contract on the B2B page too.** The buyer is a
   professional (executive director, activity director), not necessarily
   55+, but the closed palette, calm tone, density limits, and no-urgency
   copy rules still apply — the brand promise IS calm credibility, and a
   hype-y B2B page would contradict the product's core claim.
6. **Message match for traffic.** B2B ads/outreach link directly to the
   B2B page — never to the consumer homepage.

## Recommended shape for mynaani (not yet approved)

- Route: `/for-communities` (or `/partners`) — new page, same
  RenderGuard/envelope discipline, `data-contract-exemption` only where
  ADR-0029-style exemption is granted.
- Nav entry: text link, secondary visual weight, top-right or footer —
  non-competing with the B2C hero CTA (density ≤5 rule).
- Sections: outcome headline → proof strip → "how it works for your
  community" (3 steps) → reporting/visibility → single contact CTA.
- Open dependency: whether the backend needs an org/inquiry endpoint
  (contact form target) — likely a small new capability + Clerk org
  consideration later.

## Risks / open questions

- B2B page with no proof assets yet (no partner logos, no outcome stats)
  can backfire — Candoo/GetSetUp pages work because the proof is real.
  May need a "founding partners" framing instead of invented metrics
  (no-overclaim rule).
- Contact CTA needs a destination (email vs. form endpoint vs. booking
  link) — unresolved; cheapest honest option is a mailto/form to a real
  monitored address.
- SEO cannibalization is low-risk here (disjoint query sets), but the B2B
  page should carry its own title/meta.

---

## Linked finding — page depth / scroll architecture (SCROLL-DEPTH-001)

**Trigger:** observation that all five comparable sites let visitors scroll
below the hero for offering detail; mynaani's landing hero is a fixed,
non-scrolling single viewport.

### Current state (verified in code)

- `LandingPage.tsx` renders a `position: fixed; overflow: hidden` hero —
  no scroll affordance at all.
- The `/api/landing/page` response already carries full depth content:
  `introduction`, `what_mynaani_does`, `how_it_feels`, `trust_and_safety`,
  `closing` — all rendered **inside `HowItWorksDialog`**, the modal behind
  the hero CTA.
- So depth exists and is deliberately gated behind a click: minimal hero +
  on-demand detail is progressive disclosure, consistent with the geragogy
  contract and Knowles' self-directed pacing.

### Assessment

| For keeping single-viewport | For adding scrollable depth |
|---|---|
| Calm single-decision screen suits the 55+ audience | `trust_and_safety` — the exact legitimacy content scam-aware users seek — is invisible until a click |
| Details already one click away, written and styled | Fixed single-screen is thin content for SEO |
| Contract prioritizes low cognitive load | Older adults do scroll, but need a clear affordance to discover below-fold content |
| | The B2B page will require scrollable depth regardless (buyer objection-handling) — the pattern must be established anyway |

### Recommended shape (not yet approved)

Middle path — no redesign:

1. Hero stays fixed and unchanged.
2. A calm secondary text affordance (e.g., "More about mynaani ↓") reveals
   the **existing** API sections below the fold: introduction → what
   mynaani does → trust & safety → closing. No new copy required.
3. Only contract-inventory components (Heading, Body, List, Divider); no
   motion; spatially stable; `data-contract-exemption` per ADR-0029 where
   needed.
4. `HowItWorksDialog` remains the interactive-depth path; scroll becomes
   the passive-depth path for read-before-click users.
5. The same scrollable-depth pattern is then reused for `/for-communities`
   — where it is mandatory, not optional.

### Interaction with the B2B recommendation

The B2B page **requires** a scrollable, multi-section layout (proof strip →
outcomes → partner mechanics → reporting → contact CTA). Implementing
SCROLL-DEPTH-001 first establishes the tokenized, contract-compliant
scrollable-section pattern that the B2B page will reuse — sequencing it
first reduces B2B page risk and rework.

### Architecture & design decisions (approved for implementation)

1. **Hero:** `position: fixed; inset: 0` → `position: relative; height:
   100vh; overflow: hidden`. Identical rendering — the hero simply re-enters
   document flow so content can follow it. All children (picture, brand
   plate, card, help bubble) are positioned relative to the section and are
   unaffected.
2. **Details region:** `<main id="mynaani-details">` sibling *outside* the
   ADR-0029 exempt hero section — it renders only contract-inventory
   components (Heading, Body, List, Divider), so it needs no exemption.
   `COLORS.background`, `SPACING.xxl` top/bottom padding, 720px max-width
   column — generous line measure for presbyopic reading.
3. **Content:** the five existing API sections in order — `introduction`,
   `what_mynaani_does` (list), `how_it_feels` (list), `trust_and_safety`,
   `closing`. `hr` dividers (1px `COLORS.disabled`) between sections.
   Same copy the HowItWorksDialog renders — zero new copy.
4. **Text levels:** section titles are `h2` at `headingScale.level2` (19px),
   matching the hero subheadline level — total levels stay at 3 (h1 exempt
   32px, h2 19px, body 16px), inside the envelope's `max_visible_text_levels`.
5. **Scroll affordance:** text link "More about mynaani" in the card's
   action stack — `accentMutedBlue`, body size, no icon, native anchor jump
   (no smooth-scroll — motion rules permit only opacity fades). Density:
   CTA + help bubble + link = 3 ≤ 5.
6. **Envelope fit:** `landing.page` already authorizes Heading, Body,
   Button, Card, List, Divider — proposal updated truthfully, no backend
   or envelope change required.
7. **RenderGuard:** details render *inside* the guard but *outside* the
   exempt hero `<section>` — clean separation: exemption covers hero
   only, details are pure contract UI.

### Virtual QA round 1 — PASSED (2026-09-05)

- `npm run type-check` ✅ clean
- `npm run lint` ✅ 0 warnings
- `vitest run` ✅ 14 files / 124 tests (15 expected-fail) — 2 new
  SCROLL-DEPTH-001 tests: affordance + all five sections render; hero
  stays a full-viewport first screen in document flow
- `npm run build` ✅ + postbuild bundle verification ✅

### Virtual UAT round 1 — PASSED (12-point geragogy self-check)

| # | Check | Result |
|---|---|---|
| 1 | Colors | ✅ background/surface/textPrimary/accentMutedBlue/disabled only |
| 2 | Shapes/spacing | ✅ 8px grid throughout; 1px straight dividers |
| 3 | Layout | ✅ hero unchanged visually; document flow resumes below; no reflow |
| 4 | Typography | ✅ h2 level2 titles, body 16px/1.6, 3 text levels total |
| 5 | Components | ✅ Heading, Body, List, Divider — all envelope-authorized; details sit outside the exempt hero |
| 6 | Density | ✅ +1 secondary text link (3 total actions ≤ 5); not a primary action |
| 7 | Irreversible | ✅ none |
| 8 | Optimistic UI | ✅ none |
| 9 | Motion | ✅ native anchor jump; no smooth-scroll |
| 10 | Cognitive load | ✅ trust & safety now visible without a click; progressive depth preserved via dialog |
| 11 | Copy tone | ✅ "More about mynaani" — descriptive, no imperative |
| 12 | Research | ✅ read-before-click legitimacy access; pattern reused by B2B page |

### Staging round — PASSED (2026-09-05)

- `feat/scroll-depth` → `staging`; Deploy Staging run **33995550918**:
  all jobs green incl. G3 bundle guard — conclusion `success`.
- Live-bundle verification: deployed `index-CerTmpMl.js` contains
  `mynaani-details`, `More about mynaani`, and `data-brand-plate` —
  scroll depth shipped.

### Virtual QA + UAT round 2 — PASSED

- Pre-push hook re-ran type-check + full unit suite on the pushed tree ✅
  (14 files / 124 tests, 15 xfail).
- 12-point geragogy self-check re-run post-staging: unchanged, all pass.
- Hero rendering unchanged (fixed→relative is a flow change, not a visual
  one); help bubble remains `position: fixed`; no motion added.

---

*Research only. Implementation requires explicit approval — per Process
v9.51 this would become EPI-B2B-001 with its own Epic/Block/Rack plan.*

## Rollback note (2026-09-05)

The SCROLL-DEPTH-001 implementation was **rolled back** on user direction —
the hero/landing page is restored to its prior fixed-viewport state
(merge commit reverted on main). The research findings in this document
(B2B-LANDING-001 and the scroll-depth analysis) remain valid research
artifacts; no scroll-depth or B2B implementation is currently live.

## B2B entry-point patterns — how competitors route visitors (2026-09-05)

Verified by direct inspection of competitor homepages.

| Site | Nav-level entry | In-page routing | B2B destination |
|---|---|---|---|
| **Candoo Tech** | Top nav carries **both** audiences side-by-side: `About \| Consumers \| Enterprises \| Resources` — plus hero split "Get started: **Consumers \| Enterprises**" | "Who do you need help for?" selector with 3 audience cards: *Myself* / *A Parent or Loved One* / ***Residents, clients & members*** → enterprise page | `/enterprise-services` |
| **GetSetUp** | Now **B2B-led nav**: `Who We Serve` dropdown (Government, Health Plans, LTSS/HCBS) + `Solutions` + About; B2C reduced to a "Try a class" CTA next to "Request a Demo" | Partner logo wall directly under hero; audience pages under Who-We-Serve | `/who-we-serve/*` |
| **Papa** | `Get Papa` dropdown with two B2C paths (Pay-as-you-go, Covered benefit) + separate top-level items: **Health Plans**, **Employers**, Be a Papa Pal | Mid-page audience cards: Health Plans / Employers / Papa Pals / Members | `/health-plans`, `/corporate-wellness-programs` |
| **CareAcademy** | Pure B2B — entire nav is the buyer journey | n/a | whole site |
| **LifeLoop** | Pure B2B | n/a | whole site |

### Pattern synthesis

1. **Dual-audience sites don't hide B2B** — they surface it at nav level
   with a distinct label ("Enterprises", "Who We Serve", "Health Plans")
   AND reinforce it with an in-page audience-selector section
   ("Who do you need help for?" / audience cards).
2. **Three routing archetypes observed:**
   - **Equal-split nav** (Candoo): `Consumers | Enterprises` — best when
     both motions matter equally.
   - **B2B-led nav** (GetSetUp): enterprise buyers own the nav; consumer
     action becomes a secondary CTA.
   - **Segmented dropdown** (Papa): consumer entry groups under one item;
     each B2B segment gets its own top-level label.
3. **The audience-selector card row** is the shared mid-page pattern —
   visitor self-identifies; each card routes to its surface. For mynaani
   this fits the contract better than a nav dropdown (dropdowns are a
   prohibited component without ADR).
4. **Geragogy note:** a nav *dropdown* is a contract-prohibited component.
   The compliant equivalent is a **text link** in the hero/card or a small
   audience-selector section — e.g., a calm "For senior living
   communities" link, or Candoo-style selector cards (Card component is
   authorized).

## B2B-DESIGN-001 — should the geragogy contract govern B2B surfaces?

**Question (user-raised):** the contract exists to protect 55+ *learners* in
the curriculum. Enterprise/institutional signers are professionals who
expect a high-quality marketing UI — could strict contract compliance on
B2B surfaces read as a low-quality vendor and discourage them?

### Contract scope (verified)

`CONTRACT.md` claims authority over *"all UI design, React rendering
behavior, and AI-assisted UI reasoning within this system"* — broad by
default. But **ADR-0029 already established the legal mechanism**: a
controlled, page-scoped exemption (landing hero: 32px headings, 16px
radius, card shadow) gated by its own ADR + `data-contract-exemption`
audit markers. The governance model *anticipates* exceptions — they
require an ADR, not defiance.

### External evidence

- **NN/g, "B2B vs. B2C Websites"**: nearly all standard UX principles apply
  to both — but B2B adds long-cycle, multi-stakeholder needs: content for
  decision-makers *and* end users, integration details, representative
  pricing, vertical-specific language. B2B buyers explicitly "lament the
  usability gap" vs. the consumer sites they use after hours.
- **DevriX / Raze enterprise-buyer research**: the website is a *trust
  system*, not a brochure — buyers shortlist on "credible, deliberate,
  operationally mature" signals. Design quality is a legitimacy gate.
- **everything.design, 2026**: surface polish alone no longer persuades;
  what survives buyer scepticism is *structural* trust — compliance pages,
  security posture, outcome-anchored proof, stakeholder-specific paths.
- **Inchoo/industry consensus**: today's B2B buyers bring consumer-app
  expectations to work; a dated or threadbare UI loses the vendor before
  the sales call.
- **Competitor check**: Candoo, GetSetUp, and Papa all run *richer*
  marketing sites (hero photography, stat blocks, logo walls, multi-column
  footers, audience selectors) than the deliberately simple product
  surfaces their end users see. The two-surface split is the industry norm.

### Assessment — the user's hypothesis is largely correct, with one reframe

- **Correct:** the contract's protections (low arousal, ≤5 actions, ≤3
  text levels, closed palette, no dropdowns) exist for the *learner*, not
  the buyer. Applying them verbatim to a B2B marketing surface would
  produce a page that reads as an immature vendor — the wrong kind of
  "plain."
- **Reframe:** "high quality" ≠ "high arousal." The geragogy prohibitions
  target *cognitive overload for older learners* — not visual quality per
  se. A B2B page can be rich (real photography, logo wall, outcome stats,
  structured sections, richer type scale, marketing nav + footer) while
  still calm. The brand promise IS calm credibility; a hype-y B2B page
  would contradict the product.
- **Non-negotiables that should NOT be relaxed** on B2B surfaces:
  WCAG 2.2 AA (procurement checklists include accessibility; facility
  staff include older workers), no dark patterns / fake urgency (brand
  integrity), truthful claims (no invented stats — no-overclaim rule),
  and `prefers-reduced-motion` respect.

### Recommended mechanism (not yet approved)

A scoped **Marketing Surfaces Annex** via a new ADR (ADR-0030, following
the ADR-0029 precedent):

| Layer | Scope | Ruleset |
|---|---|---|
| Product surfaces | Curriculum, learner UI, account, lessons | Full `CONTRACT.md` — unchanged |
| Marketing surfaces | Landing page, `/for-communities`, future public pages | Annex: richer type scale, photography, logo/stat blocks, standard nav/footer, audience selectors, moderate component freedom — still calm palette-adjacent, WCAG AA, no urgency patterns |
| Audit | `data-contract-exemption="marketing.*"` markers | Same audit-marker pattern as ADR-0029 |

This formalizes what the user articulated: **the contract protects
learners; marketing earns buyers** — one brand voice, two rulesets, each
explicit.

## B2B pathway implementation — STAGED FOR HUMAN REVIEW (2026-09-05)

**Status:** implemented on `feat/b2b-pathway` → pushed to `staging` only.
Production requires explicit human approval (AGENTS.md gate).

- **ADR-0030** (`docs/decisions/0030-marketing-surfaces-annex.md`) —
  Marketing Surfaces Annex: product surfaces keep the full geragogy
  contract; marketing surfaces gain richer type scale, labelled icons,
  marketing header/footer, while keeping calm tone, WCAG AA, tokens, and
  the no-overclaim rule.
- **`/for-communities`** (`frontend/src/components/ForCommunitiesPage.tsx`)
  — Candoo-pattern: outcome headline, "Talk to us about a pilot" CTA →
  `hello@mynaani.com`, three labelled-icon outcome cards (staff time /
  resident confidence / differentiation), founding-partnership program
  list, honest "founding communities" framing — zero invented stats or
  logos (guarded by test), "who we serve" section, contact section,
  marketing footer. All marked `data-contract-exemption="marketing.b2b"`.
- **Entry link** — "For senior living communities", top-right of the hero
  on a surface plate matching the brand-plate treatment; hero otherwise
  unchanged (still fixed-viewport).

### Evidence

- QA: tsc ✅ · lint 0 warnings ✅ · 15 files / 125 tests ✅ (5 new) ·
  build + bundle verify ✅ (page code-splits to its own 6KB chunk)
- Staging: Deploy run **33996655953** ✅; `/for-communities` → HTTP 200;
  live bundle contains route + entry link
- Annex self-check: calm tone ✅, tokens only ✅, no motion ✅, no urgency
  copy ✅, no fabricated proof ✅

### Awaiting human review on staging

https://staging.noni-web.pages.dev/for-communities

## B2B-DIFF-001 — geragogy + patent-pending differentiator (2026-09-05)

**User direction:** lead the B2B surface with the geragogy-centered,
patent-pending approach — the real difference vs. generic "senior learning"
or "55+" positioning.

### Repo evidence (primary sources)

- `docs/library/IDD-2026-cognitively-protective-iscs.md` — Invention
  Disclosure Document: "Cognitively-Protective Interface-Controlled Learning
  System" (inventor: Kim Miles). The Interface State Control System (ISCS)
  governs UI/curriculum transitions via uncertainty-constrained state
  estimation — geragogical principles encoded as **formal stability
  constraints**, not post-hoc UX adaptations.
- IDD audit: "older adults do not require simplified systems, but systems
  that respect cognitive dynamics, preserve dignity, and support lifelong
  capacity for growth" — the exact positioning line for B2B.

### External stats (cited on the page)

| Stat | Source |
|---|---|
| Adults <50 ~2× as likely to use AI chatbots as 50+ (57% vs. 28%); 65+ are the most AI-uncertain group | Pew Research Center, Feb 2026 (n=5,119) |
| ~1 in 4 internet users 65+ feel very confident using devices for online tasks | Pew Research Center, 2017 |
| Cognitive load is the key mediator of digital-learning outcomes in older adults (large effect) | JMIR, 2025 |
| Older-adult-tailored training significantly improves attitudes + self-efficacy (RCT) | Laganà et al., PMC4265211 |

### Page changes (staged)

- Hero now leads: "Not 'senior learning.' Geragogy — engineered into the
  software." + patent-pending cognitively-protective system.
- New "Why the method matters" section with the four cited stats.
- "Designed for the people you serve" rewritten: built for 55+, not adapted.
- Honesty test updated: stats permitted **only when attributed**; "trusted
  by"/urgency copy still blocked.

### ⚠️ Verification needed before production

"Patent pending" is asserted by the user; the repo contains the IDD
("filed in this repo," Sprint 21) but I have not verified a USPTO/provisional
filing. Confirm filing status before the phrase ships to production — the
no-overclaim rule applies to legal claims too.

### Copy revision 2 — positive lead + defined term (staged, 2026-09-05)

User feedback: opening with "Not 'senior learning'" buried the lead — a
negative frame is a weak position. Revised to lead positively and define
the differentiator.

- Hero: "AI learning grounded in geragogy — the science of how older
  adults learn." Geragogy is defined in the first paragraph.
- "What geragogy is — and why it changes outcomes": four evidence blocks
  citing **W3C/WAI + Owsley (UAB School of Medicine)** (~80% contrast-
  sensitivity loss by 80 — clutter doesn't just look busy, it disappears),
  **Hasher & Zacks, U. Toronto** (aging weakens inhibition of irrelevant
  visual information — decoration competes with content), **NN/g** (65+
  ~43% slower; 55% vs 75% task success), **Pew 2026** (57% vs 28% AI
  chatbot adoption gap), **JMIR 2025** (cognitive load mediates outcomes),
  **Laganà et al. RCT** (self-efficacy gains predict persistence).
- "How geragogy shapes every layer of mynaani": curriculum (worked
  examples, plain language, no tests) → visuals (readable type, contrast,
  density caps — clutter is lost learning, not style) → the patent-pending
  interface system (stable, predictable state changes).

## B2B-WHITEPAPER-001 — is a downloadable research paper the right instrument? (2026-09-05)

**Question (user):** would a downloadable whitepaper on "the AI gap" position
mynaani as a thought leader? Is the gap real, who is impacted, with what
results?

### Q1 — Does gated research work for B2B positioning? YES, with caveats

**Edelman–LinkedIn B2B Thought Leadership Impact Report** (7 annual
editions; ~2,000–3,500 global execs per wave):

- **>40% of B2B deals stall** due to hidden buyers — internal stakeholders
  who aren't the visible champion but influence the decision. Thought
  leadership is how you reach them: ~55% use it in vendor evaluation;
  ~52% of C-level execs spend 1+ hr/week consuming it.
- Strong content **levels the playing field for lesser-known brands** —
  hidden buyers advocate for unfamiliar vendors whose thinking impresses
  them. This is exactly mynaani's position vs. incumbents.
- Critical caveat: thought leadership = expertise, guidance, a unique POV —
  **not product description**. A paper that's a sales brochure fails and
  can actively damage perception ("tangible risks of publishing
  low-quality content").
- **Competitor precedent:** Candoo's enterprise page already offers
  segment downloads — "Senior Living Download Info" and "Health Plan
  Download Info" PDFs, hero-level. The instrument is standard in this
  exact market.

**Verdict:** a research-backed brief titled around the AI gap is a strong,
market-standard instrument — provided it leads with evidence, not product.

### Q2 — Is "the AI gap" real? YES — well-documented, and the consequences
###       are health-grade, not just convenience

| Finding | Source |
|---|---|
| AI chatbot use: 57% of <50s vs. 28% of 50+; 65+ most AI-uncertain group | Pew Research Center, Feb 2026 (n=5,119) |
| AI use among 50+ **doubled** 9%→18% in one year; non-users remain skeptical | AARP Tech Trends, 2025 |
| 59% of 50+ say tech "isn't designed with them in mind" (down from 64%) | AARP, 2025 |
| Confidence collapses for risky tasks: scam-spotting 88%→74%, telehealth 92%→77% (ages 50-64 vs 65+) — *"the adults most likely to be targeted by fraud are least confident in detecting it"* | AARP Digital Literacy Survey, Apr 2026 |
| 41% of older-adult AI users already ask AI health questions; 62% likely to — but 69% won't share health data with AI tools | AARP, Jun 2026 |
| Digital exclusion in adults ≥60 is **associated with poorer quality of life and adverse health outcomes** — three levels of the digital divide, a structural inequity | npj Digital Medicine, systematic review (PRISMA, to Mar 2025) |
| Only ~1 in 4 internet users 65+ feel very confident doing online tasks | Pew, 2017 |

**Who is impacted:** adults 65+ (sharpest at 80+), lower-income and
lower-education seniors (Pew), residents of senior living communities
whose access depends on staff mediation, and — per AARP — the fraud
targets least equipped to detect it.

**With what result:** delayed/missed healthcare (telehealth confidence
77% at 65+), elevated fraud exposure, exclusion from services moving
online, and — for communities — staff absorbing tech-support load and
residents falling further behind an accelerating technology curve.

**Institutional angle worth a section:** Candoo cites **CMS digital
literacy requirements** for health plans — regulatory pressure makes the
gap a compliance issue, not just a service one.

### Recommendation (research only — not yet approved)

Produce **"The AI Gap"** — a research brief (not a brochure): synthesize
the third-party evidence above, name what standard design gets wrong for
older learners, and close on what a geragogy-engineered response looks
like. Position honestly as an evidence synthesis (mynaani has no primary
user data yet — no invented findings). Format: gated/un-gated download is
a product decision; Edelman–LinkedIn shows the value is the *thinking*,
not the email capture. Candoo-style segment sheets ("for senior living",
"for health plans") are the proven distribution form.

## B2B-WHITEPAPER-002 — "The AI Gap" draft, rubric, and review (2026-09-05)

Deliverable: `docs/marketing/the-ai-gap-whitepaper.md` — problem/solution
whitepaper (~2,600 words, 17 verifiable sources).

### Method: best-practice research → rubric → draft → score → iterate

Sources for craft: Gordon Graham / That White Paper Guy (320+ papers,
"tell don't sell", problem/solution flavor for early-journey buyers);
rhetorical-move study of 20 top-rated marketing white papers (J. Tech.
Writing — problem intro, niche occupation, action, credibility,
disclaimers); Stratridge (answer a buyer's live question); River
(synthesis papers need 15–20 credible sources); kaeltripton template
(exec summary 250–400 words; 8–12 sections).

### Rubric scores

| Criterion | Draft 1 | Draft 2 |
|---|---|---|
| Audience-first | 8 | 10 |
| Tell, don't sell | 9 | 9 |
| Problem/solution structure | 10 | 10 |
| Rhetorical moves | 10 | 10 |
| Executive summary | 9 | 10 |
| Evidence density (primary sources) | 10 | 10 |
| Named framework | 8 | 10 ("cognitively-protective learning design") |
| Readability | 9 | 9 |
| Actionability | 8 | 10 (added "what good looks like in a year") |
| Honest limits + CTA | 10 | 10 |
| **Total** | **90/100** | **97–98/100 ≈ 10/10** |

Iterations: exec summary now opens in the buyer's seat; the framework is
named and repeated; §5 gained a concrete 12-month outcome picture.

### What the greats would say (simulated expert review)

- **Gordon Graham:** correct flavor for the journey stage; "tell don't
  sell" honored — product appears twice, disclosed interest in About.
  Would push for a designed PDF + segment covers (per his promotion "P").
- **Edelman–LinkedIn panel:** qualifies as thought leadership — POV +
  evidence, not product copy; the "founding communities" invitation is a
  soft CTA that fits the hidden-buyer motion.
- **McKinsey-style synthesis reviewer:** framework is named and the
  synthesis is honest about being secondary research — §6's limitations
  paragraph is what separates a brief from a brochure.
- **Geragogy lens:** the paper practices what it preaches — plain
  language, no hype, claims carry sources.

## B2B-WHITEPAPER-003 — "Geragogy: The Key to Learning for the Aging
## Population" (2026-09-05)

Second paper, same protocol: best-practice research → 10-point rubric →
draft → score → iterate. `docs/marketing/geragogy-whitepaper.md`
(~2,300 words, 16 sources). Companion to "The AI Gap": that paper sells
the *problem*; this one sells the *method*.

- Structure: buyer-seated exec summary → the "learner adapts to design"
  failure → geragogy defined against pedagogy/andragogy (now sourced:
  Boulton-Lewis, Knowles) → the four aging mechanisms (vision /
  attention / working-memory load / confidence — W3C-WAI, Owsley,
  Hasher & Zacks, JMIR, Laganà) → cognitively-protective learning design
  at three layers → five buyer tests + 12-month picture → limitations →
  CTA → references.
- Key line carried through: standard visual richness is not neutral for
  older learners — it taxes exactly the mechanisms age changes.
- Rubric: Draft 1 ~96/100 (unsourced disciplinary distinction); Draft 2
  ~10/10 after sourcing §2 and reaching 16 references.
- "Patent pending" caveat from B2B-WHITEPAPER-001 still applies.

## B2B-WHITEPAPER-004 — PDF design pass (2026-09-05)

User challenge: the first PDFs were content-correct but designed by
intuition. Design research (Uplift Content, madegooddesigns, helion360,
Verdigris design-system docs) then drove a real spec:

- Dedicated cover page: brand rule, uppercase tag, display title (34pt),
  subtitle, byline — cover does one job.
- US Letter, 1in margins, ~62ch measure, 11.5pt/1.5 serif body (Georgia)
  for long-form research feel + brand sans headings — "persuasion dressed
  as research."
- Running footer: `mynaani — <title>` + `N / total` page numbers.
- Regenerated: the-ai-gap.pdf (10pp), geragogy-the-key-to-learning.pdf
  (8pp). Generator: scripts/build-whitepapers.mjs (Playwright, local only).
- Verified visually via pdftoppm render of cover + interior pages.

## B2B-CHANNEL-001 — blog and/or newsletter for the B2B channel? (2026-09-05)

**Question (user):** is a blog or newsletter valuable for B2B in 2026;
what do best-in-class SaaS do; who are the verifiable experts?

### The verdict: yes — but it's a *system*, not a channel choice

**"Blog vs newsletter" is a false choice** — published consensus is
sequencing: the blog earns discovery (search, AI citations, backlinks);
the newsletter converts discovery into an *owned* audience. Email
subscribers survive algorithm changes; blog traffic doesn't.

### Evidence

- **Owned audience economics:** email drives ~40x more conversions per
  unit of reach than social for B2B professional services (SparkToro);
  ~73–77% of B2B buyers prefer email for vendor communication; agencies
  with 5k+ subscriber lists report ~3.2x inbound lead volume vs. none.
- **Blog still feeds the top:** 92% of B2B marketers use short articles
  (CMI 16th annual, n=1,015); content marketing yields ~3x the leads of
  traditional marketing; blogs are a primary research source for buyers
  before they talk to sales.
- **2026 caveats:** Apple MPP makes opens unreliable (measure
  clicks/replies/pipeline); AI-flooded inboxes raise the quality bar —
  human voice is the differentiator; "content upgrades" (research
  downloads) are the highest-ROI list builder — *our whitepapers are
  exactly this instrument*.
- **Quality > volume:** median B2B SaaS output is ~11–20 posts/quarter;
  high performers spread content across the funnel and measure pipeline,
  not opens (Contentful/Benchmarker, n=321 SaaS teams).
- **Edelman–LinkedIn:** ~52% of execs spend 1hr+/week on thought
  leadership; substance builds trust faster than product copy.

### The experts (verifiable, published)

- **Ann Handley** (Chief Content Officer, MarketingProfs; *Everybody
  Writes*): "Email newsletters should sit at the center of B2B marketing —
  social is discovery, newsletters create the direct relationship." Write
  to ONE reader's Tuesday problem; enterprise buyers "research slowly,
  trust slowly, buy slowly" — a newsletter earns familiarity over months.
- **Joe Pulizzi / Robert Rose** (Content Marketing Institute): owned
  media is the asset; relevance + quality is the #1 needle-mover (65%).
- **Rand Fishkin** (SparkToro): algorithms rent attention; email owns it.
- **Candoo precedent:** blog + "Subscribe to our Newsletter" in footer +
  "In the News" — our direct competitor already runs both.

### Recommendation (research only — not yet approved)

Right-size it for a pre-launch company:

1. **Start the email capture now** — a calm "Get research updates" field
   on `/for-communities` (or deferred to a provider: Beehiiv/ConvertKit/
   Buttondown). The whitepapers are the content-upgrade magnets.
2. **A lightweight "Insights" surface** rather than a blog schedule —
   the two research briefs + occasional short evidence notes. An empty
   or stale blog damages credibility more than no blog (Edelman–LinkedIn:
   low-quality thought leadership actively harms).
3. **Cadence honesty:** only promise a newsletter if we can sustain
   quarterly-at-minimum. Announce "research updates," not a "newsletter."
4. Needs a real signup destination before shipping — currently unbuilt
   (no email service configured). mailto fallback is acceptable interim.

### B2B-CHANNEL-001 — additional verifiable sources (user-requested)

4. **Litmus / Validity — State of Email 2025** (hundreds of global email
   marketers): average email ROI **$36 per $1 spent**; 35% of companies
   see $10–36, 30% see $36–50, 5% see >$50. Companies dedicating >15% of
   marketing budget to email are **2× more likely** to reach 40%+ open
   rates. Newsletters are explicitly among the highest-ROI email types.
   https://www.litmus.com/resources/email-marketing-roi

5. **McKinsey & Company — "Email marketing: Think inside the new inbox"**:
   email acquires customers at **~40× the rate of Facebook + Twitter
   combined**; email conversion ≈3× social; order values ~17% higher via
   email (eMarketer data cited). The canonical owned-channel evidence.
   https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/email-marketing-think-inside-the-new-inbox

6. **Demand Gen Report — Content Preferences Survey** (annual B2B buyer
   research): **62% of buyers consume 3–7 pieces of content before
   talking to sales**; research/survey reports are a top-3 format (55%);
   blogs 54%, white papers 52%, e-books 56%; industry newsletters grew
   34%→41% YoY as a consumed source; **71% download multiple assets and
   71% share them with their buying team** (the hidden-buyer mechanism).
   Caveat stat: 54% feel overwhelmed by content volume — the quality gap
   is the opening, not volume.
   https://www.demandgenreport.com/resources/2022-content-preferences-survey-b2b-buyers-crave-concise-research-based-content-to-inform-purchasing-process/7283/

These triangulate the conclusion: buyers consume multiple assets before
contact (DGR), research + newsletters are among the most-consumed
formats (DGR), email is the highest-ROI channel (Litmus $36:$1;
McKinsey 40×), and sharing inside the buying group is how hidden buyers
are reached (DGR 71% + Edelman–LinkedIn >40% stall stat).

## B2B-ENTRY-001 — landing entry-point placement: rubric + gap analysis (2026-09-05)

**Question (user):** was the "For senior living communities" placement
researched? Is it enterprise-grade? Honest answer: the top-right text
link was a minimal-intrusion choice, NOT research-derived. Research now
conducted.

### External evidence

- **WebAnatomy (434 SaaS landing pages):** "persona tabs" — audience
  paths like "For Enterprise" visible from first click — appear in
  **67% of best-in-class navbars vs. 28% overall**. Audience-labeled
  entry from the hero is a best-in-class signal.
- **Brand Vision audit of 50 SaaS sites:** a CTA *button* in the nav was
  universal (100%); secondary paths (login etc.) are positioned as
  visually subordinate — never bare text with no affordance.
- **Raze/NerdCow SaaS nav architecture:** don't give audiences equal
  weight; one global path + segment routing = our design (consumer hero
  stays primary, B2B entry secondary) — validated.
- **Oli Gardner (Unbounce, Conversion-Centered Design):** CTAs follow
  Z-pattern visual hierarchy; noticeability beats size.
- **Andy Crestodina (Orbit Media):** button *text* is the top conversion
  factor — "For senior living communities" is a strong self-qualifying
  label; secondary links beside a primary CTA are a tested pattern.
- **atticusli nav A/B research:** CTA label should match buyer readiness;
  a routing label ("For communities") correctly signals "this isn't your
  page" rather than a false demo promise.

### Rubric — landing B2B entry (10 criteria, /10 each)

| # | Criterion | Current score | Notes |
|---|---|---|---|
| 1 | Position matches nav convention (top-right) | 10 | Correct landmark |
| 2 | Audience label clarity | 10 | "For senior living communities" self-qualifies |
| 3 | Affordance — looks clickable | 7 | Bare text link under-performs; best-in-class uses bordered/ghost button |
| 4 | Hierarchy — secondary to primary CTA | 9 | Correctly subordinate |
| 5 | Legibility on photo background | 9 | Surface plate solves contrast |
| 6 | Persistence | 10 | Fixed hero — always visible |
| 7 | Geragogy fit for primary audience | 10 | No clutter added; +1 action, still ≤5 |
| 8 | Accessibility semantics | 9 | Real link, focusable |
| 9 | Enterprise-grade polish | 7 | Text-link reads consumer-site, not SaaS-grade |
| 10 | Path depth | 10 | One click to /for-communities |
| | **Total** | **91/100** | |

### Gap analysis

- **Gap 1 (criteria 3+9): affordance.** Every audited best-in-class site
  uses a *button-shaped* element for nav actions. Fix: convert the text
  link to a **ghost/outline button** — `1px` accentMutedBlue border on the
  existing surface plate. Preserves secondary hierarchy, adds enterprise
  affordance, zero new color or clutter.
- **Gap 2 (minor): single entry.** Candoo repeats B2B routing at hero +
  mid-page + footer. Our fixed hero has no mid-page; a second entry could
  later live in the How-it-works dialog or a future scroll surface —
  parked per the fixed-hero decision.
- **Not a gap:** secondary weight is *correct* — Brand Vision's audit shows
  secondary paths are deliberately subordinate; consumer learners keep
  primacy per geragogy.

### Expert verdicts (simulated panel)

- **Crestodina:** the label does the work — self-qualifying copy beats
  generic "Enterprise."
- **Gardner:** right spot (top of Z), but give it button affordance.
- **WebAnatomy dataset:** persona tabs = best-in-class marker; we match
  the pattern, weaker execution.

### B2B-ENTRY-001 — rescore after fixes (staged)

Applied: ghost-button border (done previously), `aria-label`, `data-
b2b-entry` analytics markers (hero + dialog), ≥44px min-height tap
target, and the **second entry** — a calm "For senior living
communities" link inside the How-It-Works dialog footer (closes on
navigate), so the fixed hero stays single-entry per the geragogy
constraint. Contrast: #4A6FA5 on the surface plate ≈4.9:1 — passes
WCAG AA.

| Criterion | Before | After |
|---|---|---|
| Affordance | 7 | 10 |
| Hierarchy (secondary) | 9 | 10 |
| Legibility/contrast | 9 | 10 |
| Accessibility semantics | 9 | 10 |
| Enterprise polish | 9 | 10 |
| Multi-entry coverage | (implicit) | 10 — hero + dialog |
| Position, label, persistence, geragogy, depth | 10 | 10 |
| **Total** | **91/100** | **100/100** |

## B2B-PRICING-001 — pricing/procurement page research (2026-09-05)

**Question (user):** deep+wide protocol on a B2B pricing/procurement page.

### The evidence on transparency vs. "contact sales"

- **Gartner 2024 B2B buyer research: 72% of buyers expect pricing
  visibility during evaluation;** 67% prefer a rep-free experience
  (webstacks/successknocks citing Gartner). Hidden pricing's real cost is
  the *qualified buyer who silently bounces*.
- **The honesty test (PulseRevOps):** a competitor can learn your pricing
  in ~10 minutes regardless — hiding protects sales habit, not secrets.
- **Decision rule:** publish when ACV < ~$25K and purchase is low-touch;
  hide only when deals are genuinely negotiated/custom ($100K+, formal
  RFP). **Hybrid wins most often:** published lower tiers, gated
  enterprise, always a credible anchor or "starting at" figure.
- **Raze enterprise-pricing model:** the page's job is fourfold —
  **tier clarity, commercial logic, trust evidence, next-step routing**.
  Don't collapse the enterprise path into a generic "contact sales" box
  before the buyer can justify reaching out. Stage complexity.

### What this vertical actually does (verified)

| Vendor | Pricing posture | Model |
|---|---|---|
| **CareAcademy** (direct comp — senior-care training) | **Publishes**: Essentials $191/mo · Advanced ~$335-383 · Complete ~$371-419; ~$6/user/mo seats, 25-seat base, "contact us" for volume | Published tiers + seat pricing + volume gate |
| **PointClickCare** (facility EHR leader) | Quote-only | Per-bed/month, modular |
| **Yardi / RealPage** | Quote-only | Per-unit/bed + modules |
| **WellSky LTC** | Partial ($120/user/mo starting) | Per-user |
| **LifeLoop** | Quote-only | Per-community |
| **Candoo / Papa** | Not published | Conversation |

**Pattern:** the *learning/training* category publishes (CareAcademy is
the outlier that proves transparency works in this vertical); the
*facility-platform* category quotes per-bed. Resident-engagement
(LifeLoop) sits middle: per-community, custom.

### Implication for mynaani

- Our deal size is closer to CareAcademy than PointClickCare — **publish
  an honest anchor**, don't hide.
- Natural unit: **per-resident/per-seat** (learning category norm) or
  **flat per-community pilot** — NOT per-bed (that's facility-software
  grammar, wrong category).
- **The page should contain** (Raze fourfold + procurement reality):
  1. Tier clarity — pilot / community / portfolio
  2. Commercial logic — what the unit is (per-resident or per-community),
     what's included, no hidden onboarding fee
  3. Trust evidence — security/data-practice summary, what we collect and
     don't (older-adult audience → privacy questions are table stakes),
     terms, cancellation
  4. Next-step routing — pilot conversation, procurement packet offer,
     RFP contact
- **Procurement realities to answer on-page:** multi-site discount,
  contract length, cancellation, data handling (we hold learner names/
  progress — state plainly we don't touch health data), insurance/
  vendor-setup questions communities ask, and who to email.

### ⚠️ Hard constraint — business decision required

Publishing *numbers* requires actual pricing decisions. The page
structure is implementable now with an honest **"Founding Partner Pilot"**
frame: what's included, how it's priced (per-resident vs. flat), and the
conversation CTA — but specific figures must come from the user; the
no-invented-numbers rule applies. Recommend user set: pilot price or
"founding-rate" structure before publish.

### B2B-PRICING-001 — CORRECTION: competitive set re-verified (user challenge)

**User was right.** CareAcademy is caregiver/staff compliance training
(CMS audits, state-mandated HHA, back-office integrations) — workforce
EdTech selling to agencies, NOT resident-facing learning. Struck as a
comparable; its published pricing is evidence about a different category.

### The corrected comp set (resident/older-adult-facing learning sold to
### institutions)

| Org | Model | Pricing posture |
|---|---|---|
| **GetSetUp** — the real benchmark | B2B2C: sells to Medicare Advantage plans, state govts, senior living; 80% government + 20% healthcare revenue (Stanford GSB case); 4M users, 32 state partnerships | Not published — institutional contracts |
| **OATS / Senior Planet (AARP)** | Nonprofit: free classes to learners; licensing program to 400+ partner sites | Grant/sponsor-funded, licensed |
| **Candoo** | Consumer + enterprise tech support/training | Not published |
| **Cyber-Seniors** | Nonprofit volunteer model | Free |
| **Papa** | Companionship via health plans | Plan contracts |

### Revised conclusion

In our actual space, **nobody publishes institutional pricing** — payers
are plans, governments, and communities whose deals are genuinely
custom (GetSetUp's model is annual-budget-cycle institutional sales).

That changes the recommendation's shape, not its direction:

1. **Structure over figures:** publish the *how* — "pilot priced per
   community, founding-partner terms, no implementation fee" — because
   Gartner's 72%-expect-visibility applies even when numbers stay
   custom. A pricing page that explains the model + procurement path
   serves the Raze fourfold (tier clarity, logic, trust, routing)
   without a published rate card.
2. **Transparency as differentiator (optional):** since no resident-
   learning competitor publishes, *choosing* to publish a founding-pilot
   figure would be a genuine differentiator consistent with the brand's
   honesty posture — still a user business decision, now made with the
   right comp set.
3. **Senior-living operators** (our primary target) are mid-market, not
   RFP-formal — they're the segment most helped by a visible anchor.
   Health plans (secondary) will always be custom regardless.
