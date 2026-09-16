# Research — What is the modern enterprise default contact channel?

**Date:** 2026-09-16
**Intake:** `.ai/intake/2026-09-16-p1-contact-channel-modern-default.md`
**Trigger:** Owner — "none of the top-20 eLearning or SaaS companies ship
a button that launches an email client; what is the FAANG-in-class
default? Do Claude/Google agents or OSS repos help? Does Retell AI?"

## Research question

If `mailto:` is not the modern default for partner/contact intake, what
is — short forms, chat, voice, or hybrid — and which agent frameworks or
OSS repos deliver it?

## Source table

| # | URL | Org | Type | Finding |
|---|-----|-----|------|---------|
| 1 | https://cloud.google.com/contact/form | Google Cloud | FAANG | Server-side structured form; no mailto |
| 2 | https://aws.amazon.com/premiumsupport/enterprise-support-contact-us/ | AWS | FAANG | Server-side structured form |
| 3 | https://business.linkedin.com/learn/elearning-solutions-contact-us | LinkedIn Learning | FAANG/eLearning | Form + "chat with a sales rep" + phone |
| 4 | https://www.coursera.org/business/learn-more | Coursera | eLearning top-20 | Demo-request form; no mailto |
| 5 | https://business.udemy.com/request-demo/ | Udemy Business | eLearning top-20 | Marketo demo form; no mailto |
| 6 | https://seniorplanet.org/contact | Senior Planet/AARP | Senior ed | 888 hotline FIRST, form second — never mailto-only |
| 7 | https://seniorplanet.org/hotline | Senior Planet/AARP | Senior ed | Live trainers answer calls as primary support |
| 8 | https://www.candootech.com/umh | Candoo Tech | Senior tech | Phone + email + chat widget — three channels |
| 9 | https://www.gogograndparent.com/about/how-we-work | GoGoGrandparent | Senior services | Phone-first product: "one call" is the product |
| 10 | https://www.thinkwithgoogle.com/_qs/documents/690/click-to-call_research-studies.pdf | Google/Ipsos | FAANG data | 70% of mobile searchers use click-to-call; +8% ad CTR; 61% say calls matter most at purchase phase |
| 11 | https://yougov.com/en-us/articles/50003 | YouGov | Survey data | 52% of boomers prefer calling vs 37% general pop |
| 12 | https://seniorhousingnews.com/2025/03/18/shn-sales-marketing-the-silent-killer/ | Senior Housing News | Industry | 1M calls analyzed: phone = 25% of leads, 46% of move-ins; calls schedule 2x tours vs web leads |
| 13 | https://via.serviam.org/blog/baby-boomer-myths/ | VIA Contact Center | Industry data | Inbound calls produce 5x more tours than form fills for boomers |
| 14 | https://alineops.com/senior-living-sales-marketing-benchmark-report-2026/ | Aline | Industry | 95k-researcher benchmark; phone remains the intent channel |
| 15 | https://livingmetrics.com/blog/speaking-their-language-crm-communications/ | LivingMetrics | Industry | 85+ families prefer direct voice contact at inquiry stage |
| 16 | https://getperspective.ai/blog/2026-form-replacement-report/ | Perspective AI | Industry data | 41% of top-quartile SaaS replaced primary forms with AI conversation; 3.8x conversion lift |
| 17 | https://tglivechat.com/blog/pre-chat-forms-2026-guide | TGLiveChat (Drift/Forrester synthesis) | Industry data | Static forms 2–5% conv.; chat intake 8–15%; but Forrester: form leads close 14% vs chat 9% |
| 18 | https://botnation.ai/en/chatbot-vs-form/ | Botnation | Industry data | Forms 2–5%, lead-gen chatbots 15–30% (vendor-reported) |
| 19 | https://docs.retellai.com/deploy/chat-widget | Retell AI | Vendor docs | Script-tag widget: chat + real-time voice + callback modes; no backend proxy needed |
| 20 | https://www.retellai.com/features/book-appointments | Retell AI | Vendor docs | Voice agent books to Cal.com during the call |
| 21 | https://www.retellai.com/use-cases/ai-virtual-agent | Retell AI | Vendor docs | Grounded KB agent; escalates rather than invents; CRM sync (Salesforce/HubSpot) |
| 22 | https://github.com/pipecat-ai/pipecat | Daily/Pipecat | OSS (FAANG-adjacent eng.) | Open-source Python realtime voice-agent framework; v1.0 Apr 2026; fits our FastAPI stack |
| 23 | https://livekit.io / LiveKit Agents | LiveKit | OSS | Open-source WebRTC + agents SDK; self-host or cloud |
| 24 | https://www.assemblyai.com/blog/vapi-vs-pipecat-vs-livekit | AssemblyAI | Technical comparison | Vapi=managed, LiveKit=transport+SDK, Pipecat=pipeline you own |
| 25 | https://cloud.google.com/dialogflow/cx/docs/concept/integration/dialogflow-messenger | Google | FAANG | Dialogflow CX Messenger embeddable chat widget |
| 26 | https://docs.cloud.google.com/gemini-enterprise-cx/cx-agent-studio/deploy/web-widget | Google CX Agent Studio | FAANG | Web widget supports chat + voice + expanded modes |
| 27 | https://github.com/brutusdev0/client-intake-agent | OSS (Claude Agent SDK) | OSS | Next.js Claude intake agent: qualifies, extracts structured JSON, scores hot/warm/cold, posts to webhook — config-driven |
| 28 | https://github.com/lumizone/formto | OSS | OSS | Self-hosted Formspree alternative; inbox + SMTP/webhooks |
| 29 | https://github.com/barancezayirli/dsforms | OSS | OSS | Single-binary Go form backend; SQLite; honeypot+rate limit |
| 30 | https://www.flyn.to/blog/click-to-x-links-mobile-conversion | Flyn | Industry data | tel:/sms:/wa.me convert 30–50% higher than forms on mobile; click-to-call 8–15% vs 1–2% form |

## What is the modern default — answered

The top-20 eLearning and SaaS pattern is **layered**, never a single
mailto:

1. **Primary: short structured form → server endpoint → CRM.** (Google
   Cloud, AWS, Coursera, Udemy, LinkedIn Learning, GetSetUp.) We now
   match this — `POST /api/v1/site/partner-inquiry` is exactly this
   pattern, minus CRM sync.
2. **Immediate-answer layer: chat/conversation.** 41% of top-quartile
   SaaS now use an AI conversation as primary intake (Perspective 2026);
   LinkedIn Learning pairs its form with "chat with a sales rep."
3. **Voice layer — decisive for our audience.** This is the finding the
   generic SaaS comparison misses. For adults 55+ the phone is the
   highest-converting channel by a wide margin:
   - 52% of boomers prefer phone contact (YouGov #11)
   - Inbound calls → 5x more tours than form fills (VIA #13)
   - Calls = 25% of leads but 46% of move-ins (SHN #12)
   - Senior Planet puts an 888 hotline above the fold on every page (#6)
   - GoGoGrandparent's entire product is "make one call" (#9)
4. **mailto:** survives only as an unadvertised fallback — which is where
   we keep it today.

## Decision matrix

| Option | Fit for us | Effort | Risk | Confidence |
|--------|-----------|--------|------|------------|
| **A. Current form + add `tel:` click-to-call + callback request** | High — matches senior-living best practice; zero new deps | Low | Needs a real phone number from owner | **High** |
| **B. + Retell AI voice/callback widget** | High — 24/7 AI voice intake; agent captures inquiry and POSTs to our endpoint; phone-native for 55+ | Medium (vendor config, not code) | Per-minute cost; vendor lock; quality of voice UX needs UAT | **High** |
| C. Pipecat self-hosted voice agent | Medium — OSS, fits FastAPI, full control | High — we own telephony, TTS, turn-taking | Weeks of build; ops burden | Medium |
| D. Dialogflow CX / Google CX Agent Studio chat+voice widget | Medium — enterprise-grade, script embed | Medium | Google account complexity; cost; latency for casual users | Medium |
| E. Claude client-intake-agent (OSS repo) as chat intake | Medium — config-driven, posts structured JSON to our endpoint | Medium | Next.js template — we'd port the pattern to our stack | Medium |
| F. Intercom/Drift chat widget | Medium | Low | Cost; third-party data; icon-only widget conflicts with contract | Medium-Low |
| G. Third-party form backend (formto/dsforms) | Low — we already built our own endpoint | — | Unnecessary indirection | Low |

## Recommendation (staged)

- **Phase 1 (now):** Keep the inline form as primary on `/partners` and
  `/for-communities`. Add a visible **`tel:` call line** to both pages
  ("Prefer to talk? Call us at …") once the owner supplies a number —
  this is the single highest-converting element for this audience and
  costs one line of code. Add an optional **"Call me back" checkbox** to
  the form (captures phone intent without a live line).
- **Phase 2 (owner decision — Retell):** Retell's website widget is the
  best-in-class fit: voice + callback modes, no backend proxy required,
  CRM sync, Cal.com booking — and it directly serves the phone-preferring
  demographic. Evaluate pricing + voice quality on staging before prod.
  Pipecat is the OSS fallback if we need to own the stack.
- **Phase 3 (optional):** Claude-powered chat intake (the
  client-intake-agent pattern) if call volume doesn't materialize —
  captures structure without form fields.
- **mailto:** remains only as the unreachable-endpoint fallback.

## Edge cases / remediation (top items)

| # | Trigger | Impact | Remediation |
|---|---------|--------|-------------|
| 1 | No phone number owned | `tel:` is dead UI | Gate behind `PARTNER_PHONE` env; hide when unset |
| 2 | Retell key missing | Widget 404s | Same env-gate pattern as RESEND_API_KEY |
| 3 | Voice agent hallucinates policy | Trust/compliance | Retell grounded KB + "escalate when unsure" config (#21) |
| 4 | Older adult can't use widget | Exclusion | `tel:` link always present beside widget |
| 5 | Bot calls the voice line | Cost | Retell IVR/caller screening |
| 6 | Callback abuse (lead spam) | Ops | Honeypot + rate limit already on endpoint |
| 7 | Widget script blocked by CSP | Broken UI | Add widget origin to CSP allowlist |
| 8 | Voice call records PII | Privacy | Retell HIPAA/BAA option; disclosure line in call intro |
| 9 | Chat intake vs form redundancy | Confusion | One primary CTA per surface; form stays canonical |
| 10 | mailto still reachable in code | Regression | Keep fallback path only on fetch failure (current) |

## Codebase conflict check

- No conflicts: `/api/v1/site/partner-inquiry` already exists;
  `services/email.py` owns delivery; `PARTNER_INBOX` configured.
- `PARTNER_PHONE` env var needed — owner must supply a real number.
- Geragogy: a "Call us" line is text-first and contract-clean; the Retell
  widget would need an ADR-0033-style annex note (third-party embed).

## Gaps needing owner input

1. Real phone number for `tel:` / callback (also needs staffing plan or
   Retell to answer it).
2. Retell AI account decision — pricing is per-minute.
3. Whether chat intake should ever replace the form (recommend: no —
   keep both).

## Confidence

**High** that form→backend is the enterprise-correct primary; **High**
that voice is the differentiated channel for this audience; **Medium**
on Retell vs. Pipecat pending pricing/ops review.
