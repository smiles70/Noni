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
import { useAuth } from "../auth/AuthProvider";
import { COLORS, MOTION, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";
import { GeragogySafeTap } from "./GeragogySafeTap";

interface Props {
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
  /** S25.1: open the lesson menu / table of contents. Optional so
   *  callers whose envelope cannot accommodate an extra primary action
   *  (e.g. LandingPage) can omit it. */
  onOpenMenu?: () => void;
  onHelp?: () => void;
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
  onOpenMenu,
  onHelp,
}: Props) {
  // B1: NavBar reads auth state from AuthProvider, never via its own
  // whoami() call (T-H2). It also never mounts an interceptor or fetches
  // /auth/session itself.
  const ctx = useAuth();
  const state = ctx?.state;
  const status = state?.status;

  // Loading-equivalent: AuthProvider hasn't finished resolving yet.
  // Reserve space so the page doesn't reflow on transition.
  if (status === "BOOT" || status === "AUTHENTICATING" || !status) {
    return <nav style={NAV} aria-hidden="true" />;
  }

  const signedIn = status === "READY";
  // Display identity = best available human-readable label.
  const identity: string | null = signedIn
    ? state?.displayName ?? state?.email ?? null
    : null;

  return (
    <nav style={NAV} aria-label="Account">
      {signedIn && identity && <span style={EMAIL}>{identity}</span>}

      {!signedIn && onSignIn && (
        <GeragogySafeTap>
          <button type="button" style={LINK_BTN} onClick={onSignIn}>
            Sign in
          </button>
        </GeragogySafeTap>
      )}

      {signedIn && onContinuePaid && (
        <GeragogySafeTap>
          <button type="button" style={LINK_BTN} onClick={onContinuePaid}>
            Upgrade — Modules 4 & 5
          </button>
        </GeragogySafeTap>
      )}

      {signedIn && onAccount && (
        <GeragogySafeTap>
          <button type="button" style={LINK_BTN} onClick={onAccount}>
            Your account
          </button>
        </GeragogySafeTap>
      )}

      {onOpenMenu && (
        <GeragogySafeTap>
          <button type="button" style={LINK_BTN} onClick={onOpenMenu}>
            Lessons
          </button>
        </GeragogySafeTap>
      )}

      {onHelp && (
        <GeragogySafeTap>
          <button type="button" style={LINK_BTN} onClick={onHelp}>
            Help
          </button>
        </GeragogySafeTap>
      )}
    </nav>
  );
}
