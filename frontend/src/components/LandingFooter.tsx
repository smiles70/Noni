/**
 * Landing mini-footer — a slim translucent strip pinned to the bottom
 * edge of the fixed-viewport hero.
 *
 * Why it exists: CCPA §7011(d) requires a conspicuous "privacy" link
 * on the homepage; the fixed hero cannot scroll to a footer, so the
 * footer comes inside the viewport (NN/g mini-footer pattern). Carries
 * only the legal minimum — copyright + Privacy/Terms/Help — so the
 * hero keeps its single-CTA focus.
 *
 * Rendered as a body-level <footer> sibling to the hero <section> so
 * it keeps its contentinfo landmark role (a footer nested inside a
 * section loses it per W3C APG).
 *
 * Intake: .ai/intake/2026-09-16-p2-landing-mini-footer.md
 */

import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING, TYPOGRAPHY } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import { loadFooterContent, type SiteFooterContent } from "../api/siteChrome";

const FALLBACK: Pick<SiteFooterContent, "mini_links" | "copyright"> = {
  mini_links: [
    { label: "Privacy", href: "/privacy" },
    { label: "Terms", href: "/terms" },
    { label: "Help", href: "/help" },
  ],
  copyright: `© ${new Date().getFullYear()} mynaani.`,
};

export default function LandingFooter() {
  const [content, setContent] = useState(FALLBACK);

  useEffect(() => {
    let cancelled = false;
    loadFooterContent()
      .then((c) => {
        if (!cancelled)
          setContent({
            mini_links: c.mini_links,
            copyright: c.copyright,
          });
      })
      .catch(() => {
        /* FALLBACK already covers the legal minimum */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <footer style={STRIP} data-landing-footer="mini">
      <span style={COPYRIGHT}>{content.copyright}</span>
      <nav aria-label="Legal" style={LINKS}>
        {content.mini_links.map((link) => (
          <Link key={link.label} to={link.href} style={LINK}>
            {link.label}
          </Link>
        ))}
      </nav>
    </footer>
  );
}

const STRIP: CSSProperties = {
  position: "fixed",
  bottom: 0,
  left: 0,
  right: 0,
  zIndex: 2,
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  flexWrap: "wrap",
  gap: `${SPACING.xs}px ${SPACING.md}px`,
  // Translucent like the logo plate, but opaque enough that small text
  // keeps a 4.5:1 contrast ratio over the hero photo.
  backgroundColor: "rgba(250, 250, 248, 0.85)",
  backdropFilter: "blur(8px)",
  WebkitBackdropFilter: "blur(8px)",
  padding: `${SPACING.xs}px ${SPACING.lg}px`,
  paddingBottom: `calc(${SPACING.xs}px + env(safe-area-inset-bottom, 0px))`,
  // The strip is a visual surface, not a click target. Keeping the
  // hero CTA interactive on small viewports is more important than
  // letting the strip background capture pointer events.
  pointerEvents: "none",
  fontFamily: TYPOGRAPHY.fontFamily,
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.textPrimary,
};

const COPYRIGHT: CSSProperties = {
  padding: `${SPACING.xs}px 0`,
  // Static text — no interaction needed. Leaving pointer-events off
  // keeps the hero CTA clickable where the wrapped strip overlaps it on
  // iPhone-width viewports (landing CTA timeout flake).
};

const LINKS: CSSProperties = {
  display: "flex",
  gap: SPACING.lg,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  minHeight: MIN_TOUCH_TARGET.mobile,
  minWidth: MIN_TOUCH_TARGET.mobile,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: `0 ${SPACING.xs}px`,
  pointerEvents: "auto",
};
