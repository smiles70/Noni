/**
 * OnThisPage — in-page anchor menu for long marketing surfaces (WS-A).
 *
 * NN/g 2023: users now engage TOC links naturally; they increase
 * discoverability of deep content on long pages. Labels must carry
 * information scent — pass the real section headings, not clever names.
 *
 * In normal flow (never fixed/sticky) so it cannot intercept pointer
 * events over CTAs — the mobile-iphone overlap lesson applies.
 */
import { CSSProperties, MouseEvent } from "react";
import { COLORS, SPACING, RADIUS } from "../design/tokens";

export interface PageSection {
  id: string;
  label: string;
}

const NAV: CSSProperties = {
  maxWidth: 880,
  margin: `0 auto`,
  padding: `${SPACING.lg}px ${SPACING.xl}px 0`,
};

const LABEL: CSSProperties = {
  margin: `0 0 ${SPACING.sm}px`,
  fontSize: 15,
  fontWeight: 600,
  color: COLORS.textPrimary,
  letterSpacing: 0.4,
};

const LIST: CSSProperties = {
  listStyle: "none",
  display: "flex",
  flexWrap: "wrap",
  gap: SPACING.sm,
  margin: 0,
  padding: 0,
  // Horizontal scroll fallback on narrow viewports instead of a
  // collapsed dropdown — keeps all choices visible for older users.
  overflowX: "auto",
};

const LINK: CSSProperties = {
  display: "inline-block",
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  borderRadius: RADIUS.md,
  border: `1px solid ${COLORS.disabled}`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  fontSize: 15,
  lineHeight: 1.4,
  textDecoration: "none",
  whiteSpace: "nowrap",
};

export default function OnThisPage({ sections }: { sections: PageSection[] }) {
  const jump = (id: string) => (e: MouseEvent<HTMLAnchorElement>) => {
    const el = document.getElementById(id);
    if (!el) return; // fall through to native anchor behavior
    e.preventDefault();
    const reduced =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView?.({ behavior: reduced ? "auto" : "smooth" });
    // Move keyboard/AT focus to the destination heading so the jump
    // is announced and follow-up tab order is correct. Headings are
    // not natively focusable — make the target so programmatically.
    if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
    el.focus({ preventScroll: true });
  };

  return (
    <nav aria-label="On this page" style={NAV}>
      <p style={LABEL}>On this page</p>
      <ul style={LIST}>
        {sections.map((s) => (
          <li key={s.id}>
            <a href={`#${s.id}`} style={LINK} onClick={jump(s.id)}>
              {s.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
