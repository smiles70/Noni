/**
 * Terms of Service — plain-language terms, structured to match the
 * proven PrivacyPage voice ("you/we", short sections, no legalese).
 *
 * Public view (no auth required). Covers the standard ToS checklist
 * (acceptance, eligibility, account, service, payment, refunds, gifts,
 * acceptable use, IP, disclaimers, termination, changes, contact)
 * adapted to mynaani's actual product: one-time access purchase, gift
 * tokens, community access codes. ISO 21800 + UK BEIS evidence: Q&A-ish
 * headings and short sections measurably improve comprehension.
 *
 * Geragogy contract: calm, dignified, no legalese. Design tokens only.
 */

import type { CSSProperties } from "react";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";
import { BODY, DIVIDER, H1, H2, PAGE } from "./AccountStyles";

interface Props {
  onBack: () => void;
}

export default function TermsPage({ onBack }: Props) {
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

      <h1 style={H1}>Terms of Service</h1>

      <p style={BODY}>
        These are the rules for using mynaani, written in plain language. They
        were last updated in September 2026. If anything here is unclear, write
        to us at{" "}
        <a href="mailto:help@mynaani.com" style={LINK}>
          help@mynaani.com
        </a>{" "}
        before you sign up or buy.
      </p>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>What you are agreeing to</h2>
        <div style={BODY}>
          <p>
            By creating an account, buying access, or redeeming a gift, you
            agree to these terms. If you do not agree, please do not use the
            service.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>Who can use mynaani</h2>
        <div style={BODY}>
          <p>
            Mynaani is designed for adults. You must be at least 18 years old,
            or old enough to agree to a contract where you live, and you must
            sign in with an email address that belongs to you.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>Your account</h2>
        <div style={BODY}>
          <p>
            You sign in with a link we email to you — there is no password to
            remember. Keep your email account secure, since anyone who can read
            your email can sign in as you. Your account is for you; please do
            not share your sign-in link or your account with others.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>What mynaani is</h2>
        <div style={BODY}>
          <p>
            Mynaani is an online curriculum that teaches adults how to
            understand and use AI tools, in plain language, at your own pace. It
            is educational material — it is not professional, legal, medical, or
            financial advice.
          </p>
          <p>
            We may update lessons and features over time to keep them accurate
            and useful. We will not remove access you have already paid for.
          </p>
        </div>
      </section>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>Paying for access</h2>
        <div style={BODY}>
          <p>
            Buying access is a one-time purchase that unlocks Modules 2, 3, 4,
            and 5 — it is not a subscription, and nothing renews or bills again.
            Payment is handled by Stripe on their secure checkout page; we never
            see or store your card number.
          </p>
        </div>

        <h2 style={H2}>Refunds</h2>
        <div style={BODY}>
          <p>
            If you change your mind, write to us within 30 days of purchase for
            a full refund. Because access is immediate and complete, we ask that
            you have finished less than half of the paid modules — that keeps
            the promise fair for everyone.
          </p>
        </div>

        <h2 style={H2}>Gifts</h2>
        <div style={BODY}>
          <p>
            You can buy access for someone else as a gift. After payment you
            receive a gift token to pass on to them. A gift token can be
            redeemed once, by the person you give it to. If a gift is refunded,
            the refund goes to the person who paid.
          </p>
        </div>

        <h2 style={H2}>Community programs</h2>
        <div style={BODY}>
          <p>
            If you joined through a senior center or community program, an
            access code may have been provided for you. Staff there can see
            whether a code was used — they cannot see your lessons, your
            answers, or your activity.
          </p>
        </div>
      </section>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>Using mynaani fairly</h2>
        <div style={BODY}>
          <p>Please do not:</p>
          <ul style={UL}>
            <li>share your account or your sign-in link,</li>
            <li>copy, resell, or republish the lessons,</li>
            <li>try to break into, scrape, or interfere with the service,</li>
            <li>use mynaani for anything unlawful.</li>
          </ul>
          <p>
            If an account is used in these ways, we may suspend or close it.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>Who owns what</h2>
        <div style={BODY}>
          <p>
            The mynaani lessons, design, and software belong to us. Your account
            and your progress information belong to you — you can delete them at
            any time.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>What we do not promise</h2>
        <div style={BODY}>
          <p>
            We work hard to keep mynaani available and accurate, but the service
            is provided "as is." We cannot promise it will always be
            uninterrupted or error-free, and we are not liable for losses caused
            by things outside our reasonable control. Where the law does not
            allow us to limit our responsibility, this section does not apply.
          </p>
        </div>
      </section>

      <div style={DIVIDER} />

      <section>
        <h2 style={H2}>Ending your account</h2>
        <div style={BODY}>
          <p>
            You can delete your account at any time from the "Your account"
            page. Deletion is scheduled 30 days later, and you can cancel it
            during that time. We may close accounts that break these terms,
            after contacting you first where we reasonably can.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>Changes to these terms</h2>
        <div style={BODY}>
          <p>
            If we change these terms, we will update this page and change the
            date at the top. For significant changes we will also tell you by
            email or on the site. Continuing to use mynaani after a change means
            you accept the new terms.
          </p>
        </div>
      </section>

      <section>
        <h2 style={H2}>If something goes wrong</h2>
        <div style={BODY}>
          <p>
            Talk to us first — most problems can be fixed by writing to{" "}
            <a href="mailto:help@mynaani.com" style={LINK}>
              help@mynaani.com
            </a>
            . These terms are governed by the laws of the State of Delaware,
            United States.
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
