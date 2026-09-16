# Research — Contact / partner CTA: mailto button vs. inline form

**Date:** 2026-09-16  
**Intake:** `.ai/intake/2026-09-16-p3-footer-contact-social-follow-up.md`  
**Research question:** When a visitor clicks "Be our partner" / "Contact us", is launching the system email client via `mailto:` still optimal and acceptable at an enterprise/FAANG level, or is an inline form preferred? What does a best-in-class partner-inquiry form look like for an older-adult / senior-services audience?

---

## Executive summary

- **Enterprise/FAANG pattern is an inline, structured form.** Google Cloud,
  AWS Enterprise Support, Google Workspace, Amazon Business, and Chrome
  Enterprise all route partner/sales inquiries through multi-step forms with
  required fields, not mailto links.
- **Mailto is a low-friction, low-maintenance fallback** but it exposes the
  address to scraping, gives no structured data, relies on the visitor's
  configured mail client, and is rarely used as the primary channel for
  enterprise partner/sales flows.
- **For older adults, the deciding factor is control and clarity.** A form
  that labels every field, avoids dropdowns, explains what happens next, and
  provides a fallback when the user's mail client is unconfigured is safer
  than an opaque "Email us" button.
- **Recommended implementation for Mynaani:** ship a short inline form on
  `/partners` that collects the details a partnership team needs. Use a
  `mailto:`-generated message as an interim submit path that does not require
  new backend email infrastructure, with a clear fallback page if the
  visitor's email client does not open.

---

## Source table

| URL | Author / org | Title | Date | Relevance |
|-----|--------------|-------|------|-----------|
| https://cloud.google.com/contact/form | Google Cloud | Contact Us | 2025 | Enterprise form: name, job title, company email, country, reason |
| https://aws.amazon.com/premiumsupport/enterprise-support-contact-us/ | AWS | Contact Enterprise Support | 2025 | Structured form with job role, region, nature of inquiry |
| https://workspace.google.com/contact/ | Google Workspace | Contact Sales & Support | 2025 | Multi-step business-inquiry form |
| https://business.amazon.com/en/contact-us | Amazon Business | Contact our sales team | 2025 | Form with org size, contact reason, postal code |
| https://chromeenterprise.google/contact/ | Chrome Enterprise | Talk to a Chrome Enterprise expert | 2025 | Multi-step form, explicit progress |
| https://www.getsetup.com/about-us/contact-us | GetSetUp | Contact us | 2025 | Senior-services landing: short copy, "Request a Demo" CTA, social links |
| https://gale.com/elearning/getsetup | Gale (GetSetUp partner) | Request More Information | 2025 | Form fields: first name, last name, email, job title, institution, state, reason, details |
| https://www.gazesite.com/blog/making-your-contact-page-reachable-by-everyone/ | GazeSite ( accessibility ) | Making Your Contact Page Reachable by Everyone | 2025 | Argues mailto can hijack click into unconfigured desktop app; better to print the address and offer a form |
| https://mailtomaker.com/blog/mailto-vs-contact-forms | MailtoMaker | Mailto Links vs Contact Forms | 2026 | Comparison matrix; mailto wins on setup/maintenance, form wins on data/analytics/spam protection |
| https://instantlinkhub.com/blog/mailto-vs-contact-form.html | InstantLinkHub | Mailto Link vs Contact Form | 2026 | Use mailto for simple low-volume sites; forms for structured leads |
| https://www.flyn.to/blog/mailto-vs-contact-form-when-each-wins | Flyn | Mailto vs Contact Form: Which Converts? | 2026 | Mailto converts 30-50% better on mobile; forms protect address and structure leads |
| https://doi.org/10.1145/3763243 | ACM CHI / Idrobo et al. | Accessible Web Design for Older Adults | 2025 | Older adults need simplified content, reduced cognitive load, and clear form structure beyond bare WCAG |

## Decision matrix

| Approach | Enterprise grade | Older-adult safe | Backend cost | Spam protection | Recommendation |
|----------|------------------|------------------|--------------|-----------------|----------------|
| `mailto:` button only | No | Risky (unconfigured client) | None | None (exposes address) | Not for partner CTA |
| Inline form → backend email service | Yes | Yes | High (SMTP/Postmark/SendGrid) | CAPTCHA/honeypot | Best long-term |
| Inline form → `mailto:` body | Interim | Yes if fallback shown | None | Limited | Use now, replace later |
| Formspree/Netlify Forms third party | Yes | Yes | Low | Built-in | Requires vendor review |

## GetSetUp / Gale form field pattern

Fields observed in the partner/demo flow:

1. First name *
2. Last name *
3. Email address *
4. Job title *
5. Organization / institution *
6. Country / state
7. Reason for contact *
8. Relevant details / open message

Mynaani's form should mirror this but avoid dropdowns (contract prohibits them) and keep the field count ≤7 visible at once for cognitive load containment.

## Edge cases and remediation

| # | Trigger | Impact | Remediation |
|---|---------|--------|-------------|
| 1 | Visitor has no default email client | mailto: goes nowhere | Show a confirmation page with the plain address to copy |
| 2 | Visitor on a managed/corporate device | Corporate mail app fills wrong From address | Ask them to double-check the From address before sending |
| 3 | Spam bots scrape the mailto address | Inbox spam | Replace with backend email service in next iteration |
| 4 | Visitor with low digital confidence | Unsure if submission worked | Show explicit "Thank you" + "what to expect next" copy |
| 5 | Mobile screen reader focus jumps after submit | Confusion | Return focus to the heading on the confirmation page |
| 6 | Form fields too small or too close | Motor / vision errors | 44 px min touch targets, 16 px text, 16 px+ gaps |
| 7 | Required fields not marked clearly | Submission errors | Asterisk with explanatory text at the top |

## Conflicts and gaps

- Geragogy V1 contract prohibits icons, so social links in the footer must
  remain text-only unless a discrete ADR is approved.
- The `accentDesatGreen` token is not approved as a footer background in the
  current role table; the owner requested it for brand. A short color-usage
  note or ADR should be recorded.
- We do not have verified social URLs for Instagram, TikTok, or YouTube yet;
  placeholders are currently configured in the footer content.
