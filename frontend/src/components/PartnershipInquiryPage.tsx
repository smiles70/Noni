/**
 * Partner inquiry page (/partners).
 *
 * Public form for senior communities, health plans, caregiver networks,
 * and other organizations that want to offer mynaani to the adults they
 * serve. Modeled on the GetSetUp contact/demo pattern: a short,
 * plain-language form that asks for the details a partnership team needs.
 *
 * Submission: the form builds a mailto: message as a pragmatic interim
 * until a backend email/CRM integration is added. A true enterprise
 * pattern is a server-side form; see the research memo.
 *
 * Geragogy: large labels, 16px+ fields, calm copy, no dropdowns, no
 * urgency, explicit confirmation.
 */

import { useState, type CSSProperties, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import {
  BODY,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  FIELD,
  FIELD_LABEL,
  STACK,
} from "./AccountStyles";

const INQUIRY_EMAIL = "partnerships@mynaani.com";

interface Props {
  onBack: () => void;
}

interface FormState {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  organization: string;
  role: string;
  message: string;
}

const INITIAL: FormState = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  organization: "",
  role: "",
  message: "",
};

export default function PartnershipInquiryPage({ onBack }: Props) {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitted, setSubmitted] = useState(false);

  function update<K extends keyof FormState>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const subject = `Partner inquiry from ${form.firstName} ${form.lastName}`;
    const body = [
      `Name: ${form.firstName} ${form.lastName}`,
      `Email: ${form.email}`,
      `Phone: ${form.phone || "Not provided"}`,
      `Organization: ${form.organization}`,
      `Role: ${form.role}`,
      "",
      form.message,
    ].join("\n");
    const mailto = `mailto:${INQUIRY_EMAIL}?subject=${encodeURIComponent(
      subject,
    )}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <main style={PAGE}>
        <h1 style={H1}>Thank you</h1>
        <p style={BODY}>
          If your email app did not open, copy your message and send it to{" "}
          <a href={`mailto:${INQUIRY_EMAIL}`} style={LINK}>
            {INQUIRY_EMAIL}
          </a>
          .
        </p>
        <button onClick={onBack} style={PRIMARY_BTN}>
          Back to mynaani
        </button>
      </main>
    );
  }

  return (
    <main style={PAGE}>
      <Link
        to="/"
        style={BACK}
        onClick={(e) => {
          e.preventDefault();
          onBack();
        }}
      >
        ← Back to mynaani
      </Link>
      <h1 style={H1}>Partner with mynaani</h1>
      <p style={BODY}>
        If you lead a senior community, health plan, caregiver network, or
        aging-services organization and want to bring confident AI learning to
        the people you serve, tell us about your organization. A member of our
        team will be in touch.
      </p>

      <h2 style={H2}>Request information</h2>
      <form onSubmit={handleSubmit} style={FORM}>
        <div style={STACK}>
          <FormField label="First name" required>
            <input
              type="text"
              value={form.firstName}
              onChange={(e) => update("firstName", e.target.value)}
              style={INPUT}
              required
            />
          </FormField>
          <FormField label="Last name" required>
            <input
              type="text"
              value={form.lastName}
              onChange={(e) => update("lastName", e.target.value)}
              style={INPUT}
              required
            />
          </FormField>
          <FormField label="Work email" required>
            <input
              type="email"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              style={INPUT}
              required
            />
          </FormField>
          <FormField label="Phone (optional)">
            <input
              type="tel"
              value={form.phone}
              onChange={(e) => update("phone", e.target.value)}
              style={INPUT}
            />
          </FormField>
          <FormField label="Organization" required>
            <input
              type="text"
              value={form.organization}
              onChange={(e) => update("organization", e.target.value)}
              style={INPUT}
              required
            />
          </FormField>
          <FormField label="Your role" required>
            <input
              type="text"
              value={form.role}
              onChange={(e) => update("role", e.target.value)}
              style={INPUT}
              required
            />
          </FormField>
          <FormField label="How can we help?">
            <textarea
              value={form.message}
              onChange={(e) => update("message", e.target.value)}
              style={{ ...INPUT, minHeight: 120 }}
              rows={4}
            />
          </FormField>
          <button type="submit" style={PRIMARY_BTN}>
            Send inquiry
          </button>
        </div>
      </form>
    </main>
  );
}

function FormField({
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

const INPUT: CSSProperties = {
  ...FIELD,
  minHeight: MIN_TOUCH_TARGET.mobile,
};

const FORM: CSSProperties = {
  marginTop: SPACING.xl,
};

const FIELD_WRAP: CSSProperties = {
  display: "flex",
  flexDirection: "column",
};

const REQUIRED: CSSProperties = {
  color: COLORS.errorConfirm,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
};

const BACK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "none",
  display: "inline-block",
  marginBottom: SPACING.md,
};
