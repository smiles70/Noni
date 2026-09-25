/**
 * Contact page (/contact) — the "Talk to us" destination.
 *
 * Shared surface: serves both learner-side and facility visitors, so
 * copy stays persona-neutral — no gift pricing, no facility tiers, no
 * chat widget. Visual grammar: bid-17 MARKETING tokens (charcoal hero,
 * paper surface, gold CTA) matching /for-communities (PS-BID17-022).
 *
 * Submission: POST /api/v1/site/contact-inquiry (backend emails the
 * help inbox off the request path). If the endpoint is unreachable the
 * form falls back to a mailto: with the same content so a message is
 * never lost.
 *
 * Intake: .ai/intake/2026-09-17-p2-contact-page-talk-to-us.md
 */

import { useEffect, useState, type CSSProperties, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { API_BASE_URL } from "../api/client";
import { loadFooterContent } from "../api/siteChrome";
import {
  COLORS,
  MARKETING,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import { BODY, FIELD_LABEL, H2, STACK } from "./AccountStyles";

const CONTACT_EMAIL = "help@mynaani.com";

interface Props {
  onBack: () => void;
}

interface FormState {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  /** Honeypot — hidden from humans, bots fill it. */
  website: string;
}

const INITIAL: FormState = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  website: "",
};

export default function ContactPage({ onBack }: Props) {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [fellBack, setFellBack] = useState(false);
  const [contactPhone, setContactPhone] = useState("");

  useEffect(() => {
    loadFooterContent()
      .then((c) => setContactPhone(c.contact_phone || ""))
      .catch(() => setContactPhone(""));
  }, []);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function mailtoHref(): string {
    const subject = `Contact request from ${form.firstName} ${form.lastName}`;
    const body = [
      `Name: ${form.firstName} ${form.lastName}`,
      `Email: ${form.email}`,
      `Phone: ${form.phone || "Not provided"}`,
    ].join("\n");
    return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(
      subject,
    )}&body=${encodeURIComponent(body)}`;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/site/contact-inquiry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: form.firstName,
          last_name: form.lastName,
          email: form.email,
          phone: form.phone,
          website: form.website,
        }),
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      setSubmitted(true);
    } catch {
      // Message must never be lost — fall back to the visitor's mail app.
      window.location.href = mailtoHref();
      setFellBack(true);
      setSubmitted(true);
    } finally {
      setSubmitting(false);
    }
  }

  if (submitted) {
    return (
      <main style={PAGE}>
        <div style={HERO}>
          <div style={HERO_INNER}>
            <p style={KICKER}>Talk to us</p>
            <h1 style={H1_DARK}>Thank you</h1>
            <p style={SUB_DARK}>
              {fellBack
                ? "Your message opened in your email app. If it did not, copy your details and send them to "
                : "We received your note and a member of our team will reply. If you need us sooner, write to "}
              <a href={`mailto:${CONTACT_EMAIL}`} style={LINK_DARK}>
                {CONTACT_EMAIL}
              </a>
              .
            </p>
            <button onClick={onBack} style={CTA_GOLD_BTN}>
              Back to mynaani
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main style={PAGE}>
      <div style={HERO}>
        <div style={HERO_INNER}>
          <Link
            to="/"
            style={BACK_DARK}
            onClick={(e) => {
              e.preventDefault();
              onBack();
            }}
          >
            ← Back to mynaani
          </Link>
          <p style={KICKER}>Talk to us</p>
          <h1 style={H1_DARK}>We'd love to hear from you</h1>
          {contactPhone && (
            <p style={SUB_DARK}>
              Call us at{" "}
              <a
                href={`tel:${contactPhone.replace(/[^0-9+]/g, "")}`}
                style={LINK_DARK}
                aria-label="Call MyNaani, toll-free"
              >
                {contactPhone}
              </a>{" "}
              (toll-free) — the line is answered by our AI receptionist, who can
              connect you to a person when needed. Or send us a note below and
              we'll reply.
            </p>
          )}
        </div>
      </div>

      <div style={FORM_WRAP}>
        <form onSubmit={handleSubmit} style={FORM_CARD}>
          <h2 style={{ ...H2, marginTop: 0 }}>Send us a note</h2>

          <div style={STACK}>
            <Field label="First name" required>
              <input
                type="text"
                name="first_name"
                value={form.firstName}
                onChange={(e) => update("firstName", e.target.value)}
                style={INPUT}
                required
                autoComplete="given-name"
              />
            </Field>
            <Field label="Last name" required>
              <input
                type="text"
                name="last_name"
                value={form.lastName}
                onChange={(e) => update("lastName", e.target.value)}
                style={INPUT}
                required
                autoComplete="family-name"
              />
            </Field>
            <Field label="Email" required>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
                style={INPUT}
                required
                autoComplete="email"
              />
            </Field>
            <Field label="Phone number">
              <input
                type="tel"
                name="phone"
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
                style={INPUT}
                autoComplete="tel"
              />
            </Field>

            {/* Honeypot — visually hidden; bots fill it, humans never do. */}
            <label style={HONEYPOT} aria-hidden="true" tabIndex={-1}>
              Website
              <input
                type="text"
                name="website"
                value={form.website}
                onChange={(e) => update("website", e.target.value)}
                tabIndex={-1}
                autoComplete="off"
              />
            </label>

            <button type="submit" style={CTA_GOLD_BTN} disabled={submitting}>
              {submitting ? "Sending…" : "Send message"}
            </button>
            <p style={PRIVACY_NOTE}>
              We only use these details to reply to you — no marketing list, no
              sharing.
            </p>
          </div>
        </form>
      </div>
    </main>
  );
}

function Field({
  label,
  children,
  required,
}: {
  label: string;
  children: React.ReactNode;
  required?: boolean;
}) {
  return (
    <label style={FIELD_WRAP}>
      <span style={FIELD_LABEL}>
        {label}
        {required && <span style={REQUIRED}> *</span>}
      </span>
      {children}
    </label>
  );
}

const PAGE: CSSProperties = {
  minHeight: "100vh",
  backgroundColor: MARKETING.paper,
};

const HERO: CSSProperties = {
  background: `linear-gradient(150deg, ${MARKETING.charcoal} 0%, ${MARKETING.charcoalDeep} 100%)`,
  color: MARKETING.paperCard,
  padding: `${SPACING.xl}px ${SPACING.xl}px 64px`,
};

const HERO_INNER: CSSProperties = {
  maxWidth: 760,
  margin: "0 auto",
};

const KICKER: CSSProperties = {
  fontSize: 13,
  fontWeight: 700,
  letterSpacing: 2.5,
  textTransform: "uppercase",
  color: MARKETING.tealBright,
  margin: `${SPACING.md}px 0 0`,
};

const H1_DARK: CSSProperties = {
  fontSize: 40,
  fontWeight: 700,
  lineHeight: 1.15,
  margin: `${SPACING.md}px 0 0`,
  color: MARKETING.paperCard,
};

const SUB_DARK: CSSProperties = {
  fontSize: 18,
  lineHeight: 1.7,
  color: MARKETING.bodyOnDark,
  margin: `20px 0 0`,
};

const LINK_DARK: CSSProperties = {
  color: MARKETING.tealBright,
};

const BACK_DARK: CSSProperties = {
  color: MARKETING.mutedOnDark,
  textDecoration: "none",
  display: "inline-block",
  fontSize: 15,
};

const CTA_GOLD_BTN: CSSProperties = {
  display: "inline-block",
  backgroundColor: MARKETING.gold,
  color: MARKETING.charcoalDeep,
  border: "none",
  cursor: "pointer",
  padding: `${SPACING.md}px 36px`,
  borderRadius: 28,
  fontSize: TYPOGRAPHY.bodySizePx,
  fontWeight: 700,
  fontFamily: TYPOGRAPHY.fontFamily,
  minHeight: MIN_TOUCH_TARGET.mobile,
};

const FORM_WRAP: CSSProperties = {
  maxWidth: 760,
  margin: "0 auto",
  padding: `${SPACING.xl}px ${SPACING.lg}px`,
};

const FORM_CARD: CSSProperties = {
  background: MARKETING.paperCard,
  border: `1px solid ${MARKETING.paperEdge}`,
  borderRadius: RADIUS.lg,
  padding: SPACING.xl,
};

const INPUT: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  border: `1px solid ${COLORS.disabled}`,
  borderRadius: RADIUS.sm,
  width: "100%",
  boxSizing: "border-box",
  fontFamily: TYPOGRAPHY.fontFamily,
  minHeight: MIN_TOUCH_TARGET.mobile,
  backgroundColor: COLORS.surface,
  color: COLORS.textPrimary,
};

const FIELD_WRAP: CSSProperties = {
  display: "flex",
  flexDirection: "column",
};

const REQUIRED: CSSProperties = {
  color: COLORS.errorConfirm,
};

const PRIVACY_NOTE: CSSProperties = {
  ...BODY,
  fontSize: TYPOGRAPHY.bodySizePx - 1,
  color: COLORS.textPrimary,
  margin: 0,
};

const HONEYPOT: CSSProperties = {
  position: "absolute",
  left: "-9999px",
  top: "-9999px",
  opacity: 0,
  pointerEvents: "none",
};
