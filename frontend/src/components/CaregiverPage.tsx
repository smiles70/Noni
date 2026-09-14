/**
 * CaregiverPage — marketing surface for adult children, family members,
 * and caregivers who want to give mynaani as a gift.
 *
 * Governed by ADR-0030 (Marketing Surfaces Annex), NOT the learner-facing
 * geragogy contract: richer type scale, marketing header/footer, and
 * outcome blocks are permitted here — but tone stays calm, WCAG AA holds,
 * and no claims are invented. Every element is marked
 * `data-contract-exemption="marketing.caregiver"` for audit.
 *
 * The primary gift action remains the existing public `/gift` checkout;
 * this page explains the journey before sending the caregiver there.
 * Content is static (no envelope, no RenderGuard) per ADR-0030.
 */
import { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../design/tokens";
import ChatWidget from "./ChatWidget";
import SupportContact from "./SupportContact";

const CONTACT = "hello@mynaani.com";
const MAILTO = `mailto:${CONTACT}?subject=Gift%20question`;
const UPDATES_MAILTO = `mailto:${CONTACT}?subject=Research%20updates`;

// ---- Tokenized styles (marketing annex) ------------------------------------

const PAGE: CSSProperties = {
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: COLORS.background,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  minHeight: "100vh",
};

const HEADER: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: `${SPACING.sm}px ${SPACING.xl}px`,
  backgroundColor: COLORS.surface,
  borderBottom: `1px solid ${COLORS.disabled}`,
};

const HEADER_NAV: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: SPACING.lg,
};

const HEADER_LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  fontSize: TYPOGRAPHY.bodySizePx,
};

const HEADER_CTA: CSSProperties = {
  display: "inline-block",
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentDesatGreen,
  color: COLORS.surface,
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  textDecoration: "none",
};

const SECTION: CSSProperties = {
  maxWidth: 880,
  margin: "0 auto",
  padding: `${SPACING.xxl}px ${SPACING.xl}px`,
};

const H1: CSSProperties = {
  fontSize: 36,
  lineHeight: 1.25,
  marginTop: 0,
  marginBottom: SPACING.md,
  color: COLORS.textPrimary,
  fontWeight: 700,
};

const LEAD: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  marginTop: 0,
  marginBottom: SPACING.xl,
  maxWidth: 640,
};

const H2: CSSProperties = {
  fontSize: 26,
  lineHeight: 1.3,
  marginTop: 0,
  marginBottom: SPACING.lg,
  color: COLORS.textPrimary,
  fontWeight: 600,
};

const H3: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
  fontWeight: 600,
};

const PRIMARY_BTN: CSSProperties = {
  display: "inline-block",
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.xl}px`,
  backgroundColor: COLORS.accentDesatGreen,
  color: COLORS.surface,
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  textDecoration: "none",
};

const SECONDARY_BTN: CSSProperties = {
  display: "inline-block",
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  textDecoration: "none",
};

const TEXT_LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  fontSize: TYPOGRAPHY.bodySizePx,
};

const CARD_ROW: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: SPACING.lg,
};

const CARD: CSSProperties = {
  backgroundColor: COLORS.surface,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
  flex: "1 1 220px",
  boxSizing: "border-box",
};

const DIVIDER: CSSProperties = {
  border: "none",
  borderTop: `1px solid ${COLORS.disabled}`,
  margin: 0,
};

const LIST: CSSProperties = {
  margin: 0,
  paddingLeft: SPACING.lg,
};

const FOOTER: CSSProperties = {
  borderTop: `1px solid ${COLORS.disabled}`,
  padding: `${SPACING.xl}px`,
  display: "flex",
  justifyContent: "space-between",
  flexWrap: "wrap",
  gap: SPACING.md,
  backgroundColor: COLORS.surface,
  fontSize: TYPOGRAPHY.bodySizePx,
};

// ---- Sources (best practice: inline attribution AND a linked list) ----------

const SOURCES = [
  {
    name: "Pew Research Center — How Americans' opinions and use of AI differ by age (2026)",
    url: "https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-use-of-ai-differ-by-age/",
    why: "AI chatbot adoption: 57% under-50 vs. 28% ages 50+; 65+ the most uncertain group.",
  },
  {
    name: "Nielsen Norman Group — Usability for Senior Citizens",
    url: "https://www.nngroup.com/articles/usability-seniors-improvements/",
    why: "Adults 65+ succeed at website tasks 55% vs. 75% for ages 21–55, ~43% slower.",
  },
  {
    name: "W3C Web Accessibility Initiative — Web Accessibility for Older Users: A Literature Review",
    url: "https://www.w3.org/WAI/older-users/literature/",
    why: "Ageing vision: ~80% contrast-sensitivity loss by age 80; presbyopia; colour-shift.",
  },
  {
    name: "Owsley C. — Vision and Aging, Annual Review of Vision Science (UAB School of Medicine)",
    url: "https://www.annualreviews.org/content/journals/10.1146/annurev-vision-111815-114550",
    why: "Contrast sensitivity and visual-processing-speed decline in later life.",
  },
  {
    name: "Hasher L. & Zacks R.T. — Working memory, comprehension, and aging (University of Toronto)",
    url: "https://hasherlab.psych.utoronto.ca/abstracts/hasher_zacks_88.htm",
    why: "Aging reduces inhibition of irrelevant information — visual distraction harms learning.",
  },
  {
    name: "JMIR (2025) — Cognitive load and learning performance in digital health education for older patients",
    url: "https://www.jmir.org/2025/1/e79430",
    why: "Cognitive load is the key mediator of digital-learning outcomes (large effect).",
  },
  {
    name: "Laganà L. et al. — Enhancing computer self-efficacy in older adults: a randomised controlled study",
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/",
    why: "Age-appropriate training significantly improves attitudes and self-efficacy.",
  },
];

const OUTCOMES = [
  {
    title: "A thoughtful gift",
    body: "You are giving access to calm, self-paced AI learning designed for adults 55+ — not another gadget or subscription to manage.",
  },
  {
    title: "Confidence without pressure",
    body: "The recipient moves at their own pace with plain-language explanations. There are no tests, grades, or time limits.",
  },
  {
    title: "You stay in control",
    body: "You pay once and we email the gift code to you. The recipient redeems it whenever they are ready — nothing is auto-applied.",
  },
];

const STEPS = [
  "Choose the gift — you do not need an account.",
  "Enter your email and complete the secure checkout.",
  "We send the gift code to you; share it whenever you like.",
];

const INCLUDES = [
  "A guided AI curriculum written in plain language for adults 55+",
  "A calm, self-paced interface — no tests, grades, or time pressure",
  "The recipient redeems the gift code in their own account",
  "Support from a real person if either of you needs help",
];

// ---- Page -------------------------------------------------------------------

export default function CaregiverPage() {
  return (
    <div style={PAGE} data-contract-exemption="marketing.caregiver">
      {/* Marketing header — text links only, no dropdowns */}
      <header style={HEADER}>
        <Link
          to="/"
          style={{ textDecoration: "none", color: COLORS.textPrimary }}
          aria-label="mynaani home"
        >
          <strong>mynaani</strong>
        </Link>
        <nav style={HEADER_NAV} aria-label="Caregiver">
          <a href="#caregiver-how" style={HEADER_LINK}>
            How it works
          </a>
          <a href="#caregiver-sources" style={HEADER_LINK}>
            Sources
          </a>
          <Link to="/for-communities" style={HEADER_LINK}>
            For senior facilities
          </Link>
          <Link to="/" style={HEADER_LINK}>
            For learners
          </Link>
          <Link to="/gift" style={HEADER_CTA} data-gift-entry="header">
            Gift mynaani
          </Link>
        </nav>
      </header>

      <main>
        {/* Hero */}
        <section style={SECTION} aria-labelledby="caregiver-hero">
          <h1 id="caregiver-hero" style={H1}>
            Give calm, self-paced AI learning to someone you care about
          </h1>
          <p style={LEAD}>
            Mynaani explains AI in plain language, one step at a time. It was
            designed for adults 55+ — readable type, predictable behaviour, and
            no pressure. As a caregiver, you can give access as a gift: you pay
            once, we send the gift code to your email, and the recipient redeems
            it whenever they are ready.
          </p>
          <div style={{ display: "flex", gap: SPACING.md, flexWrap: "wrap" }}>
            <Link to="/gift" style={PRIMARY_BTN} data-gift-entry="hero">
              Gift mynaani
            </Link>
            <a href="#caregiver-how" style={SECONDARY_BTN}>
              How gifting works
            </a>
          </div>
          <SupportContact />
          <ChatWidget journey="gift" />
        </section>

        <hr style={DIVIDER} />

        {/* Difference */}
        <section style={SECTION} aria-labelledby="caregiver-difference">
          <h2 id="caregiver-difference" style={H2}>
            Why this is a different kind of gift
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.lg, maxWidth: 640 }}>
            Most technology gifts ask the recipient to adapt to the tool.
            Mynaani was built the other way around: the interface, pacing, and
            explanations are designed for the way older adults actually see,
            process, and gain confidence. The result is a gift that supports
            independence rather than creating another thing to learn.
          </p>
          <div style={CARD_ROW}>
            {OUTCOMES.map((o) => (
              <div key={o.title} style={CARD}>
                <h3 style={H3}>{o.title}</h3>
                <p style={{ margin: 0 }}>{o.body}</p>
              </div>
            ))}
          </div>
        </section>

        <hr style={DIVIDER} />

        {/* How it works */}
        <section style={SECTION} aria-labelledby="caregiver-how">
          <h2 id="caregiver-how" style={H2}>
            How gifting works
          </h2>
          <ol style={{ ...LIST, maxWidth: 640 }}>
            {STEPS.map((s) => (
              <li key={s} style={{ marginBottom: SPACING.md }}>
                {s}
              </li>
            ))}
          </ol>
          <p style={{ marginTop: SPACING.lg, marginBottom: 0, maxWidth: 640 }}>
            The gift code is not time-limited. If the person you care about
            already has a mynaani account, they can redeem it there; if not,
            they can create a free account when they redeem.
          </p>
        </section>

        <hr style={DIVIDER} />

        {/* What the gift includes */}
        <section style={SECTION} aria-labelledby="caregiver-includes">
          <h2 id="caregiver-includes" style={H2}>
            What the gift includes
          </h2>
          <ul style={{ ...LIST, maxWidth: 640 }}>
            {INCLUDES.map((i) => (
              <li key={i} style={{ marginBottom: SPACING.md }}>
                {i}
              </li>
            ))}
          </ul>
        </section>

        <hr style={DIVIDER} />

        {/* Designed for the person you care about */}
        <section style={SECTION} aria-labelledby="caregiver-who">
          <h2 id="caregiver-who" style={H2}>
            Designed for the person you care about
          </h2>
          <p style={{ marginTop: 0, marginBottom: 0, maxWidth: 640 }}>
            Mynaani is built specifically for adults 55+ — not adapted for them.
            Our geragogy-centered curriculum and cognitively-protective
            interface were designed for older learners from the start: readable
            type, predictable behaviour, and an approach that respects
            experience rather than talking down to it.
          </p>
        </section>

        <hr style={DIVIDER} />

        {/* Insights / whitepapers */}
        <section style={SECTION} aria-labelledby="caregiver-papers">
          <h2 id="caregiver-papers" style={H2}>
            Insights — research briefs you can share
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.lg, maxWidth: 640 }}>
            Two short, fully-referenced papers you can read or share with the
            person you are thinking about:
          </p>
          <div style={CARD_ROW}>
            <div style={CARD}>
              <h3 style={H3}>The AI Gap</h3>
              <p style={{ margin: `0 0 ${SPACING.md}px` }}>
                Who AI is leaving behind, what it costs in health access and
                fraud exposure — and why the gap is a design failure, not an
                ability one. 17 sources.
              </p>
              <a
                href="/whitepapers/the-ai-gap.pdf"
                target="_blank"
                rel="noopener noreferrer"
                style={SECONDARY_BTN}
              >
                Download the PDF
              </a>
            </div>
            <div style={CARD}>
              <h3 style={H3}>
                Geragogy — the key to learning for the aging population
              </h3>
              <p style={{ margin: `0 0 ${SPACING.md}px` }}>
                The science of how older adults learn, what standard design gets
                wrong, and the method mynaani is built on. 16 sources.
              </p>
              <a
                href="/whitepapers/geragogy-the-key-to-learning.pdf"
                target="_blank"
                rel="noopener noreferrer"
                style={SECONDARY_BTN}
              >
                Download the PDF
              </a>
            </div>
          </div>
          <div
            style={{
              marginTop: SPACING.xl,
              backgroundColor: COLORS.surface,
              borderRadius: RADIUS.lg,
              padding: SPACING.lg,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: SPACING.md,
            }}
          >
            <p style={{ margin: 0, maxWidth: 440 }}>
              <strong>Get research updates.</strong> New briefs as they are
              published — occasional, evidence-first, no noise.
            </p>
            <a href={UPDATES_MAILTO} style={SECONDARY_BTN}>
              Email us to join the list
            </a>
          </div>
        </section>

        <hr style={DIVIDER} />

        {/* Gift options */}
        <section style={SECTION} aria-labelledby="caregiver-gift">
          <h2 id="caregiver-gift" style={H2}>
            Gift options
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.lg, maxWidth: 640 }}>
            The gift covers the paid curriculum modules. It is a one-time
            purchase, not a subscription — the recipient will not be charged
            again. Checkout happens on Stripe's secure payment page; your card
            details never reach our system.
          </p>
          <div style={{ display: "flex", gap: SPACING.md, flexWrap: "wrap" }}>
            <Link to="/gift" style={PRIMARY_BTN} data-gift-entry="section">
              Gift mynaani
            </Link>
            <a href={MAILTO} style={SECONDARY_BTN}>
              Ask a question first
            </a>
          </div>
          <p style={{ marginTop: SPACING.lg, marginBottom: 0, maxWidth: 640 }}>
            <strong>Working with a senior living community?</strong> If you are
            exploring mynaani for a group rather than one person, see{" "}
            <Link to="/for-communities" style={TEXT_LINK}>
              our community program
            </Link>
            .
          </p>
        </section>

        <hr style={DIVIDER} />

        {/* Contact */}
        <section style={SECTION} aria-labelledby="caregiver-contact">
          <h2 id="caregiver-contact" style={H2}>
            Questions before you give
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.lg, maxWidth: 640 }}>
            If you want to check whether mynaani is the right fit, or you need
            help with a gift code, email us. A real person answers — usually
            within one business day.
          </p>
          <a href={MAILTO} style={PRIMARY_BTN}>
            Email {CONTACT}
          </a>
        </section>

        <hr style={DIVIDER} />

        {/* Sources */}
        <section style={SECTION} aria-labelledby="caregiver-sources">
          <h2 id="caregiver-sources" style={H2}>
            Sources
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.lg, maxWidth: 640 }}>
            The design and research claims on this page are grounded in the
            following published sources:
          </p>
          <ul style={{ ...LIST, maxWidth: 760 }}>
            {SOURCES.map((s) => (
              <li key={s.url} style={{ marginBottom: SPACING.lg }}>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={TEXT_LINK}
                >
                  {s.name}
                </a>
                <p
                  style={{
                    margin: `${SPACING.xs}px 0 0`,
                    color: COLORS.textPrimary,
                  }}
                >
                  {s.why}
                </p>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer style={FOOTER}>
        <span>mynaani — AI learning for adults 55+</span>
        <span>
          <Link to="/" style={TEXT_LINK}>
            For learners
          </Link>{" "}
          <Link to="/for-communities" style={TEXT_LINK}>
            For senior facilities
          </Link>
        </span>
      </footer>
    </div>
  );
}
