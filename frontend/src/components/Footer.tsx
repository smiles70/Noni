/**
 * Shared site footer ("fat footer") for scrollable marketing surfaces.
 *
 * Structure follows the GetSetUp reference and NN/g doormat-nav
 * pattern: centered brand mark, one nav row covering every public
 * surface, hairline divider, then a legal row (privacy/terms +
 * copyright). Copy is backend-served via /api/site/footer; on load
 * failure the footer still renders its legal row from a static
 * fallback so the CCPA "conspicuous privacy link" is never absent.
 *
 * Geragogy: ≤6 nav links, ≥24px targets, calm sentence-case labels.
 * Semantic <footer> at body level → contentinfo landmark.
 *
 * Intakes: .ai/intake/2026-09-16-p2-marketing-fat-footer.md
 */

import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING, TYPOGRAPHY } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import { loadFooterContent, type SiteFooterContent } from "../api/siteChrome";

// Legal-row fallback so Privacy/Terms are never absent even if the
// content endpoint is unreachable.
const FALLBACK: SiteFooterContent = {
  tagline: "mynaani — AI learning for adults 55+",
  nav_links: [
    { label: "For learners", href: "/" },
    { label: "For caregivers", href: "/caregiver" },
    { label: "Be our partner", href: "/for-communities" },
    { label: "Gift", href: "/gift" },
    { label: "About us", href: "/about" },
    { label: "Help", href: "/help" },
  ],
  legal_links: [
    { label: "Privacy", href: "/privacy" },
    { label: "Terms", href: "/terms" },
  ],
  mini_links: [],
  brand_label: "mynaani",
  copyright: `© ${new Date().getFullYear()} mynaani. All rights reserved.`,
};

interface Props {
  /** Current page path; its own nav entry is de-emphasized. */
  currentPath?: string;
}

export default function Footer({ currentPath }: Props) {
  const [content, setContent] = useState<SiteFooterContent>(FALLBACK);

  useEffect(() => {
    let cancelled = false;
    loadFooterContent()
      .then((c) => {
        if (!cancelled) setContent(c);
      })
      .catch(() => {
        /* FALLBACK already covers the legal minimum */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <footer style={FOOTER} data-site-footer="fat">
      <img
        src="/mynaani-logo.webp"
        alt={content.brand_label}
        width={72}
        height={75}
        style={BRAND}
      />
      <nav aria-label="Site" style={NAV}>
        {content.nav_links.map((link) => (
          <Link
            key={link.href}
            to={link.href}
            style={link.href === currentPath ? NAV_LINK_CURRENT : NAV_LINK}
            aria-current={link.href === currentPath ? "page" : undefined}
          >
            {link.label}
          </Link>
        ))}
      </nav>
      <div style={HAIRLINE} />
      <div style={LEGAL_ROW}>
        <span style={LEGAL_LINKS}>
          {content.legal_links.map((link) => (
            <Link key={link.href} to={link.href} style={LEGAL_LINK}>
              {link.label}
            </Link>
          ))}
        </span>
        <span style={COPYRIGHT}>{content.copyright}</span>
      </div>
    </footer>
  );
}

const FOOTER: CSSProperties = {
  borderTop: `1px solid ${COLORS.disabled}`,
  padding: `${SPACING.xl}px`,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: SPACING.md,
  backgroundColor: COLORS.surface,
  fontSize: TYPOGRAPHY.bodySizePx,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
};

const BRAND: CSSProperties = {
  display: "block",
};

const NAV: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  justifyContent: "center",
  gap: `${SPACING.sm}px ${SPACING.lg}px`,
};

const NAV_LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  padding: `${SPACING.xs}px ${SPACING.xs}px`,
  minHeight: MIN_TOUCH_TARGET.mobile,
  display: "inline-flex",
  alignItems: "center",
};

const NAV_LINK_CURRENT: CSSProperties = {
  ...NAV_LINK,
  color: COLORS.textPrimary,
  fontWeight: 600,
};

const HAIRLINE: CSSProperties = {
  width: "100%",
  maxWidth: 720,
  borderTop: `1px solid ${COLORS.disabled}`,
};

const LEGAL_ROW: CSSProperties = {
  width: "100%",
  maxWidth: 720,
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  flexWrap: "wrap",
  gap: SPACING.sm,
};

const LEGAL_LINKS: CSSProperties = {
  display: "inline-flex",
  gap: SPACING.lg,
};

const LEGAL_LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  padding: `${SPACING.xs}px 0`,
  minHeight: MIN_TOUCH_TARGET.mobile,
  display: "inline-flex",
  alignItems: "center",
};

const COPYRIGHT: CSSProperties = {
  color: COLORS.textPrimary,
};
