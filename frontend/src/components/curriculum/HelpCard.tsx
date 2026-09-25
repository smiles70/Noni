/**
 * HelpCard — the learner "Call me" surface (learner-help-channel intake).
 *
 * Rendered in place of the lesson body when the NavBar Help action is
 * tapped; the LessonRenderer swaps to the `curriculum.help` envelope so
 * FIELD is authorized here and nowhere else on learner surfaces.
 *
 * Steps: offer → number → called | queued. One action at a time; the
 * number is stored locally so a repeat request is one tap (progress.ts
 * precedent — wrapped, never throws).
 */
import { CSSProperties, useState } from "react";
import { requestCallback } from "../../api/help";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  RADIUS,
  MOTION,
} from "../../design/tokens";
import { MIN_TOUCH_TARGET } from "../../styles/responsiveTokens";

type Step = "offer" | "number" | "called" | "queued";

const PHONE_KEY = "mynaani_help_phone";

function savedPhone(): string {
  try {
    return localStorage.getItem(PHONE_KEY) ?? "";
  } catch {
    return "";
  }
}

export default function HelpCard() {
  const [step, setStep] = useState<Step>("offer");
  const [phone, setPhone] = useState(savedPhone);
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    const value = phone.trim();
    if (submitting || value.length < 7) return;
    setSubmitting(true);
    try {
      const res = await requestCallback(value);
      try {
        localStorage.setItem(PHONE_KEY, value);
      } catch {
        /* storage unavailable — the call still proceeds */
      }
      setStep(res.calling ? "called" : "queued");
    } catch {
      setStep("queued");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={CARD} data-component="Card">
      <h2 style={H2}>Get help with this lesson</h2>
      {step === "offer" || step === "number" ? (
        <p style={PARA}>Tap the button and someone will call you right away.</p>
      ) : null}

      {step === "offer" ? (
        <button
          type="button"
          style={CALL_BTN}
          onClick={() => setStep("number")}
          data-component="Button"
        >
          Call me
        </button>
      ) : null}

      {step === "number" ? (
        <form
          onSubmit={(ev) => {
            ev.preventDefault();
            void submit();
          }}
          style={STACK}
        >
          <div>
            <label htmlFor="help-phone" style={FIELD_LABEL}>
              Your phone number
            </label>
            <input
              id="help-phone"
              type="tel"
              autoComplete="tel"
              inputMode="tel"
              required
              minLength={7}
              maxLength={20}
              value={phone}
              onChange={(ev) => setPhone(ev.target.value)}
              style={FIELD}
              disabled={submitting}
              data-component="Field"
            />
          </div>
          <button
            type="submit"
            style={CALL_BTN}
            disabled={submitting}
            data-component="Button"
          >
            Call me now
          </button>
        </form>
      ) : null}

      {step === "called" ? (
        <p style={PARA} role="status">
          We are calling you now. Keep your phone nearby — it will ring in a few
          seconds from 1-877-409-4144.
        </p>
      ) : null}

      {step === "queued" ? (
        <p style={PARA} role="status">
          We could not place the call just now. Our team has your request and
          will call you as soon as we can.
        </p>
      ) : null}

      <p style={FINE_PRINT}>
        Free call · your place in the lesson is saved. Prefer writing?{" "}
        <a href="mailto:help@mynaani.com" style={LINK}>
          help@mynaani.com
        </a>
      </p>
    </div>
  );
}

const CARD: CSSProperties = {
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.md,
  padding: SPACING.xl,
};

const H2: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  marginTop: 0,
  marginBottom: SPACING.md,
  color: COLORS.textPrimary,
};

const PARA: CSSProperties = {
  marginTop: 0,
  marginBottom: SPACING.md,
};

const STACK: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: SPACING.md,
};

const FIELD_LABEL: CSSProperties = {
  display: "block",
  fontSize: TYPOGRAPHY.bodySizePx,
  marginBottom: SPACING.xs,
  color: COLORS.textPrimary,
};

const FIELD: CSSProperties = {
  width: "100%",
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: COLORS.surface,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.sm,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  boxSizing: "border-box",
  minHeight: MIN_TOUCH_TARGET.mobile,
};

const CALL_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.md}px ${SPACING.lg}px`,
  backgroundColor: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  fontWeight: 600,
  cursor: "pointer",
  minHeight: MIN_TOUCH_TARGET.mobile,
  whiteSpace: "normal",
  transition: `opacity ${MOTION.defaultFadeMs}ms ease-out`,
  fontFamily: TYPOGRAPHY.fontFamily,
};

const FINE_PRINT: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.textPrimary,
  opacity: 0.7,
  marginTop: SPACING.lg,
  marginBottom: 0,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
};
