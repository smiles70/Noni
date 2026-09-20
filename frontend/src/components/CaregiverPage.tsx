/**
 * CaregiverPage — marketing surface for adult children, family members,
 * and caregivers who want to give mynaani as a gift.
 *
 * Bid-17 visual system (owner-approved 2026-09-19, ADR-0034): charcoal
 * nav/hero/CTA bands on MARKETING tokens, warm-paper reading sections.
 * Governed by ADR-0030 (Marketing Surfaces Annex), NOT the learner-facing
 * geragogy contract — but tone stays calm, WCAG AA holds, no claims are
 * invented. Every element is marked `data-contract-exemption=
 * "marketing.caregiver"` for audit.
 *
 * Preserved integrations (do not remove): ChatWidget journey="gift",
 * SupportContact, Footer currentPath="/caregiver", trackScrollDepth
 * ("caregiver"), data-gift-entry attributes, whitepaper links, and the
 * toll-free tel: line.
 */
import { CSSProperties, useEffect } from "react";
import { Link } from "react-router-dom";
import { COLORS, MARKETING, SPACING, TYPOGRAPHY } from "../design/tokens";
import ChatWidget from "./ChatWidget";
import SupportContact from "./SupportContact";
import Footer from "./Footer";
import { trackScrollDepth } from "../lib/scrollDepthTelemetry";

// ---- Tokenized styles (marketing annex, ADR-0034 dark palette) --------------

const PAGE: CSSProperties = {
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: MARKETING.paper,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  minHeight: "100vh",
};

const NAV: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: `14px ${SPACING.xl}px`,
  backgroundColor: MARKETING.charcoal,
};

const NAV_LINKS: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: SPACING.lg,
};

const NAV_LINK: CSSProperties = {
  color: MARKETING.mutedOnDark,
  textDecoration: "none",
  fontSize: 15,
  fontWeight: 500,
};

const NAV_CTA: CSSProperties = {
  color: MARKETING.charcoalDeep,
  backgroundColor: MARKETING.gold,
  padding: `11px ${SPACING.lg}px`,
  borderRadius: 24,
  fontWeight: 600,
  fontSize: 15,
  textDecoration: "none",
};

const HERO: CSSProperties = {
  background: `linear-gradient(150deg, ${MARKETING.charcoal} 0%, ${MARKETING.charcoalDeep} 100%)`,
  color: "#FFFFFF",
  padding: `76px ${SPACING.xl}px`,
};

const HERO_INNER: CSSProperties = {
  maxWidth: 1100,
  margin: "0 auto",
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
  gap: 56,
  alignItems: "center",
};

const KICKER: CSSProperties = {
  fontSize: 13,
  fontWeight: 700,
  letterSpacing: 2.5,
  textTransform: "uppercase",
  color: MARKETING.tealBright,
};

const H1_DARK: CSSProperties = {
  fontSize: 48,
  fontWeight: 700,
  lineHeight: 1.15,
  margin: `${SPACING.md}px 0 0`,
  color: "#FFFFFF",
};

const SUB_DARK: CSSProperties = {
  fontSize: 18,
  lineHeight: 1.7,
  color: "#D4D8DC",
  margin: `22px 0 34px`,
  maxWidth: 520,
};

const CTA_GOLD: CSSProperties = {
  display: "inline-block",
  backgroundColor: MARKETING.gold,
  color: MARKETING.charcoalDeep,
  textDecoration: "none",
  padding: `${SPACING.md}px 36px`,
  borderRadius: 28,
  fontSize: TYPOGRAPHY.bodySizePx,
  fontWeight: 700,
};

const SUB_LINK_DARK: CSSProperties = {
  display: "inline-block",
  color: MARKETING.mutedOnDark,
  fontSize: 15,
  marginLeft: 20,
};

const STORY_CARD: CSSProperties = {
  background: "rgba(255,255,255,0.07)",
  border: "1px solid rgba(255,255,255,0.18)",
  borderRadius: 16,
  padding: 30,
};

const SECTION: CSSProperties = {
  maxWidth: 1100,
  margin: "0 auto",
  padding: `66px ${SPACING.xl}px`,
};

const KICKER_LIGHT: CSSProperties = {
  ...KICKER,
  color: "#1F6357",
};

const H2_LIGHT: CSSProperties = {
  fontSize: 34,
  fontWeight: 700,
  lineHeight: 1.25,
  margin: "10px 0 18px",
  color: MARKETING.charcoal,
};

const PROOF_GRID: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
  gap: 18,
  marginTop: 36,
};

const PROOF_CARD: CSSProperties = {
  background: "#FFFFFF",
  border: "1px solid #E2E0D8",
  borderRadius: 12,
  padding: SPACING.lg,
};

const PROOF_NUM: CSSProperties = {
  fontSize: 36,
  fontWeight: 800,
  color: MARKETING.charcoal,
};

const PROOF_LABEL: CSSProperties = {
  fontSize: 13,
  fontWeight: 700,
  color: COLORS.textPrimary,
  marginTop: 6,
};

const PROOF_BODY: CSSProperties = {
  fontSize: 13,
  color: "#7A7568",
  marginTop: 8,
  lineHeight: 1.55,
};

const OBJECTION: CSSProperties = {
  background: "#FFFFFF",
  border: "1px solid #E2E0D8",
  borderRadius: 14,
  padding: 36,
  marginTop: 32,
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
  gap: 40,
};

const DARK_SECTION: CSSProperties = {
  background: MARKETING.charcoalDeep,
};

const BIZ_GRID: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
  gap: 18,
  marginTop: 32,
};

const BIZ_CARD: CSSProperties = {
  background: "rgba(255,255,255,0.06)",
  border: "1px solid #3A3E43",
  borderRadius: 12,
  padding: 26,
  color: "#FFFFFF",
};

const CTA_BAND: CSSProperties = {
  background: MARKETING.charcoal,
  color: "#FFFFFF",
  textAlign: "center",
  padding: `80px ${SPACING.xl}px`,
};

const LINK_TEAL: CSSProperties = {
  color: "#1F6357",
  fontWeight: 600,
};

const LINK_TEAL_DARK: CSSProperties = {
  color: MARKETING.tealBright,
  fontWeight: 600,
};

// ---- Content ----------------------------------------------------------------

const PROOFS = [
  {
    n: "11+",
    u: "hrs/week on care coordination",
    p: "Nearly 4 in 10 family caregivers — Caregiver Action Network, 2026. This is the load you're already carrying.",
  },
  {
    n: "57→28",
    u: "% AI adoption, under-50 vs 50+",
    p: "Pew Research, 2026 — they're being left behind by design, not ability.",
  },
  {
    n: "55→75",
    u: "% task success, 65+ vs younger",
    p: "Nielsen Norman Group — standard design fails them; ours was built around why.",
  },
  {
    n: "0",
    u: "tech-support calls required",
    p: "Self-guided lessons plus a named human contact — you're off the hook.",
  },
  {
    n: "RCT",
    u: "evidence training works",
    p: "Age-appropriate training improves self-efficacy — the strongest predictor of persistence (Laganà et al.).",
  },
];

const BIZ = [
  {
    cat: "For them",
    title: "A real skill, not a babysitter app",
    p: "They learn to actually use AI — asking questions, getting help, video-calling grandkids — on their own terms.",
  },
  {
    cat: "For you",
    title: "You get to be family",
    p: "Calmer phone calls, fewer \u201cwhat is this?\u201d moments — you're the daughter, the son, the friend, not the help desk.",
  },
];

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

// ---- Page -------------------------------------------------------------------

export default function CaregiverPage() {
  // WS-D: scroll-depth baseline (milestones only, silent failure).
  useEffect(() => trackScrollDepth("caregiver"), []);
  return (
    <div style={PAGE} data-contract-exemption="marketing.caregiver">
      <nav style={NAV} aria-label="Caregiver">
        <Link
          to="/"
          aria-label="mynaani home"
          style={{ display: "flex", alignItems: "center" }}
        >
          <img
            src="/mynaani-icon-linework-dark.svg"
            alt="mynaani"
            height={56}
            style={{ display: "block", height: 56, width: "auto" }}
          />
        </Link>
        <div style={NAV_LINKS}>
          <a href="#why" style={NAV_LINK}>
            Why it works
          </a>
          <a href="#worry" style={NAV_LINK}>
            The worry
          </a>
          <a href="#gift" style={NAV_LINK}>
            Give a gift
          </a>
          <a href="#contact" style={NAV_CTA}>
            Start a conversation
          </a>
        </div>
      </nav>

      <main>
        <header style={HERO}>
          <div style={HERO_INNER}>
            <div>
              <span style={KICKER}>
                AI learning for your parent or loved one
              </span>
              <h1 style={H1_DARK}>
                They learn AI.{" "}
                <span style={{ color: MARKETING.tealBright }}>
                  You stop being tech support.
                </span>
              </h1>
              <p style={SUB_DARK}>
                Mynaani is AI learning built for the way older adults learn —
                self-guided, self-paced, staffed by us. They gain real
                confidence; you get a better phone call.
              </p>
              <a href="#contact" style={CTA_GOLD}>
                Start a conversation
              </a>
              <Link to="/" style={SUB_LINK_DARK}>
                See the learner experience →
              </Link>
              <div style={{ marginTop: SPACING.lg }}>
                <Link
                  to="/gift"
                  style={{
                    ...SUB_LINK_DARK,
                    fontWeight: 700,
                    marginLeft: 0,
                    display: "block",
                  }}
                  data-gift-entry="hero"
                >
                  Gift mynaani →
                </Link>
              </div>
              <div style={{ marginTop: SPACING.lg }}>
                <SupportContact />
                <ChatWidget journey="gift" />
              </div>
            </div>
            <div style={STORY_CARD}>
              <span style={{ ...KICKER, fontSize: 12 }}>
                Why it matters, in one sentence
              </span>
              <p
                style={{
                  fontSize: 17,
                  fontStyle: "italic",
                  lineHeight: 1.7,
                  color: "#EEF0F2",
                  marginTop: 14,
                }}
              >
                &ldquo;My mom learned to video-call her grandson by herself.
                That&rsquo;s the moment that changed our calls.&rdquo;
              </p>
              <p
                style={{
                  fontSize: 13,
                  color: MARKETING.mutedOnDark,
                  marginTop: 16,
                }}
              >
                — the kind of moment Mynaani exists to make more of
              </p>
            </div>
          </div>
        </header>

        <section style={SECTION} id="why" aria-labelledby="cg-evidence">
          <span style={KICKER_LIGHT}>The evidence behind the moment</span>
          <h2 id="cg-evidence" style={H2_LIGHT}>
            Warm on the surface, rigorous underneath.
          </h2>
          <div style={PROOF_GRID}>
            {PROOFS.map((c) => (
              <div key={c.u} style={PROOF_CARD}>
                <div style={PROOF_NUM}>{c.n}</div>
                <div style={PROOF_LABEL}>{c.u}</div>
                <p style={PROOF_BODY}>{c.p}</p>
              </div>
            ))}
          </div>
          <div style={OBJECTION} id="worry">
            <div>
              <span style={KICKER_LIGHT}>The worry this page must resolve</span>
              <blockquote
                style={{
                  fontSize: 22,
                  fontStyle: "italic",
                  lineHeight: 1.5,
                  color: MARKETING.charcoalDeep,
                  margin: "14px 0 0",
                }}
              >
                &ldquo;She&rsquo;ll get frustrated, feel stupid, and quit — like
                every other time we&rsquo;ve tried.&rdquo;
              </blockquote>
            </div>
            <div>
              <h3
                style={{
                  fontSize: 13,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                  color: "#1F6357",
                  marginTop: 0,
                  marginBottom: 10,
                }}
              >
                Why this time is different
              </h3>
              <p
                style={{
                  fontSize: 15,
                  lineHeight: 1.65,
                  color: MARKETING.inkSoft,
                  margin: 0,
                }}
              >
                Frustration comes from interfaces that punish mistakes.
                Mynaani&rsquo;s geragogy-centered, patent-pending,
                cognitively-protective system keeps every screen stable and
                predictable — nothing jumps, nothing competes for attention,
                every step reversible. Confidence is protected by design, not
                luck.
              </p>
            </div>
          </div>
        </section>

        <section style={DARK_SECTION} id="gift">
          <div style={SECTION}>
            <span style={KICKER}>Give mynaani</span>
            <h2 style={{ ...H2_LIGHT, color: "#FFFFFF" }}>
              The gift of staying capable.
            </h2>
            <div style={BIZ_GRID}>
              {BIZ.map((b) => (
                <div key={b.title} style={BIZ_CARD}>
                  <span
                    style={{
                      fontSize: 12,
                      letterSpacing: 1.5,
                      textTransform: "uppercase",
                      color: MARKETING.gold,
                      fontWeight: 700,
                    }}
                  >
                    {b.cat}
                  </span>
                  <h3 style={{ fontSize: 19, margin: "10px 0" }}>{b.title}</h3>
                  <p
                    style={{
                      fontSize: 14,
                      color: "#D4D8DC",
                      lineHeight: 1.6,
                      margin: 0,
                    }}
                  >
                    {b.p}
                  </p>
                </div>
              ))}
              <div style={BIZ_CARD}>
                <span
                  style={{
                    fontSize: 12,
                    letterSpacing: 1.5,
                    textTransform: "uppercase",
                    color: MARKETING.gold,
                    fontWeight: 700,
                  }}
                >
                  The proof
                </span>
                <h3 style={{ fontSize: 19, margin: "10px 0" }}>
                  Read the research first
                </h3>
                <p
                  style={{
                    fontSize: 14,
                    color: "#D4D8DC",
                    lineHeight: 1.6,
                    margin: 0,
                  }}
                >
                  Two fully-referenced briefs written for caregivers —
                  &ldquo;Cognitive Engagement&rdquo; and &ldquo;Geragogy for
                  Caregivers&rdquo; — free to read before you decide.{" "}
                  <a href="#research" style={LINK_TEAL_DARK}>
                    Download →
                  </a>
                </p>
              </div>
            </div>
            <div style={{ marginTop: 28 }}>
              <Link
                to="/gift"
                style={{ ...CTA_GOLD, display: "inline-block" }}
                data-gift-entry="gift-section"
              >
                Gift mynaani
              </Link>
            </div>
          </div>
        </section>

        <section style={SECTION} id="research" aria-labelledby="cg-research">
          <span style={KICKER_LIGHT}>Read the research before you decide</span>
          <h2 id="cg-research" style={H2_LIGHT}>
            Two briefs written for caregivers. Free.
          </h2>
          <div style={PROOF_GRID}>
            <div style={PROOF_CARD}>
              <div style={PROOF_NUM}>10</div>
              <div style={PROOF_LABEL}>
                sources — &ldquo;Cognitive Engagement&rdquo;
              </div>
              <p style={PROOF_BODY}>
                Why mentally stimulating activities matter in later life, what
                the research shows, and how caregivers can support them.{" "}
                <a
                  href="/whitepapers/cognitive-engagement.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={LINK_TEAL}
                >
                  Download the brief →
                </a>
              </p>
            </div>
            <div style={PROOF_CARD}>
              <div style={PROOF_NUM}>12</div>
              <div style={PROOF_LABEL}>
                sources — &ldquo;Geragogy for Caregivers&rdquo;
              </div>
              <p style={PROOF_BODY}>
                The science of helping an older adult learn, the four changes
                aging makes, and how to support without becoming the help desk.{" "}
                <a
                  href="/whitepapers/geragogy-for-caregivers.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={LINK_TEAL}
                >
                  Download the brief →
                </a>
              </p>
            </div>
            <div style={{ ...PROOF_CARD, padding: 0, overflow: "hidden" }}>
              <img
                src="/hero-mynaani.jpg"
                alt="The actual mynaani learner experience"
                style={{
                  width: "100%",
                  height: 120,
                  objectFit: "cover",
                  objectPosition: "center 20%",
                  display: "block",
                }}
              />
              <div style={{ padding: "14px 18px" }}>
                <div style={PROOF_LABEL}>The real product, not a mockup</div>
                <p style={PROOF_BODY}>
                  Judge the actual interface your loved one would use.{" "}
                  <Link to="/" style={LINK_TEAL}>
                    See the learner experience →
                  </Link>
                </p>
              </div>
            </div>
            <div style={PROOF_CARD}>
              <div style={PROOF_NUM}>1</div>
              <div style={PROOF_LABEL}>business day</div>
              <p style={PROOF_BODY}>
                Questions about giving it? A person answers within one business
                day — same day for anything urgent.
              </p>
            </div>
          </div>
        </section>

        <div style={CTA_BAND} id="contact">
          <h2 style={{ ...H2_LIGHT, color: "#FFFFFF", marginTop: 0 }}>
            Start a conversation
          </h2>
          <p
            style={{
              color: "#D4D8DC",
              maxWidth: 560,
              margin: "0 auto 32px",
              fontSize: 17,
              lineHeight: 1.6,
            }}
          >
            Questions before you decide — or ready to give it? A person answers
            within one business day, same day for anything urgent.
          </p>
          <Link to="/contact" style={CTA_GOLD}>
            Start a conversation
          </Link>
          <a
            href="tel:+18774094144"
            style={{
              display: "block",
              color: MARKETING.tealBright,
              fontSize: 20,
              fontWeight: 700,
              marginTop: 18,
              textDecoration: "none",
            }}
          >
            1 (877) 409-4144
          </a>
          <p
            style={{
              marginTop: 20,
              fontSize: 14,
              color: MARKETING.mutedOnDark,
            }}
          >
            Working with a senior living community?{" "}
            <Link to="/for-communities" style={LINK_TEAL_DARK}>
              See our community program
            </Link>
            {" · "}Ready to give it?{" "}
            <Link
              to="/gift"
              style={LINK_TEAL_DARK}
              data-gift-entry="footer-cta"
            >
              Gift mynaani →
            </Link>
          </p>
        </div>
        <section
          style={{ ...SECTION, paddingTop: 32, paddingBottom: 40 }}
          aria-labelledby="cg-sources"
        >
          <h2
            id="cg-sources"
            style={{
              fontSize: 13,
              letterSpacing: 1.5,
              textTransform: "uppercase",
              color: "#8A8577",
              fontWeight: 700,
            }}
          >
            Sources
          </h2>
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              margin: "14px 0 0",
              fontSize: 13,
              color: "#6B6759",
              lineHeight: 1.7,
            }}
          >
            {SOURCES.map((s) => (
              <li key={s.url} style={{ marginBottom: SPACING.md }}>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={LINK_TEAL}
                >
                  {s.name}
                </a>
                <br />
                {s.why}
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
