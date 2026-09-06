/**
 * Privacy page — plain-language statement of what we collect, what we
 * never collect, and who can see progress.
 *
 * Public view (no auth required). Trust rubric T1/T3/T7: for an audience
 * whose top adoption barrier is data privacy (AARP 2025), the good
 * practices we already follow must be visible, not implied.
 *
 * Geragogy contract: calm, dignified, no urgency, no legalese. Uses only
 * design tokens and AccountStyles — same visual language as /help.
 */

import type { CSSProperties } from "react";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import { BODY, DIVIDER, H1, H2, PAGE } from "./AccountStyles";

interface Props {
  onBack: () => void;
}

export default function PrivacyPage({ onBack }: Props) {
  return (
    <main style={PAGE}>
      <button
        type="button"
        onClick={onBack}
        style={BACK_BTN}
        aria-label="Go back"
      >
        ← Back
      </button>

      <h1 style={H1}>Your privacy on mynaani</h1>

      <p style={BODY}>
        This page explains, in plain language, what information we keep and
        what we never collect. If anything here is unclear, the "Help and
        common questions" page has more detail, and you can always write to
        us.
      </p>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>What we keep</h2>
        <div style={BODY}>
          <p>To provide your lessons, we keep only what is needed:</p>
          <ul style={UL}>
            <li>Your email address, so you can sign in.</li>
            <li>
              Which lessons you have started and completed, so you can pick
              up where you left off.
            </li>
            <li>
              If you joined through a gift or a community program, the code
              you used.
            </li>
          </ul>
          <p>
            That is the whole list. We do not collect anything else about
            you.
          </p>
        </div>
      </section>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>What we never collect</h2>
        <div style={BODY}>
          <ul style={UL}>
            <li>Your contacts, photos, or files.</li>
            <li>Your location.</li>
            <li>
              What you do on other websites or in other apps.
            </li>
            <li>
              Your card or bank details. Payment is handled on Stripe's
              secure checkout page; card numbers never reach our system.
            </li>
          </ul>
        </div>
      </section>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>Who can see your progress</h2>
        <div style={BODY}>
          <p>
            Your lesson progress belongs to you. If you joined through a
            senior center or community program, the staff there can see
            whether an access code was used — they cannot see your lessons,
            your answers, or your activity.
          </p>
          <p>
            We do not sell or share your information with advertisers, and
            we do not use tracking cookies for advertising.
          </p>
        </div>
      </section>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>The services we use</h2>
        <div style={BODY}>
          <p>
            A small number of specialist companies help us run mynaani. Each
            handles only what it needs to:</p>
          <ul style={UL}>
            <li>Stripe — processes payments; card details go to them, not us.</li>
            <li>Magic.link — sends your sign-in link and verifies it.</li>
            <li>Railway — hosts the service and its database.</li>
            <li>Cloudflare — delivers pages quickly and safely.</li>
          </ul>
          <p>
            We do not use advertising networks or data brokers. A data
            processing agreement is available to community and institutional
            partners on request.
          </p>
        </div>

        <h2 style={H2}>Reporting a concern</h2>
        <div style={BODY}>
          <p>
            If you believe you have found a security problem, or something
            about your information worries you, write to us at{" "}
            <a href="mailto:hello@mynaani.com" style={LINK}>
              hello@mynaani.com
            </a>
            . We reply within two business days.
          </p>
        </div>

        <h2 style={H2}>Removing your information</h2>
        <div style={BODY}>
          <p>
            You can delete your account at any time from the "Your account"
            page. Deletion is scheduled 30 days later, and you can cancel
            it during that time. After 30 days your account and associated
            data are removed permanently.
          </p>
          <p>
            Your information travels to us over an encrypted connection. We
            keep your account and progress for as long as your account
            exists. Purchase records are kept as required for tax purposes.
          </p>
          <p>
            Questions are always welcome at{" "}
            <a href="mailto:hello@mynaani.com" style={LINK}>
              hello@mynaani.com
            </a>
            . We reply within two business days.
          </p>
        </div>
      </section>
    </main>
  );
}

const UL: CSSProperties = {
  paddingLeft: SPACING.lg,
  margin: `${SPACING.sm}px 0`,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
};

const BACK_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.xs}px ${SPACING.md}px`,
  minHeight: MIN_TOUCH_TARGET.mobile,
  marginBottom: SPACING.md,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
};
