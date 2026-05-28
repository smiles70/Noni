/**
 * Gift redemption page (account.gift_redeem envelope).
 *
 * Two-step flow:
 *   1. Paste token -> POST /api/gifts/preview (read-only validation)
 *   2. Confirm     -> POST /api/gifts/claim   (irreversible binding)
 *
 * Step 2 is reversible from the user's perspective: claiming binds the
 * gift to the current account and is fine to repeat (the same account
 * cannot re-claim the consumed token; another account cannot either).
 * It is therefore not modeled as an irreversible action in the envelope.
 */
import { useEffect, useState } from "react";
import { claimGift, previewGift } from "../api/billing";
import { loadEnvelope } from "../api/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import {
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
  DIVIDER,
  FIELD,
  FIELD_LABEL,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
  SUCCESS_TEXT,
} from "./AccountStyles";

interface Props {
  onClaimed: () => void;
  onBack: () => void;
  onHelp?: () => void;
}

type Phase = "enter" | "preview_ok" | "claimed";

export default function GiftRedeemPage({ onClaimed, onBack, onHelp }: Props) {
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [token, setToken] = useState("");
  const [productCode, setProductCode] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>("enter");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEnvelope("account.gift_redeem")
      .then(setEnvelope)
      .catch(() => setError("This page is paused. Refresh in a moment."));
  }, []);

  if (!envelope) {
    return (
      <main style={PAGE} aria-live="polite" data-component="PendingBanner">
        <p style={BODY}>{error ?? "One moment — loading."}</p>
      </main>
    );
  }

  const handlePreview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await previewGift(token.trim());
      if (!res.valid) {
        setError("This gift code is not valid, or it has already been used.");
        setPhase("enter");
      } else {
        setProductCode(res.product_code);
        setPhase("preview_ok");
      }
    } catch {
      setError("We could not check that code. Please try again in a moment.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleClaim = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await claimGift(token.trim());
      setPhase("claimed");
    } catch {
      setError(
        "We could not redeem that code. It may have just been used by someone else.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Field", "Card", "Divider"],
    primaryActionCount: 2,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
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
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.md],
    motionDurationsMs: [MOTION.defaultFadeMs],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE} aria-busy={submitting}>
        <h1 style={H1}>Redeem a gift</h1>
        <p style={BODY}>
          Paste the gift code you received. We will check it before anything
          changes on your account.
        </p>

        {phase === "enter" && (
          <form onSubmit={handlePreview} style={STACK}>
            <div>
              <label htmlFor="gift-token" style={FIELD_LABEL}>
                Gift code
              </label>
              <input
                id="gift-token"
                type="text"
                autoComplete="off"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                style={FIELD}
                disabled={submitting}
                required
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? "gift-token-error" : undefined}
              />
            </div>
            <div style={STACK}>
              <button type="submit" style={PRIMARY_BTN} disabled={submitting}>
                {submitting ? "Checking…" : "Check this code"}
              </button>
              <button
                type="button"
                style={SECONDARY_BTN}
                onClick={onBack}
                disabled={submitting}
              >
                Go back
              </button>
            </div>
            {error && (
              <p id="gift-token-error" style={ALERT_TEXT} role="alert">
                {error}
              </p>
            )}
          </form>
        )}

        {phase === "preview_ok" && (
          <section style={CARD}>
            <h2 style={H2}>This code is valid</h2>
            <p style={BODY}>
              It will give you access to:{" "}
              <strong>{productCode ?? "the gifted content"}</strong>.
            </p>
            <div style={STACK}>
              <button
                type="button"
                style={PRIMARY_BTN}
                onClick={handleClaim}
                disabled={submitting}
              >
                {submitting ? "Redeeming…" : "Redeem now"}
              </button>
              <button
                type="button"
                style={SECONDARY_BTN}
                onClick={() => {
                  setPhase("enter");
                  setProductCode(null);
                }}
                disabled={submitting}
              >
                Go back
              </button>
            </div>
            {error && (
              <p style={ALERT_TEXT} role="alert">
                {error}
              </p>
            )}
          </section>
        )}

        {phase === "claimed" && (
          <section style={CARD}>
            <h2 style={H2}>Done</h2>
            <p style={SUCCESS_TEXT}>
              The gift has been added to your account. You can continue to
              the next module whenever you are ready.
            </p>
            <hr style={DIVIDER} />
            <button type="button" style={PRIMARY_BTN} onClick={onClaimed}>
              Continue
            </button>
          </section>
        )}
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
              Questions about gift tokens
            </button>
          </p>
        )}
      </main>
    </RenderGuard>
  );
}
