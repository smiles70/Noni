/**
 * Account settings page (account.settings envelope).
 *
 * Hosts:
 *   - identity summary (email, via useAuth()'s AuthProvider state)
 *   - sign out (reversible; delegates to AuthProvider.signOut)
 *   - delete account (IRREVERSIBLE; envelope permits exactly 1)
 *
 * Delete uses a ConfirmDialog with the contract-mandated copy
 * pattern: "This will change [X]. You can continue or go back."
 * (CONTRACT Section III.) After confirmation we POST /me/delete,
 * which marks the account for deletion and revokes all sessions.
 */
import { useEffect, useState } from "react";
import { clearMockToken, deleteAccount } from "../api/auth";
import { useAuth } from "../auth/AuthProvider";
import { loadEnvelope } from "../api/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import {
  buildConfirmationCopy,
  COLORS,
  MOTION,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import {
  ALERT_TEXT,
  BODY,
  CARD,
  DESTRUCTIVE_BTN,
  DIVIDER,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
  SUCCESS_TEXT,
} from "./AccountStyles";
import ClerkSignOutButton from "./ClerkSignOutButton";

// Build-time switch (mirrors App.tsx). In Clerk mode we render the
// Clerk-aware sign-out button (uses useClerk()); in mock mode we just
// clear the localStorage Bearer token. ADR 0024 — no backend round-trip
// for sign-out in either path.
const AUTH_PROVIDER =
  ((import.meta as unknown as { env?: { VITE_AUTH_PROVIDER?: string } }).env
    ?.VITE_AUTH_PROVIDER ?? "mock");

interface Props {
  onSignedOut: () => void;
  onDeleted: () => void;
  onBack: () => void;
  onHelp?: () => void;
}

export default function AccountSettingsPage({
  onSignedOut,
  onDeleted,
  onBack,
  onHelp,
}: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [deletedNotice, setDeletedNotice] = useState(false);

  // B1: identity comes from AuthProvider, not a local whoami() fetch.
  const ctx = useAuth();
  const me = ctx?.state?.status === "READY" ? ctx.state : null;

  const CONFIRM_COPY = buildConfirmationCopy("your account access");

  useEffect(() => {
    loadEnvelope("account.settings")
      .then(setEnvelope)
      .catch(() =>
        setError("This page is paused. Please refresh in a moment."),
      );
  }, []);

  if (!envelope) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>{error ?? "One moment — loading."}</p>
      </main>
    );
  }

  const handleSignOut = async () => {
    setSubmitting(true);
    try {
      // Mock-mode sign-out is purely client-side: drop the Bearer
      // token from localStorage; AuthProvider's onSignedOut callback
      // will transition state to SIGNED_OUT and the caller navigates.
      clearMockToken();
      onSignedOut();
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmDelete = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await deleteAccount();
      setDeletedNotice(true);
      // Brief pause so the user can read the confirmation text.
      setTimeout(onDeleted, 1500);
    } catch {
      setError("We could not complete that. Please try again in a moment.");
    } finally {
      setSubmitting(false);
    }
  };

  const proposal: RenderProposal = {
    components: [
      "Heading",
      "Body",
      "Button",
      "Card",
      "List",
      "Divider",
      ...(confirming ? (["ConfirmDialog"] as const) : []),
    ],
    primaryActionCount: confirming ? 2 : 3, // back + signout + delete-trigger
    irreversibleActionCount: confirming ? 1 : 0,
    highlightedRecommendationCount: 0,
    visibleTextLevels: 2,
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentMutedBlue,
      COLORS.accentDesatGreen,
      COLORS.disabled,
      COLORS.errorConfirm,
    ],
    spacingPxUsed: [SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false, // confirmed via ConfirmDialog
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE} aria-busy={submitting}>
        <h1 style={H1}>Your account</h1>

        <section style={CARD}>
          <h2 style={H2}>Signed in as</h2>
          <p style={BODY}>{me?.email ?? "—"}</p>
          {AUTH_PROVIDER === "clerk" ? (
            // In Clerk mode the sign-out has to drop Clerk's cookies
            // first; ClerkSignOutButton owns that orchestration via the
            // useClerk() hook, which can only run inside ClerkProvider.
            <ClerkSignOutButton
              onSignedOut={onSignedOut}
              disabled={submitting}
            />
          ) : (
            <button
              type="button"
              style={SECONDARY_BTN}
              onClick={handleSignOut}
              disabled={submitting}
            >
              Sign out
            </button>
          )}
        </section>

        <section style={CARD}>
          <h2 style={H2}>Delete this account</h2>
          <p style={BODY}>
            This removes your saved progress and any access you have purchased.
            You will be signed out on every device. There is a short grace
            period during which you can ask us to restore the account.
          </p>

          {!confirming && !deletedNotice && (
            <button
              type="button"
              style={DESTRUCTIVE_BTN}
              onClick={() => setConfirming(true)}
              disabled={submitting}
            >
              Delete my account
            </button>
          )}

          {confirming && !deletedNotice && (
            <div role="dialog" aria-modal="true" data-component="ConfirmDialog">
              <p style={BODY}>{CONFIRM_COPY}</p>
              <div style={STACK}>
                <button
                  type="button"
                  style={DESTRUCTIVE_BTN}
                  onClick={handleConfirmDelete}
                  disabled={submitting}
                >
                  {submitting ? "Working…" : "Continue and delete"}
                </button>
                <button
                  type="button"
                  style={SECONDARY_BTN}
                  onClick={() => setConfirming(false)}
                  disabled={submitting}
                >
                  Go back
                </button>
              </div>
            </div>
          )}

          {deletedNotice && (
            <p style={SUCCESS_TEXT} role="status" aria-live="polite">
              Your account has been scheduled for deletion. You will be signed
              out shortly.
            </p>
          )}

          {error && (
            <p style={ALERT_TEXT} role="alert">
              {error}
            </p>
          )}
        </section>

        <hr style={DIVIDER} />
        <button
          type="button"
          style={PRIMARY_BTN}
          onClick={onBack}
          disabled={submitting}
        >
          Go back
        </button>

        {onHelp && (
          <p style={{ marginTop: SPACING.md }}>
            <button
              type="button"
              onClick={onHelp}
              style={{
                background: "none",
                border: "none",
                padding: 0,
                color: COLORS.accentMutedBlue,
                textDecoration: "underline",
                cursor: "pointer",
                fontSize: TYPOGRAPHY.bodySizePx,
                fontFamily: TYPOGRAPHY.fontFamily,
              }}
            >
              Account help
            </button>
          </p>
        )}
      </main>
    </RenderGuard>
  );
}
