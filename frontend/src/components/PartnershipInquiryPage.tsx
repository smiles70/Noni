/**
 * Partner inquiry page (/partners).
 *
 * Public form for senior communities, health plans, caregiver networks,
 * and other organizations that want to offer mynaani to the adults they
 * serve. Visual grammar: bid-17 MARKETING tokens (charcoal hero, paper
 * surface, gold CTA) so the page reads as the same product a visitor saw
 * on /for-communities (PS-BID17-021).
 *
 * Submission: POST /api/v1/site/partner-inquiry (backend owns delivery
 * via the transactional email service). If the endpoint is unreachable
 * the form falls back to a mailto: with the same content so an inquiry
 * is never lost. See .ai/research/2026-09-16-footer-form-follow-ups.md.
 *
 * Geragogy: 16px+ fields, labels above inputs, radio buttons (all
 * choices visible — no dropdowns), 44px targets, calm copy, explicit
 * thank-you state. Radio + icon usage documented in ADR.
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
import ChatWidget from "./ChatWidget";

const INQUIRY_EMAIL = "partnerships@mynaani.com";

const ORG_TYPES = [
  "Senior living community",
  "Health plan or insurer",
  "Caregiver network",
  "Other",
] as const;

interface Props {
  onBack: () => void;
}

interface FormState {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  organization: string;
  organizationType: string;
  role: string;
  preferredContact: "email" | "phone";
  message: string;
  /** Honeypot — hidden from humans, bots fill it. */
  website: string;
}

const INITIAL: FormState = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  organization: "",
  organizationType: "",
  role: "",
  preferredContact: "email",
  message: "",
  website: "",
};

export default function PartnershipInquiryPage({ onBack }: Props) {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [fellBack, setFellBack] = useState(false);
  const [contactPhone, setContactPhone] = useState("");

  useEffect(() => {
    let cancelled = false;
    loadFooterContent()
      .then((c) => {
        if (!cancelled) setContactPhone(c.contact_phone || "");
      })
      .catch(() => {
        if (!cancelled) setContactPhone("");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function mailtoHref(): string {
    const subject = `Partner inquiry from ${form.firstName} ${form.lastName}`;
    const body = [
      `Name: ${form.firstName} ${form.lastName}`,
      `Email: ${form.email}`,
      `Phone: ${form.phone || "Not provided"}`,
      `Organization: ${form.organization}`,
      `Organization type: ${form.organizationType || "Not specified"}`,
      `Role: ${form.role || "Not specified"}`,
      `Preferred contact: ${form.preferredContact}`,
      "",
      form.message,
    ].join("\n");
    return `mailto:${INQUIRY_EMAIL}?subject=${encodeURIComponent(
      subject,
    )}&body=${encodeURIComponent(body)}`;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/site/partner-inquiry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: form.firstName,
          last_name: form.lastName,
          email: form.email,
          phone: form.phone,
          organization: form.organization,
          organization_type: form.organizationType,
          role: form.role,
          preferred_contact: form.preferredContact,
          message: form.message,
          website: form.website,
        }),
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      setSubmitted(true);
    } catch {
      // Inquiry must never be lost — fall back to the visitor's mail app.
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
            <p style={KICKER}>Partnerships</p>
            <h1 style={H1_DARK}>Thank you</h1>
            <p style={SUB_DARK}>
              {fellBack
                ? "Your message opened in your email app. If it did not, copy your message and send it to "
                : "We received your note and a member of our team will reply. If you need us sooner, write to "}
              <a href={`mailto:${INQUIRY_EMAIL}`} style={LINK_DARK}>
                {INQUIRY_EMAIL}
              </a>
              .
            </p>
            <button onClick={onBack} style={CTA_GOLD_BTN}>
              Back to mynaani
            </button>
          </div>
        </div>
        <ChatWidget journey="facility" />
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
          <p style={KICKER}>Partnerships</p>
          <h1 style={H1_DARK}>Partner with mynaani</h1>
          <p style={SUB_DARK}>
            If you lead a senior community, health plan, caregiver network, or
            aging-services organization and want to bring confident AI learning
            to the people you serve, tell us about your organization. A member
            of our team will be in touch.
          </p>
          {contactPhone && (
            <p style={SUB_DARK}>
              Prefer to talk? Call us at{" "}
              <a
                href={`tel:${contactPhone.replace(/[^0-9+]/g, "")}`}
                style={LINK_DARK}
                aria-label="Call MyNaani, toll-free"
              >
                {contactPhone}
              </a>{" "}
              (toll-free). The line is answered by our AI receptionist, who can
              connect you to a person when needed.
            </p>
          )}
        </div>
      </div>

      <div style={FORM_WRAP}>
        <form onSubmit={handleSubmit} style={FORM_CARD}>
          <h2 style={{ ...H2, marginTop: 0 }}>Request information</h2>

          <div style={STACK}>
            <fieldset style={FIELDSET}>
              <legend style={LEGEND}>
                What best describes your organization?
              </legend>
              {ORG_TYPES.map((opt) => (
                <label key={opt} style={RADIO_ROW}>
                  <input
                    type="radio"
                    name="organizationType"
                    value={opt}
                    checked={form.organizationType === opt}
                    onChange={(e) => update("organizationType", e.target.value)}
                    style={RADIO}
                    required
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </fieldset>

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
            <Field label="Work email" required>
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
            <Field label="Organization" required>
              <input
                type="text"
                name="organization"
                value={form.organization}
                onChange={(e) => update("organization", e.target.value)}
                style={INPUT}
                required
                autoComplete="organization"
              />
            </Field>
            <Field label="Your role">
              <input
                type="text"
                name="role"
                value={form.role}
                onChange={(e) => update("role", e.target.value)}
                style={INPUT}
                autoComplete="organization-title"
              />
            </Field>
            <fieldset style={FIELDSET}>
              <legend style={LEGEND}>How should we get back to you?</legend>
              <label style={RADIO_ROW}>
                <input
                  type="radio"
                  name="preferredContact"
                  value="email"
                  checked={form.preferredContact === "email"}
                  onChange={(e) =>
                    update("preferredContact", e.target.value as "email")
                  }
                  style={RADIO}
                />
                <span>Email me</span>
              </label>
              <label style={RADIO_ROW}>
                <input
                  type="radio"
                  name="preferredContact"
                  value="phone"
                  checked={form.preferredContact === "phone"}
                  onChange={(e) =>
                    update("preferredContact", e.target.value as "phone")
                  }
                  style={RADIO}
                />
                <span>Call me</span>
              </label>
            </fieldset>

            <Field
              label={
                form.preferredContact === "phone" ? "Phone" : "Phone (optional)"
              }
              required={form.preferredContact === "phone"}
            >
              <input
                type="tel"
                name="phone"
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
                style={INPUT}
                autoComplete="tel"
                required={form.preferredContact === "phone"}
              />
            </Field>
            <Field label="How can we help?">
              <textarea
                name="message"
                value={form.message}
                onChange={(e) => update("message", e.target.value)}
                style={{ ...INPUT, minHeight: 120 }}
                rows={4}
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
              {submitting ? "Sending…" : "Send inquiry"}
            </button>
            <p style={PRIVACY_NOTE}>
              We only use these details to reply about a partnership — no
              marketing list, no sharing.
            </p>
          </div>
        </form>
      </div>
      <ChatWidget journey="facility" />
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

const FIELDSET: CSSProperties = {
  border: "none",
  padding: 0,
  margin: 0,
  display: "flex",
  flexDirection: "column",
  gap: SPACING.sm,
};

const LEGEND: CSSProperties = {
  ...FIELD_LABEL,
  padding: 0,
  marginBottom: SPACING.xs,
};

const RADIO_ROW: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: SPACING.sm,
  minHeight: MIN_TOUCH_TARGET.mobile,
  fontSize: TYPOGRAPHY.bodySizePx,
  cursor: "pointer",
};

const RADIO: CSSProperties = {
  width: 22,
  height: 22,
  accentColor: MARKETING.teal,
  cursor: "pointer",
  flexShrink: 0,
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
