/**
 * Calm support-contact line (intake 013 / research
 * 2026-09-12-phone-number-placement). Mounted on gift + facility
 * journey surfaces only — never on the learner curriculum.
 * tel: link uses E.164; visible text is the number itself (WCAG 2.4.4).
 * AI-answered disclosure travels with the number everywhere.
 */
import { CSSProperties } from "react";
import { COLORS, MARKETING, SPACING, TYPOGRAPHY } from "../design/tokens";

const BODY: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  color: COLORS.textPrimary,
  marginTop: SPACING.lg,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "underline",
};

// ADR-0034 dark-surface tones (bid-17 marketing bands): AA on charcoal.
const BODY_DARK: CSSProperties = { ...BODY, color: MARKETING.bodyOnDark };
const LINK_DARK: CSSProperties = {
  ...LINK,
  color: MARKETING.tealBright,
};

interface Props {
  /** "dark" renders on charcoal marketing surfaces (PS-BID17-003). */
  tone?: "light" | "dark";
}

export default function SupportContact({ tone }: Props) {
  const dark = tone === "dark";
  return (
    <p style={dark ? BODY_DARK : BODY}>
      Questions? Call{" "}
      <a
        href="tel:+18774094144"
        style={dark ? LINK_DARK : LINK}
        aria-label="Call MyNaani support, toll free, 1 8 7 7, 4 0 9, 4 1 4 4"
      >
        1 (877) 409-4144
      </a>{" "}
      — toll-free, answered by our AI assistant — or email{" "}
      <a href="mailto:help@mynaani.com" style={dark ? LINK_DARK : LINK}>
        help@mynaani.com
      </a>
      .
    </p>
  );
}
