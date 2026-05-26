/**
 * Sprint 28-B.9: reusable empty-state component.
 *
 * Renders a centered, accessible message for views with no data
 * (empty curriculum menu, no purchases yet, etc.). Uses design tokens
 * only and includes an optional primary action.
 */

import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";

interface Props {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
}: Props) {
  return (
    <section
      role="status"
      aria-live="polite"
      data-component="EmptyState"
      style={{
        padding: SPACING.xl,
        maxWidth: 560,
        margin: "0 auto",
        textAlign: "center",
        fontFamily: TYPOGRAPHY.fontFamily,
        color: COLORS.textPrimary,
      }}
    >
      <h2
        style={{
          fontSize: TYPOGRAPHY.headingScale.level2,
          marginBottom: SPACING.md,
          fontWeight: 600,
        }}
      >
        {title}
      </h2>
      {description && (
        <p style={{ fontSize: TYPOGRAPHY.bodySizePx, marginBottom: SPACING.lg }}>
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          style={{
            fontSize: TYPOGRAPHY.bodySizePx,
            padding: `${SPACING.sm}px ${SPACING.lg}px`,
            backgroundColor: COLORS.accentMutedBlue,
            color: COLORS.surface,
            border: "none",
            borderRadius: RADIUS.sm,
            cursor: "pointer",
          }}
        >
          {actionLabel}
        </button>
      )}
    </section>
  );
}
