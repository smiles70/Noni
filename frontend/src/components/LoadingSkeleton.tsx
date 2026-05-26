/**
 * Sprint 28-B.8: Loading state for lazy-loaded views.
 *
 * Contract-compliant pending indicator (CONTRACT Section I.D #10 —
 * PendingBanner pattern). Uses ONLY palette tokens. No animation, no
 * pulse, no attention-drawing motion (CONTRACT Section I.G + VII —
 * spatial stability over loading affordance).
 *
 * State transparency (CONTRACT Section III): explicit pending label
 * via aria-live + visible text. No alarmist phrasing.
 */

import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";

const block: React.CSSProperties = {
  backgroundColor: COLORS.surface,
  borderRadius: RADIUS.sm,
};

const LoadingSkeleton: React.FC = () => (
  <main
    aria-live="polite"
    aria-busy="true"
    data-component="PendingBanner"
    style={{
      padding: SPACING.lg,
      maxWidth: 720,
      margin: "0 auto",
      display: "flex",
      flexDirection: "column",
      gap: SPACING.md,
      fontFamily: TYPOGRAPHY.fontFamily,
      color: COLORS.textPrimary,
    }}
  >
    <p style={{ fontSize: TYPOGRAPHY.bodySizePx, margin: 0 }}>
      One moment — loading.
    </p>
    <div style={{ ...block, height: SPACING.xl, width: "60%" }} aria-hidden="true" />
    <div style={{ ...block, height: SPACING.md, width: "100%" }} aria-hidden="true" />
    <div style={{ ...block, height: SPACING.md, width: "90%" }} aria-hidden="true" />
    <div style={{ ...block, height: SPACING.md, width: "95%" }} aria-hidden="true" />
  </main>
);

export default LoadingSkeleton;
