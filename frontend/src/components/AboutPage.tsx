/**
 * About page — who mynaani is and why it exists.
 *
 * Public view (no auth required). Same visual language as /help and
 * /privacy: PAGE/H1/H2/BODY from AccountStyles, design tokens only.
 * Calm, plain-language, dignified — no urgency, no hype.
 */

import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import { BODY, DIVIDER, H1, H2, PAGE } from "./AccountStyles";

interface Props {
  onBack: () => void;
}

export default function AboutPage({ onBack }: Props) {
  return (
    <main style={PAGE}>
      <button
        type="button"
        onClick={onBack}
        style={BACK_BTN}
        aria-label="Go back"
      >
        ← Back
      </button>

      <h1 style={H1}>About mynaani</h1>

      <p style={BODY}>
        Mynaani helps adults learn to use AI — clearly, calmly, and at their own
        pace.
      </p>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>Why mynaani exists</h2>
        <div style={BODY}>
          <p>
            AI is showing up everywhere — in banking, in healthcare, in the
            tools families use every day. Most explanations are written for
            people who already work with technology. Mynaani was built for
            everyone else: a curriculum grounded in geragogy, the evidence-based
            science of how older adults learn.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>How it works</h2>
        <div style={BODY}>
          <p>
            Short lessons explain what AI is, what it can and cannot do, and how
            to use it safely — one calm step at a time. You can learn for
            yourself, receive mynaani as a gift from someone who cares about
            you, or take part through a senior center or community program.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>What we believe</h2>
        <div style={BODY}>
          <ul style={UL}>
            <li>Learning should never feel rushed or patronizing.</li>
            <li>
              Your information stays yours — we collect as little as possible.
            </li>
            <li>
              Technology should adapt to people, not the other way around.
            </li>
          </ul>
        </div>
      </section>

      <section>
        <h2 style={H2}>Where to go next</h2>
        <div style={BODY}>
          <ul style={UL}>
            <li>
              <Link to="/" style={LINK}>
                Start learning
              </Link>
            </li>
            <li>
              <Link to="/gift" style={LINK}>
                Give mynaani as a gift
              </Link>
            </li>
            <li>
              <Link to="/for-communities" style={LINK}>
                Partner with us — for senior centers and communities
              </Link>
            </li>
            <li>
              <Link to="/help" style={LINK}>
                Help and common questions
              </Link>
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}

const UL: CSSProperties = {
  paddingLeft: SPACING.lg,
  margin: `${SPACING.sm}px 0`,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
};

const BACK_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.xs}px ${SPACING.md}px`,
  minHeight: MIN_TOUCH_TARGET.mobile,
  marginBottom: SPACING.md,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
};
