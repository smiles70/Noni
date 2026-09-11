/**
 * Context-aware help request widget for caregiver and senior-facility paths.
 *
 * - Never used on the main consumer learner path.
 * - Geragogy-safe: calm copy, no urgency, large touch targets, calm colors.
 * - Context-specific categories and SLAs are enforced by the component props
 *   and double-checked by the backend.
 */
import { useMemo, useState } from "react";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../design/tokens";
import {
  CATEGORIES_BY_CONTEXT,
  categoryById,
  type HelpContext,
  submitHelpRequest,
} from "../api/help";

const PANEL: React.CSSProperties = {
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
  maxWidth: 420,
  width: "100%",
  boxSizing: "border-box",
};

const TITLE: React.CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  marginTop: 0,
  marginBottom: SPACING.sm,
};

const BODY: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  marginTop: 0,
  marginBottom: SPACING.md,
};

const FIELD: React.CSSProperties = {
  marginBottom: SPACING.md,
};

const LABEL: React.CSSProperties = {
  display: "block",
  fontSize: TYPOGRAPHY.bodySizePx,
  marginBottom: SPACING.xs,
  fontWeight: 600,
};

const SELECT: React.CSSProperties = {
  width: "100%",
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.md,
  minHeight: 44,
  backgroundColor: COLORS.surface,
  color: COLORS.textPrimary,
};

const TEXTAREA: React.CSSProperties = {
  width: "100%",
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.md,
  minHeight: 96,
  resize: "vertical",
  boxSizing: "border-box",
  fontFamily: TYPOGRAPHY.fontFamily,
};

const INPUT: React.CSSProperties = {
  width: "100%",
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.md,
  minHeight: 44,
  boxSizing: "border-box",
};

const ERROR: React.CSSProperties = {
  color: COLORS.errorConfirm,
  fontSize: TYPOGRAPHY.bodySizePx,
  marginBottom: SPACING.sm,
};

const PRIMARY_BTN: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: "none",
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  cursor: "pointer",
  minHeight: 44,
};

const SECONDARY_BTN: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  backgroundColor: "transparent",
  color: COLORS.textPrimary,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.lg,
  fontWeight: 600,
  cursor: "pointer",
  minHeight: 44,
  marginRight: SPACING.md,
};

interface Props {
  context: HelpContext;
  pagePath: string;
  prefilledEmail?: string;
}

export default function HelpRequestWidget({
  context,
  pagePath,
  prefilledEmail = "",
}: Props) {
  const categories = useMemo(
    () => CATEGORIES_BY_CONTEXT[context] || [],
    [context],
  );
  const [open, setOpen] = useState(false);
  const [categoryId, setCategoryId] = useState(categories[0]?.id || "");
  const [email, setEmail] = useState(prefilledEmail);
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    if (sending) return;
    setOpen(false);
    setError(null);
    setMessage("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) {
      setError("Please tell us how we can help.");
      return;
    }
    if (!categoryId) {
      setError("Please choose a topic.");
      return;
    }
    const emailValue = email.trim();
    if (
      !emailValue ||
      !emailValue.includes("@") ||
      !emailValue.includes(".", emailValue.indexOf("@"))
    ) {
      setError("Please enter a valid email for your reply.");
      return;
    }
    setSending(true);
    setError(null);
    try {
      await submitHelpRequest(
        context,
        categoryId,
        message.trim(),
        pagePath,
        emailValue,
      );
      setSubmitted(true);
      setMessage("");
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { envelope_id?: string } } })?.response
          ?.data?.envelope_id || "help.submit_failed";
      setError(
        detail === "help.ratelimit_exceeded"
          ? "Please wait a few minutes before sending another message."
          : "We could not send your message. Please try again.",
      );
    } finally {
      setSending(false);
    }
  };

  if (submitted) {
    const category = categoryById(context, categoryId);
    const responseTime = category?.initialResponseTime || "one week";
    return (
      <aside style={PANEL} data-context={context} data-help-widget="submitted">
        <p style={{ ...BODY, margin: 0 }}>
          Thank you. We received your message.
          {email
            ? ` We will reply to ${email} within ${responseTime}.`
            : ` We will reply within ${responseTime}.`}
        </p>
        <button
          type="button"
          style={{ ...SECONDARY_BTN, marginTop: SPACING.md, marginRight: 0 }}
          onClick={() => {
            setSubmitted(false);
            setOpen(false);
          }}
        >
          Close
        </button>
      </aside>
    );
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={handleOpen}
        style={PRIMARY_BTN}
        data-context={context}
        data-help-widget="trigger"
      >
        {context === "caregiver"
          ? "Questions about gifting?"
          : "Community support"}
      </button>
    );
  }

  return (
    <aside style={PANEL} data-context={context} data-help-widget="panel">
      <h2 style={TITLE}>
        {context === "caregiver" ? "Gift help" : "Community help"}
      </h2>
      <p style={BODY}>
        {context === "caregiver"
          ? "Tell us about your gift purchase and we will get back to you."
          : "Tell us about your community or partnership question and we will get back to you."}
      </p>
      <form onSubmit={handleSubmit} noValidate>
        <div style={FIELD}>
          <label htmlFor="help-category" style={LABEL}>
            Topic
          </label>
          <select
            id="help-category"
            value={categoryId}
            onChange={(e) =>
              setCategoryId(e.target.value as import("../api/help").CategoryId)
            }
            style={SELECT}
          >
            {categories.map((c) => (
              <option value={c.id} key={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div style={FIELD}>
          <label htmlFor="help-email" style={LABEL}>
            Email for reply
          </label>
          <input
            id="help-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            style={INPUT}
            autoComplete="email"
            required
          />
        </div>
        <div style={FIELD}>
          <label htmlFor="help-message" style={LABEL}>
            Message
          </label>
          <textarea
            id="help-message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="What can we help you with?"
            style={TEXTAREA}
            maxLength={2000}
            rows={4}
          />
        </div>
        {error && <p style={ERROR}>{error}</p>}
        <div style={{ display: "flex" }}>
          <button
            type="submit"
            style={{ ...PRIMARY_BTN, marginRight: SPACING.md }}
            disabled={sending}
          >
            {sending ? "Sending..." : "Send message"}
          </button>
          <button
            type="button"
            style={SECONDARY_BTN}
            onClick={handleClose}
            disabled={sending}
          >
            Cancel
          </button>
        </div>
      </form>
    </aside>
  );
}
