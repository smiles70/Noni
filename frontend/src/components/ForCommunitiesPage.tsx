/**
 * ForCommunitiesPage — B2B marketing surface for senior living communities
 * and similar institutions (B2B-LANDING-001 / B2B-DESIGN-001).
 *
 * Bid-17 visual system (owner-approved 2026-09-19, ADR-0034): charcoal
 * nav/hero/CTA bands on MARKETING tokens, warm-paper reading sections.
 * Governed by ADR-0030 (Marketing Surfaces Annex) — buyer-facing register,
 * WCAG AA, no invented claims. Marked `data-contract-exemption=
 * "marketing.b2b"` for audit.
 *
 * Preserved integrations (do not remove): ChatWidget journey="facility",
 * SupportContact, Footer currentPath="/for-communities",
 * trackScrollDepth("for-communities"), toll-free tel: line, /partners
 * inquiry routing, founding-partner pricing table, whitepaper links.
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

const KICKER_LIGHT: CSSProperties = {
  ...KICKER,
  color: "#1F6357",
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

const TH: CSSProperties = {
  textAlign: "left",
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  borderBottom: "2px solid #E2E0D8",
  fontWeight: 700,
  fontSize: 13,
  color: MARKETING.charcoal,
};

const TD: CSSProperties = {
  padding: `14px ${SPACING.md}px`,
  borderBottom: "1px solid #E2E0D8",
  fontSize: 14,
  color: MARKETING.inkSoft,
};

// ---- Content ----------------------------------------------------------------

const PROOFS = [
  {
    n: "57→28",
    u: "% AI adoption, under-50 vs 50+",
    p: "Pew Research, 2026 — the gap is a design failure, not an ability failure. Your residents are being left behind.",
  },
  {
    n: "80%",
    u: "contrast-sensitivity loss by 80",
    p: "W3C/WAI literature review — small type and visual clutter don't just look busy, they disappear.",
  },
  {
    n: "55→75",
    u: "% task success, 65+ vs younger",
    p: "Nielsen Norman Group — standard sites measurably fail older users; geragogy-centered design answers why.",
  },
  {
    n: "0",
    u: "staff hours required",
    p: "Self-guided lessons plus a named human contact — your team is not asked to become tech trainers.",
  },
  {
    n: "RCT",
    u: "evidence training works",
    p: "Age-appropriate training improves self-efficacy — the strongest predictor of persistence (Laganà et al.).",
  },
];

const BIZ = [
  {
    cat: "Occupancy",
    title: "A differentiator families notice",
    p: "Programming that helps residents stay connected and independent is the kind of proof families weigh on tours and in renewals.",
  },
  {
    cat: "Staff leverage",
    title: "Program, not a workload",
    p: "Residents learn at their own pace in a self-guided curriculum — staff gain a benefit to offer, not a curriculum to run.",
  },
  {
    cat: "The proof",
    title: "Read the research first",
    p: "Two fully-referenced briefs written for boards and EDs — free to download before you commit to anything. \u00a0Download below →",
  },
];

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

// ---- Page -------------------------------------------------------------------

export default function ForCommunitiesPage() {
  // WS-D: scroll-depth baseline (milestones only, silent failure).
  useEffect(() => trackScrollDepth("for-communities"), []);
  return (
    <div style={PAGE} data-contract-exemption="marketing.b2b">
      <nav style={NAV} aria-label="Marketing">
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
        <div style={{ display: "flex", alignItems: "center", gap: SPACING.lg }}>
          <a href="#case" style={NAV_LINK}>
            The case
          </a>
          <a href="#pricing" style={NAV_LINK}>
            Pricing
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
                For senior living owners, operators, and EDs
              </span>
              <h1 style={H1_DARK}>
                AI learning your residents actually finish.{" "}
                <span style={{ color: MARKETING.tealBright }}>
                  Staff hours you never spend.
                </span>
              </h1>
              <p style={SUB_DARK}>
                Mynaani is a geragogy-centered AI curriculum built for adults
                55+ — self-guided, self-paced, staffed by us. Your residents
                gain real confidence; your team isn&rsquo;t asked to run the
                program.
              </p>
              <a href="#contact" style={CTA_GOLD}>
                Start a conversation
              </a>
              <Link to="/" style={SUB_LINK_DARK}>
                See the learner experience →
              </Link>
              <div style={{ marginTop: SPACING.lg }}>
                <SupportContact />
                <ChatWidget journey="facility" />
              </div>
            </div>
            <div style={STORY_CARD}>
              <span style={{ ...KICKER, fontSize: 12 }}>
                The outcome, in one line
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
                &ldquo;Residents video-call their grandkids on their own —
                that&rsquo;s the proof point families mention on tours.&rdquo;
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

        <section style={SECTION} id="case" aria-labelledby="b2b-evidence">
          <span style={KICKER_LIGHT}>The case, in numbers</span>
          <h2 id="b2b-evidence" style={H2_LIGHT}>
            Built on geragogy — the science of how older adults learn.
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
          <div style={OBJECTION}>
            <div>
              <span style={KICKER_LIGHT}>The objection we must answer</span>
              <blockquote
                style={{
                  fontSize: 22,
                  fontStyle: "italic",
                  lineHeight: 1.5,
                  color: MARKETING.charcoalDeep,
                  margin: "14px 0 0",
                }}
              >
                &ldquo;My residents won&rsquo;t use it — and my staff will end
                up running it.&rdquo;
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
                Why it lands anyway
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
                Mynaani&rsquo;s patent-pending, cognitively-protective system
                keeps every screen stable and predictable — nothing jumps,
                nothing competes for attention. Residents learn at their own
                pace; staff never become the help desk.
              </p>
            </div>
          </div>
        </section>

        <section style={DARK_SECTION}>
          <div style={SECTION}>
            <span style={KICKER}>The business case</span>
            <h2 style={{ ...H2_LIGHT, color: "#FFFFFF" }}>
              Program your residents finish. Budget you can defend.
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
            </div>
          </div>
        </section>

        <section style={SECTION} aria-labelledby="b2b-papers">
          <span style={KICKER_LIGHT}>Board-ready research</span>
          <h2 id="b2b-papers" style={H2_LIGHT}>
            Two briefs written for owners and EDs. Free.
          </h2>
          <div style={PROOF_GRID}>
            <div style={PROOF_CARD}>
              <div style={PROOF_NUM}>17</div>
              <div style={PROOF_LABEL}>sources — &ldquo;The AI Gap&rdquo;</div>
              <p style={PROOF_BODY}>
                Who AI is leaving behind, what it costs in health access and
                fraud exposure — and why the gap is a design failure, not an
                ability one.{" "}
                <a
                  href="/whitepapers/the-ai-gap.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={LINK_TEAL}
                >
                  Download the brief →
                </a>
              </p>
            </div>
            <div style={PROOF_CARD}>
              <div style={PROOF_NUM}>16</div>
              <div style={PROOF_LABEL}>
                sources — &ldquo;Geragogy — the key to learning&rdquo;
              </div>
              <p style={PROOF_BODY}>
                The science of how older adults learn, what standard design gets
                wrong, and the method mynaani is built on.{" "}
                <a
                  href="/whitepapers/geragogy-the-key-to-learning.pdf"
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
                  Judge the actual interface residents would use.{" "}
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
                Program partners hear back from a person within one business day
                — same day for anything urgent.
              </p>
            </div>
          </div>
        </section>

        <section style={SECTION} id="pricing" aria-labelledby="b2b-pricing">
          <span style={KICKER_LIGHT}>Pricing</span>
          <h2 id="b2b-pricing" style={H2_LIGHT}>
            Founding Partner rates
          </h2>
          <p
            style={{
              fontSize: 15,
              lineHeight: 1.65,
              color: MARKETING.inkSoft,
              maxWidth: 680,
              margin: "0 0 18px",
            }}
          >
            Annual site licensing, billed to your organization — never to your
            residents. <strong>Founding Partner rates</strong> for our pilot
            cohort, sized by community:
          </p>
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                background: "#FFFFFF",
                border: "1px solid #E2E0D8",
                borderRadius: 12,
              }}
            >
              <thead>
                <tr>
                  <th style={TH}>Community size</th>
                  <th style={TH}>Nonprofit site</th>
                  <th style={TH}>For-profit location</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={TD}>Up to 25 residents or members</td>
                  <td style={TD}>
                    <strong>$375 / year</strong>
                  </td>
                  <td style={TD}>
                    <strong>$850 / year</strong>
                  </td>
                </tr>
                <tr>
                  <td style={TD}>26–75</td>
                  <td style={TD}>
                    <strong>$550 / year</strong>
                  </td>
                  <td style={TD}>
                    <strong>$1,250 / year</strong>
                  </td>
                </tr>
                <tr>
                  <td style={TD}>76–150</td>
                  <td style={TD}>
                    <strong>$850 / year</strong>
                  </td>
                  <td style={TD}>
                    <strong>$1,950 / year</strong>
                  </td>
                </tr>
                <tr>
                  <td style={TD}>Multi-site, 150+, or health plans</td>
                  <td style={TD} colSpan={2}>
                    <strong>Custom</strong> — sized to your portfolio, including
                    digital-literacy benefit structures for plans
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p
            style={{
              fontSize: 13,
              color: "#6B6759",
              lineHeight: 1.6,
              margin: "14px 0 0",
              maxWidth: 680,
            }}
          >
            Every tier includes the full geragogy-centered curriculum, guided
            onboarding with no implementation fee, and staff materials. For
            honest context: institutional digital-literacy programs in this
            category typically run in the hundreds-to-low-thousands per site per
            year — we publish our numbers because we&rsquo;d want them if we
            were buying. Founding partners keep their rate for the term; rates
            are reviewed when the cohort closes.
          </p>
          <p
            style={{
              fontSize: 14,
              color: MARKETING.inkSoft,
              lineHeight: 1.65,
              marginTop: 18,
              maxWidth: 680,
            }}
          >
            <strong>Working with procurement?</strong> We hold learner names and
            progress — not health data, not clinical records. Onboarding is
            guided, no implementation fee, no IT lift. Founding-pilot terms are
            set together — we&rsquo;ll put every detail in writing before you
            commit. Multi-site pricing, security practices, vendor setup —{" "}
            <Link to="/partners" style={LINK_TEAL}>
              send us a note
            </Link>{" "}
            and a person will answer.
          </p>
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
            Tell us about your community and what your residents need —
            we&rsquo;ll arrange a conversation at a time that suits you. A
            person answers within one business day.
          </p>
          <Link to="/partners" style={CTA_GOLD}>
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
        </div>

        <section
          style={{ ...SECTION, paddingTop: 32, paddingBottom: 40 }}
          aria-labelledby="b2b-sources"
        >
          <h2
            id="b2b-sources"
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
      <Footer currentPath="/for-communities" />
    </div>
  );
}
