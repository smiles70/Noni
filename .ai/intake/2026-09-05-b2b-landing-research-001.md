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
