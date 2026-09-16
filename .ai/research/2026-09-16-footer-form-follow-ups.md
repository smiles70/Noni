# Research — Footer/form follow-ups: backend email, form redesign, footer contrast, social icons

**Date:** 2026-09-16
**Intakes:**
- `.ai/intake/2026-09-16-p2-backend-partner-inquiry-email.md`
- `.ai/intake/2026-09-16-p2-partner-form-redesign.md`
- `.ai/intake/2026-09-16-p2-footer-rounded-contrast.md`
- `.ai/intake/2026-09-16-p2-footer-social-icons.md`

---

## A. Backend email for partner inquiry

| URL | Org | Finding |
|-----|-----|---------|
| https://docs.telusko.com/docs/fastapi/files-forms-and-background-tasks/sending-emails-and-notifications | Telusko (FastAPI docs partner) | Transactional email API > raw SMTP; background tasks for latency |
| https://resend.com/docs/send-with-fastapi | Resend | First-party FastAPI integration; API-key driven |
| https://catalystproject.ai/insights/resend-vs-sendgrid-vs-postmark-transactional-email | Catalyst | Resend = DX, Postmark = deliverability, SendGrid = platform |
| https://codingeasypeasy.com/blog/asynchronous-email-sending-with-fastapi-celery-and-sendgrid-a-comprehensive-guide/ | CodingEasyPeasy | Async send via Celery/SendGrid; never block request thread |
| https://how2.sh/posts/how-to-automate-email-with-sendgrid/ | how2 | Idempotency keys, bounce handling, env-var API keys |
| https://aws.amazon.com/premiumsupport/enterprise-support-contact-us/ | AWS | Server-side structured form is the enterprise norm |
| https://cloud.google.com/contact/form | Google Cloud | Server-side structured form |

**Decision:** `POST /api/v1/site/partner-inquiry` — Pydantic-validated,
provider-agnostic `send_partner_inquiry()` that uses an env-configured
transactional API key (Resend-style) when present, else logs and returns
`delivered: false`. Async fire-and-forget per error-patterns skill.
No SMTP; no new dependency beyond stdlib `urllib`/`httpx` call to the
provider REST API so Railway deploy needs only env vars.
**Confidence:** High.

## B. /partners form redesign

| URL | Org | Finding |
|-----|-----|---------|
| https://www.getsetup.com/about-us/contact-us | GetSetUp | Short branded copy block + form CTA; org-serving-60+ framing |
| https://gale.com/elearning/getsetup | Gale/GetSetUp | Field set: name, email, job title, institution, state, reason, details |
| https://www.trajectorywebdesign.com/blog/b2b-website-forms/ | Trajectory | Radios beat dropdowns for 2-5 options; conditional logic trims fields |
| https://ivyforms.com/blog/how-to-generate-b2b-leads/ | IvyForms | ≤5 fields convert 120% better; labels above fields; radios save ~2.5s/field |
| https://orbitforms.ai/blog/how-to-design-high-converting-contact-forms | OrbitForms | Single-column, grouped fields, familiar-first ordering |
| https://antforms.com/blog/contact-form-design-converts/ | Antforms | Mark optional clearly; privacy/trust line under submit |
| https://formlova.com/en/blog/contact-form-template-guide-en | Formlova | B2B template: name, email, company, inquiry category, message, data-use notice |

**Decision:** Card form on `surface`, sage-tinted page header, fieldset+legend
radio group for organization type, ≤7 visible fields, privacy line, no
dropdowns (contract), no placeholders-as-labels. **Confidence:** High.

## C. Footer rounded edges + contrast

| URL | Org | Finding |
|-----|-----|---------|
| https://www.uxpin.com/studio/blog/footer-design-basics/ | UXPin | WCAG AA contrast, consistent branding, avoid hard edge-cases |
| https://depechecode.io/website-footer-design-ideas-to-boost-ux-in-2026/ | DepecheCode | Custom bg footer as brand "visual full stop"; 44px social targets |
| https://www.shadcnblocks.com/block/footer19 | shadcn/ui blocks | Contained rounded panel inside dark footer = current enterprise pattern |
| https://www.code-generator.net/templates/footers/curved-footer/ | Code Generator | `border-radius: X X 0 0` contained-panel footer CSS |
| https://a11y.dqm.crownpeak.com/patterns/groupings/social-media-follow/ | Crownpeak a11y | Social links need accessible names + focus rings |

**Decision:** Wrap footer content in a max-width card with `RADIUS.lg`,
`SPACING` inset margins; logo on a `surface` rounded plate so the dark
mark doesn't sit on the green; verify ≥4.5:1 for all text. `#FAFAF8` on
`#4A6D5C` ≈ 5.9:1 — passes AA normal text. **Confidence:** High.

## D. Social icons (Instagram / TikTok / YouTube)

| URL | Org | Finding |
|-----|-----|---------|
| https://a11y.dqm.crownpeak.com/patterns/groupings/social-media-follow/ | Crownpeak | Icons need accessible names; list markup; focus states |
| https://kittygiraudel.com/2020/12/10/accessible-icon-links/ | Kitty Giraudel | `aria-hidden` SVG + visually-hidden/visible label text |
| https://accessiblemindstech.com/ensure-your-websites-social-media-icons-are-accessibility-friendly/ | Accessible Minds | 3:1 non-text contrast, ≥24px targets, focus indicators |
| https://github.com/civictheme/docs/blob/main/components/organisms/social-links.md | CivicTheme | Recognizable brand icons, footer placement, labeled |
| https://github.com/janavipandole/Cara/issues/3164 | Cara | Bare SVG links announce "Link" — must add label |
| WCAG 2.5.8 | W3C | Target size ≥24px minimum (we use 44px) |

**Decision:** Inline SVG brand paths (Simple Icons license: CC0), icon
`aria-hidden` + adjacent visible platform label, `currentColor` →
`COLORS.surface` on the green, 44px target, focus ring via muted-blue
outline. Owner-approved contract exception — ADR filed.
**Confidence:** High.

## Edge cases (top items)

1. Provider key missing → endpoint returns `delivered:false`, logs JSON. ✔ handled in design
2. Double-submit → disable button while in flight. ✔
3. Bot fill → honeypot field `website` rejects silently. ✔
4. Radios on very small screens → stacked fieldset, 44px rows. ✔
5. Icon-only taps on green → `currentColor` surface + focus ring. ✔
6. Cache serving old footer → social icons appear after edge purge. ✔
7. SVG license → CC0 public-domain Simple Icons paths only. ✔
8. Screen reader hears "Link" → aria-label + visible label. ✔
9. Green too dark for amber accents → not used; surface-only text. ✔
10. Provider outage → fire-and-forget log; inquiry captured in logs. ✔

## Conflicts

- V1 contract prohibits icons → resolved via ADR-2026-09-16-social-icons.
- V1 contract prohibits radios implicitly (Field = input/textarea) →
  radios are HTML form controls within Field; documented in same ADR.
