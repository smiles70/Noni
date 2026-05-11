/**
 * Shared tokenized style objects for account/billing pages (Sprint A8).
 *
 * Each page composes from these primitives so we never re-derive raw
 * spacing/color values inside JSX. Per ADR 0019, only token values may
 * appear in styles.
 */
import { CSSProperties } from "react";
import {
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";

export const PAGE: CSSProperties = {
  padding: SPACING.xl,
  maxWidth: 680,
  margin: "0 auto",
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: COLORS.background,
};

export const H1: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level1,
  marginTop: 0,
  marginBottom: SPACING.md,
  color: COLORS.textPrimary,
};

export const H2: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
};

export const BODY: CSSProperties = {
  marginTop: 0,
  marginBottom: SPACING.md,
};

export const PRIMARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

export const SECONDARY_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

export const DESTRUCTIVE_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.errorConfirm,
  border: `2px solid ${COLORS.errorConfirm}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

export const FIELD: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.sm,
  width: "100%",
  boxSizing: "border-box",
  fontFamily: TYPOGRAPHY.fontFamily,
};

export const FIELD_LABEL: CSSProperties = {
  display: "block",
  marginBottom: SPACING.xs,
  fontWeight: 600,
};

export const CARD: CSSProperties = {
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.md,
  padding: SPACING.lg,
  marginBottom: SPACING.lg,
};

export const SECTION: CSSProperties = {
  marginTop: SPACING.xl,
};

export const STACK: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.md,
};

export const ROW: CSSProperties = {
  display: "flex",
  flexDirection: "row",
  gap: SPACING.md,
  flexWrap: "wrap",
};

export const DIVIDER: CSSProperties = {
  border: 0,
  borderTop: `1px solid ${COLORS.disabled}`,
  margin: `${SPACING.xl}px 0`,
};

export const ALERT_TEXT: CSSProperties = {
  color: COLORS.errorConfirm,
  marginTop: SPACING.sm,
  marginBottom: 0,
};

export const SUCCESS_TEXT: CSSProperties = {
  color: COLORS.accentDesatGreen,
  marginTop: SPACING.sm,
  marginBottom: 0,
};
