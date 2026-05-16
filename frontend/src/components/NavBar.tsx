/**
 * Minimal session-aware navigation strip.
 *
 * Sits at the top of long-lived pages (landing, curriculum). Surfaces the
 * three A8 entry points so they are reachable without dev-tool URL hacks:
 *   - Sign in    (when signed out)
 *   - Continue   (when signed in; routes to paywall / paid content)
 *   - Your account
 *
 * Uses only tokens from design/tokens.ts. The "Continue" entry is a
 * secondary action — the primary CTA for an unauthenticated visitor lives
 * inside LandingPage itself (the contract's single highlighted recommendation
 * per state stays unviolated because NavBar contributes zero highlighted
 * recommendations).
 */
import { useEffect, useState } from "react";
import { whoami, type WhoAmIResponse } from "../api/auth";
import { COLORS, MOTION, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";

interface Props {
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
}

const NAV: React.CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  gap: SPACING.sm,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  marginBottom: SPACING.md,
  fontFamily: TYPOGRAPHY.fontFamily,
};

const LINK_BTN: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.xs}px ${SPACING.md}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
};

const EMAIL: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.textPrimary,
  alignSelf: "center",
  marginRight: SPACING.sm,
};

export default function NavBar({
  onSignIn,
  onContinuePaid,
  onAccount,
}: Props) {
  const [me, setMe] = useState<WhoAmIResponse | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    whoami()
      .then((res) => setMe(res))
      .catch(() => setMe(null))
      .finally(() => setLoaded(true));
  }, []);

  if (!loaded) {
    // Reserve space so the page does not reflow when whoami resolves.
    return <nav style={NAV} aria-hidden="true" />;
  }

  const signedIn = me?.has_active_session === true;

  return (
    <nav style={NAV} aria-label="Account">
      {signedIn && me?.email && <span style={EMAIL}>{me.email}</span>}

      {!signedIn && onSignIn && (
        <button type="button" style={LINK_BTN} onClick={onSignIn}>
          Sign in
        </button>
      )}

      {signedIn && onContinuePaid && (
        <button type="button" style={LINK_BTN} onClick={onContinuePaid}>
          Upgrade — Modules 4 & 5
        </button>
      )}

      {signedIn && onAccount && (
        <button type="button" style={LINK_BTN} onClick={onAccount}>
          Your account
        </button>
      )}
    </nav>
  );
}
