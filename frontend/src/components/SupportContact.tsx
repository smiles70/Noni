/**
 * Calm support-contact line (intake 013 / research
 * 2026-09-12-phone-number-placement). Mounted on gift + facility
 * journey surfaces only — never on the learner curriculum.
 * tel: link uses E.164; visible text is the number itself (WCAG 2.4.4).
 * AI-answered disclosure travels with the number everywhere.
 */
import { CSSProperties } from "react";
import { COLORS, SPACING, TYPOGRAPHY } from "../design/tokens";

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

export default function SupportContact() {
  return (
    <p style={BODY}>
      Questions? Call{" "}
      <a
        href="tel:+18774094144"
        style={LINK}
        aria-label="Call MyNaani support, toll free, 1 8 7 7, 4 0 9, 4 1 4 4"
      >
        1 (877) 409-4144
      </a>{" "}
      — toll-free, answered by our AI assistant — or email{" "}
      <a href="mailto:help@mynaani.com" style={LINK}>
        help@mynaani.com
      </a>
      .
    </p>
  );
}
