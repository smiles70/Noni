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
import { CSSProperties, useEffect } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../design/tokens";
import ChatWidget from "./ChatWidget";
import SupportContact from "./SupportContact";
import Footer from "./Footer";
import { trackScrollDepth } from "../lib/scrollDepthTelemetry";
import OnThisPage, { PageSection } from "./OnThisPage";

// Single source for the "On this page" menu — labels carry the real
// section scent (NN/g: link labels must name the destination).
const SECTIONS: PageSection[] = [
  { id: "caregiver-difference", label: "Why this gift" },
  { id: "caregiver-how", label: "How gifting works" },
  { id: "caregiver-includes", label: "What's included" },
  { id: "caregiver-who", label: "Who it's for" },
  { id: "caregiver-papers", label: "Research briefs" },
  { id: "caregiver-gift", label: "Gift options" },
  { id: "caregiver-contact", label: "Questions" },
  { id: "caregiver-sources", label: "Sources" },
];

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
  scrollMarginTop: SPACING.xl,
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

// WS-C: constrained to the content column — a full-bleed hairline reads
// as "page end" (Contentsquare false-bottom); an inset rule reads as a
// section pause.
const DIVIDER: CSSProperties = {
  border: "none",
  borderTop: `1px solid ${COLORS.disabled}`,
  margin: "0 auto",
  maxWidth: 880,
};

const LIST: CSSProperties = {
  margin: 0,
  paddingLeft: SPACING.lg,
};

// ---- Sources (best practice: inline attribution AND a linked list) ----------

const SOURCES = [
  {
    name: 'Tang X. et al. — "I Never Imagined Grandma Could Do So Well with Technology" (CSCW 2022)',
    url: "https://xinrutang.github.io/file/FamilyCSCW22/FamilyCSCW22.pdf",
    why: "Younger family members support older adults' technology learning over time as influencers, supporters, protectors, and monitors.",
  },
  {
    name: "Caregiver Action Network — CIC Caregiver Tech Insights Survey (2026)",
    url: "https://www.caregiveraction.org/wp-content/uploads/2026/05/CIC-Survey-2026.pdf",
    why: "90% of family caregivers already use digital tools; nearly four in ten spend 11 or more hours per week on care coordination.",
  },
  {
    name: "AARP / Age in Place Tech — 2025 Technology Trends: Older Adults and Caregiving",
    url: "https://www.ageinplacetech.com/files/aip/2025-technology-trends-older-adults-caregiving.doi_.10.26419-2fres.00891.007.pdf",
    why: "Adults 50+ who are caregivers adopt convenience and safety technology more often than non-caregivers.",
  },
  {
    name: "JMIR Aging — Application-based interventions for family caregivers of older adults: scoping review (2026)",
    url: "https://aging.jmir.org/2026/1/e76115",
    why: "Apps can improve caregiver well-being and burden, but the biggest gap is usable, well-evaluated design.",
  },
  {
    name: "SSPH+ / Frontiers in Public Health Reviews — Digital Informal Care: The Use of Technology in Family Care (2025)",
    url: "https://www.ssph-journal.org/journals/public-health-reviews/articles/10.3389/phrs.2025.1608872/full",
    why: "Digital tools can reduce caregiver burden and improve competence, but only when they are usable and accessible.",
  },
  {
    name: "Heliyon — The impact of family members on aging persons' technology use intentions (2025)",
    url: "https://doi.org/10.1016/j.heliyon.2025.e42252",
    why: "When family caregivers and older adults share the same belief about capability, technology use intention is highest.",
  },
  {
    name: "Laganà L. et al. — Enhancing computer self-efficacy in older adults: a randomised controlled study",
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/",
    why: "Age-appropriate, self-paced training significantly improves attitudes and self-efficacy in older learners.",
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
  // WS-D: scroll-depth baseline (milestones only, silent failure).
  useEffect(() => trackScrollDepth("caregiver"), []);
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

        <OnThisPage sections={SECTIONS} />

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
          {/* WS-B: same-goal gift CTA repeated at ~50% depth — most
              visitors never reach the bottom section. */}
          <p style={{ marginTop: SPACING.xl, marginBottom: 0 }}>
            <Link to="/gift" style={PRIMARY_BTN} data-gift-entry="midpage">
              Gift mynaani
            </Link>
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
              <h3 style={H3}>Cognitive Engagement</h3>
              <p style={{ margin: `0 0 ${SPACING.md}px` }}>
                Why mentally stimulating activities matter in later life, what
                the research shows, and how caregivers can support them. 10
                sources.
              </p>
              <a
                href="/whitepapers/cognitive-engagement.pdf"
                target="_blank"
                rel="noopener noreferrer"
                style={SECONDARY_BTN}
              >
                Download the PDF
              </a>
            </div>
            <div style={CARD}>
              <h3 style={H3}>Geragogy for Caregivers</h3>
              <p style={{ margin: `0 0 ${SPACING.md}px` }}>
                The science of helping an older adult learn, the four changes
                aging makes, and how to support without becoming the help desk.
                12 sources.
              </p>
              <a
                href="/whitepapers/geragogy-for-caregivers.pdf"
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
            <Link to="/contact" style={SECONDARY_BTN}>
              Request research updates
            </Link>
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
            <Link to="/contact" style={SECONDARY_BTN}>
              Ask a question first
            </Link>
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
          <Link to="/contact" style={PRIMARY_BTN}>
            Let&apos;s talk
          </Link>
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

      {/* MKT-FOOTER-001: shared fat footer — brand, doormat nav row,
          legal row (privacy/terms/copyright). Backend-served labels. */}
      <Footer currentPath="/caregiver" />
    </div>
  );
}
