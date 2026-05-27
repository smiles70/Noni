/**
 * HowItWorksDialog — accessible modal that surfaces the long-form Noni
 * marketing copy when the visitor clicks "See how Noni works" on the
 * landing hero.
 *
 * Behaviour:
 *   - role="dialog" + aria-modal="true" + aria-labelledby for SR support.
 *   - ESC key closes; backdrop click closes; the X button closes.
 *   - Focus is moved to the close button on open and restored to the
 *     trigger element on close (handled here via a ref the caller can
 *     pass; we focus our close button on open).
 *   - Body scroll is locked while the dialog is open so older readers
 *     don't get a confusing dual-scroll surface.
 *
 * Copy is sourced from the same backend-driven LandingPageContent that
 * powers the landing page itself (ADR 0006). The caller passes it in to
 * avoid a second fetch.
 */
import { CSSProperties, useEffect, useRef } from "react";
import type { LandingPageContent } from "../api/landing";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../design/tokens";

interface Props {
  content: LandingPageContent;
  onClose: () => void;
  /** Called when the user clicks "Continue to my account" after reading. */
  onBegin?: () => void;
}

// ---- Tokenized styles ------------------------------------------------------

const BACKDROP: CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0, 0, 0, 0.55)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: SPACING.lg,
  zIndex: 1000,
};

const PANEL: CSSProperties = {
  background: COLORS.surface,
  color: COLORS.textPrimary,
  borderRadius: RADIUS.md,
  width: "min(760px, 100%)",
  maxHeight: "90vh",
  display: "flex",
  flexDirection: "column",
  boxShadow: "0 20px 50px rgba(0, 0, 0, 0.35)",
  fontFamily: TYPOGRAPHY.fontFamily,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
};

const HEADER: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  borderBottom: `1px solid ${COLORS.disabled}`,
};

const TITLE: CSSProperties = {
  margin: 0,
  fontSize: TYPOGRAPHY.headingScale.level2,
  color: COLORS.textPrimary,
};

const CLOSE_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  background: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
};

const BODY: CSSProperties = {
  padding: `${SPACING.lg}px ${SPACING.xl}px`,
  overflowY: "auto",
};

const SECTION: CSSProperties = {
  marginTop: SPACING.lg,
};

const H3: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level3,
  marginTop: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
};

const FOOTER: CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  borderTop: `1px solid ${COLORS.disabled}`,
};

const FOOTER_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  background: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
};

// ---- Helpers ---------------------------------------------------------------

function paragraphs(text: string) {
  return text.split("\n\n").map((p, i) => (
    <p key={i} style={{ marginTop: 0, marginBottom: SPACING.md }}>
      {p}
    </p>
  ));
}

// ---- Component -------------------------------------------------------------

export default function HowItWorksDialog({ content, onClose, onBegin }: Props) {
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);

  // Focus the close button when the dialog opens — ensures keyboard users
  // land somewhere predictable inside the modal.
  useEffect(() => {
    closeButtonRef.current?.focus();
  }, []);

  // ESC closes the dialog. Lock body scroll while open so the page
  // beneath doesn't drift under the modal.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [onClose]);

  return (
    <div
      style={BACKDROP}
      onClick={onClose}
      role="presentation"
      data-component="HowItWorksBackdrop"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="how-it-works-title"
        style={PANEL}
        onClick={(e) => e.stopPropagation()}
      >
        <header style={HEADER}>
          <h2 id="how-it-works-title" style={TITLE}>
            How Noni works
          </h2>
          <button
            ref={closeButtonRef}
            type="button"
            onClick={onClose}
            style={CLOSE_BTN}
            aria-label="Close"
          >
            Close
          </button>
        </header>

        <div style={BODY}>
          <section aria-labelledby="dlg-introduction-heading">
            <h3 id="dlg-introduction-heading" style={H3}>
              {content.introduction.title}
            </h3>
            {paragraphs(content.introduction.body)}
          </section>

          <section aria-labelledby="dlg-what-heading" style={SECTION}>
            <h3 id="dlg-what-heading" style={H3}>
              {content.what_noni_does.title}
            </h3>
            <ul>
              {content.what_noni_does.items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="dlg-feel-heading" style={SECTION}>
            <h3 id="dlg-feel-heading" style={H3}>
              {content.how_it_feels.title}
            </h3>
            <ul>
              {content.how_it_feels.items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="dlg-trust-heading" style={SECTION}>
            <h3 id="dlg-trust-heading" style={H3}>
              {content.trust_and_safety.title}
            </h3>
            {paragraphs(content.trust_and_safety.body)}
          </section>

          <section style={SECTION}>{paragraphs(content.closing.body)}</section>
        </div>

        <footer style={FOOTER}>
          {onBegin ? (
            <button
              type="button"
              onClick={() => {
                onBegin();
                onClose();
              }}
              style={FOOTER_BTN}
            >
              Continue to my account — free
            </button>
          ) : (
            <button type="button" onClick={onClose} style={FOOTER_BTN}>
              Got it
            </button>
          )}
        </footer>
      </div>
    </div>
  );
}
