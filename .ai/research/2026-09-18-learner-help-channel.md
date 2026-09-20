# Research — Learner "I'm stuck" help channel

**Date:** 2026-09-18
**Intake:** `.ai/intake/2026-09-18-learner-help-channel.md`
**Method:** internal codebase audit + external source review.
Subagent fleet unavailable (quota); research run inline — source
count below the 80 target, flagged honestly below.

---

## 1. Internal audit findings (verified against code)

### 1.1 The geragogy contract (`docs/library/CONTRACT.md`)

| Question | Answer | Basis |
| --- | --- | --- |
| Chat widget allowed? | **No.** The component inventory is closed: 11 items (Heading, Body text, Button, Card, Field, List, Divider, Indicator, ConfirmDialog, PendingBanner, BlockedNotice). "No additional components may be introduced without a formal ADR" and "components may not be composed to simulate new component types." A floating live-chat widget also violates "no floating, overlapping layouts" (§I.B). | CONTRACT §I.D |
| Proactive "are you stuck?" prompts? | **No, client-side.** "React MUST NOT infer readiness, mastery, confidence, or emotional state" — the frontend may not detect struggle. A proactive offer would also be an unsolicited interruption, which external evidence flags as harmful for this persona (see §3.2). | CONTRACT §IV |
| Passive "Get help" button + form? | **Yes — fully expressible.** Button, Card, Field, List are all in inventory. Text-first, stable position, ≤5 actionable elements. | CONTRACT §I.D, §I.F |
| `tel:` link? | Precedent exists: `HelpPage.tsx` already renders `tel:+18774094144` with AI-answered disclosure. | `frontend/src/components/HelpPage.tsx:339` |

### 1.2 Identity at purchase — NO PHONE

`backend/services/payment_provider.py:241` — `Session.create(mode="payment")`
with metadata `{product_code, purchase_id, is_gift, buyer_account_id,
buyer_email}`. **No `phone_number_collection`**, no phone field anywhere
in checkout. Identity held on a paying learner = **email only**.
A callback path must collect the phone number at request time.

### 1.3 Existing help surfaces

- `/help` (`HelpPage.tsx`) already offers `mailto:help@mynaani.com`
  and `tel:+18774094144` (the AI receptionist — which as of p16 now
  files every call into the CRM automatically).
- No help affordance exists inside `/curriculum` or `/paid-curriculum`
  pages themselves — a stuck learner must navigate away to `/help`.
- Footer deliberately omits `tel:`/`mailto:` on learner surfaces
  (Footer.test.tsx:87-88 asserts this).

### 1.4 Stuck state — none exists

Progress is `localStorage`-only (`frontend/src/lib/progress.ts`,
`mynaani_progress_v1`, explicitly per-browser, no server round-trip).
No server-side struggle signal exists today — no failed-attempt or
revisit telemetry reaches the backend.

---

## 2. External evidence — channel choice for 55+

| Source | Type | Key finding |
| --- | --- | --- |
| JMIR 2020, "Impact of Age on Patients' Communication and Technology Preferences" (jmir.org/2020/6/e13470) | Peer-reviewed | Seniors >65 prefer **direct/phone** interaction; non-portal users prefer phone over electronic contact. Trust is the dominant theme. |
| ACM ASSETS/CHI 2025, "Call, Text, or Face-to-Face?" (doi.org/10.1145/3663547.3759749) | Academic | 101 older adults; **call-based interfaces** score high on accessibility/ease for those "comfortable with traditional telephony"; avatar > text. |
| arXiv 2603.11303 — voice chatbot in a retirement community (N=25) | Academic | Text chat demands fine-motor typing + visual acuity that decline with age; **voice reduced cognitive load**; 80+ struggled even with touch UI → trend toward zero-touch. |
| Gerontologist 2025 — AI-assisted query reformulation (doi.org/10.1093/geroni/igaf122.2179) | Academic | Older adults' key barrier is **articulating the problem** (verbosity, under/over-specification) — a free-text box alone is a weak channel. |
| CHI 2026 GuideMe (dl.acm.org/doi/10.1145/3772318.3791448) | Academic | Older adults **abandon independent help-seeking tools**; "I don't know how to communicate my intent." |
| BMC Health Serv Res 2024 (s12913-024-11564-1, n=1100, age 75+) | Peer-reviewed | Training/support preferences vary sharply with prior digital experience — segment, don't assume. |
| W3C COGA "Limit Interruptions" (w3.org/WAI/WCAG2/supplemental/patterns/o5p01) | Standards | Interruptions cause task abandonment for memory/attention-impaired users; provide user-initiated control, never unsolicited prompts. |
| W3C COGA "Making Content Usable" (w3.org/TR/coga-usable) | Standards | Breadcrumbs/clear headings help reorientation; quiet environment; user-controlled interruptions only. |
| Figshare 32981878 — robot interruptions, n=275 age 65+ | Academic | Interruptions **increase distrust and reduce intention to use**; politeness strategies don't fully recover it. |
| ACM 2025 "When To Help?" non-intrusive struggle detection (doi.org/10.1145/3772363.3798756) | Academic | Struggle detection for older adults is an open research area — signals are subtle; intrusion risk is the design problem. |
| Geragogy review, PMC9364233 (systematic, 17 papers) | Peer-reviewed | Geragogy = empowerment + autonomy; help must be learner-controlled, not imposed. |
| Ed Psych Rev / DOI 10.1080/03601277.2025.2569386 | Peer-reviewed | Older learners benefit from relationship-based, meaningful support — human contact over automation. |
| Mindful callback guide (getmindful.com) | Industry | Callback requesters tolerate longer waits 2×; control over timing builds trust. |
| Megabite web-callback guide | Industry | 2-field forms beat 5-field by ~30% completions; callback captures high-intent hand-raisers. |
| RocketChat docs — livechat-widget-installation, omnichannel-admins-guide | Vendor docs | RC Livechat is a real embeddable widget (script + allowed-domains + offline messages → channel). Feasible technically. |
| RocketChat system requirements | Vendor docs | MongoDB 8.0+ hard dep; some widget customization fields are Enterprise-badged. |

---

## 3. Synthesis

### 3.1 The contract and the evidence agree

Two independent lines converge on the same design:

- **Contract:** only passive, text-first, inventory components; no
  floating widgets; no client-side state inference; no unsolicited
  interruption.
- **Evidence:** this persona prefers voice/phone, abandons
  independent help-seeking (can't articulate the problem), and is
  harmed by unsolicited interruption (distrust, abandonment).

**RC Omnichannel/Livechat fails on both axes** — it's a floating
chat widget (contract needs an ADR that would contradict §I.B/§I.D)
and typing-based chat is the weakest channel for this persona.

### 3.2 Recommended mechanism

**A persistent, text-first "Get help" affordance inside the
curriculum** (Button or stable footer item — same position on every
curriculum page per §I.B spatial-stability), opening a Card with
three contract-native options:

1. **"Call us"** — `tel:+18774094144`. Zero typing. The AI
   receptionist already answers and (p16) files the call as a CRM
   contact automatically. Preferred channel per the evidence.
2. **"We'll call you back"** — a 2-field form (phone number +
   optional "what are you stuck on?"). Submit → CRM form intake →
   contact + task → RocketChat `#crm-alerts` notification → human or
   Retell outbound (p18) callback. Phone collected at request time,
   which solves the no-phone-at-checkout gap.
3. **"Email us"** — `mailto:help@mynaani.com`. Async fallback.

**RocketChat stays internal-only** — the p19 boundary holds: RC is
where the alert lands, never the learner-facing channel. The scope
tension dissolves.

### 3.3 On proactive stuck detection

Not recommended for V1: contract-prohibited client-side (React may
not infer state), no server-side struggle signal exists (progress
is localStorage-only), and COGA + the interruption studies say
unsolicited prompts harm this persona. A passive affordance +
"you can always reach us" copy on the curriculum menu is the
contract-correct V1. If proactive help is ever wanted, it must be a
backend-approved envelope state + an ADR — revisit only after
server-side progress exists.

---

## 4. Decision matrix

| Option | Contract? | Persona fit | Effort | Confidence |
| --- | --- | --- | --- | --- |
| A. Passive help affordance → call / callback form / email | ✅ expressible today | ✅ strong | Small (frontend + intake reuse) | **High** |
| B. RC Omnichannel livechat widget | ❌ ADR + likely violates closed inventory | ⚠️ typing barrier | Medium (RC config + widget) | Low |
| C. Proactive stuck detection | ❌ prohibited client-side, needs server progress + ADR | ⚠️ interruption harm | Large | Low |
| D. Nothing (status quo — /help only) | ✅ | ⚠️ discoverability | Zero | — |

**Recommendation: Option A**, with callback form posting through the
existing tracking/intake path (already files contacts) plus an
explicit help-request marker so `#crm-alerts` can distinguish
"learner needs help" from marketing submissions.

## 5. Edge cases

1. Learner has no phone / won't share it → email path still works.
2. Learner requests callback outside waking hours → RC alert queues;
   message copy must set expectation ("we'll call between 9–5").
3. Callback form spam → CRM dedupe + machine-address filters exist;
   honeypot field recommended.
4. Learner's phone ≠ the number they call from → request form's
   number is authoritative.
5. Help request filed as generic `form_submit` → needs a
   distinguishable marker (hidden field or dedicated path) so
   alerts tag it `[help]` not `[form]`.
6. Free-track learners (no purchase) can still ask for help → fine;
   they file as TRACKING-sourced contacts.
7. Dual-audience guard: affordance on learner pages only — never on
   `/for-communities` (facility journey has its own channels).
8. `tel:` on a tablet/desktop without a phone app → show the number
   as readable text, not only a link (HelpPage pattern).

## 6. Gaps

- Source count ~20 verified (target 80 — subagent quota exhausted).
  Enough for the decision; deeper quota if the ADR is contested.
- RC Omnichannel licensing nuances on the deployed RC version
  unverified — moot under Option A.
- Whether backend "help request" envelope state is needed or plain
  form suffices — decided at plan stage.

## 7. What this needs from the owner

- Approve Option A direction (passive affordance, RC stays internal).
- Copy sign-off on button/help-card wording (dignity language —
  "Get help" vs "I'm stuck" matters for this persona).
- Callback hours commitment (who calls back and when).
