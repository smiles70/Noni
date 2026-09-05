/**
 * ForCommunitiesPage — B2B marketing surface for senior living communities
 * and similar institutions (B2B-LANDING-001 / B2B-DESIGN-001).
 *
 * Governed by ADR-0030 (Marketing Surfaces Annex), NOT the learner-facing
 * geragogy contract: richer type scale, simple labelled icons, marketing
 * header/footer, and stat/outcome blocks are permitted here — but tone
 * stays calm, WCAG AA holds, and no claims are invented. Every element is
 * marked `data-contract-exemption="marketing.b2b"` for audit.
 *
 * Pattern source: candoootech.com/enterprise-services — outcome headline,
 * proof strip, program list, "why partner" blocks, single contact CTA.
 * Content is static (no envelope, no RenderGuard) per ADR-0030.
 */
import { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../design/tokens";

const CONTACT = "hello@mynaani.com";
const MAILTO = `mailto:${CONTACT}?subject=Community%20partnership%20inquiry`;

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
  padding: `${SPACING.md}px ${SPACING.xl}px`,
  backgroundColor: COLORS.surface,
  borderBottom: `1px solid ${COLORS.disabled}`,
};

const HEADER_LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  fontSize: TYPOGRAPHY.bodySizePx,
  marginLeft: SPACING.lg,
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

const TEXT_LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  fontSize: TYPOGRAPHY.bodySizePx,
  marginLeft: SPACING.lg,
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

const ICON: CSSProperties = {
  color: COLORS.accentMutedBlue,
  display: "block",
  marginBottom: SPACING.sm,
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

// ---- Simple labelled icons (annex permits icons beside text) ----------------

function Icon({ path }: { path: string }) {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={ICON}
    >
      <path d={path} />
    </svg>
  );
}

const OUTCOMES = [
  {
    icon: "M12 8v4l3 3M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
    title: "Save staff time",
    body: "Residents learn at their own pace in a calm, self-guided program — your team is not asked to become technology trainers.",
  },
  {
    icon: "M20 12a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM8.5 12.5l2.5 2.5 4.5-5",
    title: "Resident confidence, family reassurance",
    body: "Plain-language AI learning designed for adults 55+ helps residents stay connected and independent — outcomes families notice.",
  },
  {
    icon: "M12 2l2.9 6.3 6.6.7-4.9 4.5 1.4 6.5L12 16.7 6 20l1.4-6.5L2.5 9l6.6-.7Z",
    title: "A visible differentiator",
    body: "Offering a considered, age-appropriate AI program signals a community that invests in residents' independence.",
  },
];

const PROGRAM_INCLUDES = [
  "A guided AI curriculum written in plain language for adults 55+",
  "A calm, self-paced interface — no tests, grades, or time pressure",
  "Onboarding support for residents and a point of contact for your staff",
  "A pilot shaped with your community — we learn together what works",
];

// ---- Page -------------------------------------------------------------------

export default function ForCommunitiesPage() {
  return (
    <div style={PAGE} data-contract-exemption="marketing.b2b">
      <header style={HEADER}>
        <Link
          to="/"
          aria-label="mynaani home"
          style={{ display: "flex", alignItems: "center" }}
        >
          <img
            src="/mynaani-logo.webp"
            alt="mynaani"
            height={48}
            style={{ display: "block", height: 48, width: "auto" }}
          />
        </Link>
        <nav aria-label="Marketing">
          <Link to="/" style={HEADER_LINK}>
            For learners
          </Link>
          <a href={MAILTO} style={HEADER_LINK}>
            Contact
          </a>
        </nav>
      </header>

      <main>
        <section style={SECTION} aria-labelledby="b2b-hero">
          <h1 id="b2b-hero" style={H1}>
            AI learning for your community, without adding to your team's
            workload
          </h1>
          <p style={LEAD}>
            Mynaani gives residents a calm, plain-language way to understand and
            use AI — designed specifically for adults 55+, and delivered as a
            program your staff does not have to run.
          </p>
          <a href={MAILTO} style={PRIMARY_BTN}>
            Talk to us about a pilot
          </a>
          <Link to="/" style={TEXT_LINK}>
            See the learner experience
          </Link>
        </section>

        <hr style={DIVIDER} />

        <section style={SECTION} aria-labelledby="b2b-outcomes">
          <h2 id="b2b-outcomes" style={H2}>
            Why communities partner with mynaani
          </h2>
          <div style={CARD_ROW}>
            {OUTCOMES.map((o) => (
              <div key={o.title} style={CARD}>
                <Icon path={o.icon} />
                <h3 style={H3}>{o.title}</h3>
                <p style={{ margin: 0 }}>{o.body}</p>
              </div>
            ))}
          </div>
        </section>

        <hr style={DIVIDER} />

        <section style={SECTION} aria-labelledby="b2b-program">
          <h2 id="b2b-program" style={H2}>
            What a founding partnership includes
          </h2>
          <ul style={LIST}>
            {PROGRAM_INCLUDES.map((item) => (
              <li key={item} style={{ marginBottom: SPACING.sm }}>
                {item}
              </li>
            ))}
          </ul>
          <p style={{ marginTop: SPACING.lg, marginBottom: 0 }}>
            We are onboarding a small number of founding communities. Working
            with us now means the program is shaped around your residents' needs
            — and your community helps set the standard.
          </p>
        </section>

        <hr style={DIVIDER} />

        <section style={SECTION} aria-labelledby="b2b-who">
          <h2 id="b2b-who" style={H2}>
            Designed for the people you serve
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.md, maxWidth: 640 }}>
            Mynaani is built specifically for adults 55+: large, readable type;
            a calm, predictable interface; and an approach that respects
            experience rather than talking down to it. The same care your
            community brings to residents is designed into every screen.
          </p>
        </section>

        <hr style={DIVIDER} />

        <section style={SECTION} aria-labelledby="b2b-contact">
          <h2 id="b2b-contact" style={H2}>
            Start a conversation
          </h2>
          <p style={{ marginTop: 0, marginBottom: SPACING.lg, maxWidth: 640 }}>
            Tell us about your community and what your residents need — we'll
            arrange a conversation at a time that suits you.
          </p>
          <a href={MAILTO} style={PRIMARY_BTN}>
            Email {CONTACT}
          </a>
        </section>
      </main>

      <footer style={FOOTER}>
        <span>mynaani — AI learning for adults 55+</span>
        <span>
          <Link to="/" style={{ ...HEADER_LINK, marginLeft: 0 }}>
            For learners
          </Link>
        </span>
      </footer>
    </div>
  );
}
