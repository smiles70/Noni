/**********************************************************************
 * AuthBlockedNotice — definitive auth-failure notice.
 *
 * Shown when AuthProvider reports `state.status === "REJECTED"`, i.e.
 * the backend definitively refused the credential and we must not pretend
 * the user is signed in. Per System Constraint Model B5, definitive
 * failures are surfaced with discriminated copy keyed on the AuthError
 * code — never a raw error message, never a stack trace.
 *
 * Geragogy contract:
 *   - Predictability: each code maps to one stable copy block
 *   - Dignity: plain language; no error codes shown to the user
 *   - Reversibility: a single recommended action ("Sign in again")
 *   - Cognitive load: title + one-sentence body + one button
 *
 * Authorized component family: BlockedNotice (CONTRACT Section I.D).
 *
 * Tag: login-redesign-v1.
 **********************************************************************/

import type { CSSProperties } from "react";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";

export interface BlockedCopy {
  title: string;
  body: string;
  actionLabel: string;
}

/**
 * Map a backend AuthError code to the user-facing copy block.
 *
 * The set of codes mirrors `backend/services/auth_verifier.py`. Any code
 * not explicitly mapped falls through to a safe generic block — we never
 * leak the raw code to the user, and we always offer a recoverable action.
 *
 * Exported for unit testing (vitest runs in node mode; we cannot render).
 */
export function copyForCode(code: string | undefined): BlockedCopy {
  switch (code) {
    case "auth.expired":
      return {
        title: "Your sign-in has expired",
        body: "Please sign in again to continue.",
        actionLabel: "Sign in again",
      };

    case "auth.account_deleted":
      return {
        title: "This account is no longer available",
        body:
          "If this is unexpected, contact support. " +
          "You can also sign in with a different account.",
        actionLabel: "Sign in again",
      };

    case "auth.signature_invalid":
    case "auth.issuer_mismatch":
    case "auth.malformed":
    case "auth.subject_missing":
      return {
        title: "We couldn't verify your sign-in",
        body: "Please sign in again to continue.",
        actionLabel: "Sign in again",
      };

    default:
      return {
        title: "Something prevented sign-in",
        body: "Please sign in again to continue.",
        actionLabel: "Sign in again",
      };
  }
}

interface Props {
  errorCode?: string;
  onSignIn?: () => void;
}

const NOTICE: CSSProperties = {
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.errorConfirm}`,
  borderRadius: RADIUS.md,
  padding: SPACING.lg,
  margin: SPACING.md,
  maxWidth: 560,
  marginLeft: "auto",
  marginRight: "auto",
  fontFamily: TYPOGRAPHY.fontFamily,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  color: COLORS.textPrimary,
};

const TITLE: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  margin: 0,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
};

const BODY: CSSProperties = {
  margin: 0,
  marginBottom: SPACING.md,
};

const ACTION_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
};

export default function AuthBlockedNotice({ errorCode, onSignIn }: Props) {
  const copy = copyForCode(errorCode);
  return (
    <div role="alert" aria-live="assertive" style={NOTICE}>
      <h2 style={TITLE}>{copy.title}</h2>
      <p style={BODY}>{copy.body}</p>
      {onSignIn && (
        <button type="button" onClick={onSignIn} style={ACTION_BTN}>
          {copy.actionLabel}
        </button>
      )}
    </div>
  );
}
