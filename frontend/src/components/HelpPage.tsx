/**
 * Help page — four geragogy-compliant self-service articles.
 *
 * Public view (no auth required). Reached via NavBar or inline links
 * on landing, paywall, gift redemption, account settings, and auth
 * error surfaces.
 *
 * Uses only tokens from design/tokens.ts and AccountStyles.ts.
 * Per CONTRACT Section VII: dignity is non-negotiable — no language
 * that infantilizes, rushes, or implies the reader is struggling.
 */

import type { CSSProperties } from "react";
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
import {
  BODY,
  DIVIDER,
  H1,
  H2,
  PAGE,
} from "./AccountStyles";

interface Props {
  onBack: () => void;
}

/* ------------------------------------------------------------------ */
/*  Root                                                               */
/* ------------------------------------------------------------------ */

export default function HelpPage({ onBack }: Props) {
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

      <h1 style={H1}>Help and common questions</h1>

      <nav aria-label="Help sections" style={TOC}>
        <ol style={TOC_LIST}>
          <li>
            <a href="#getting-started" style={TOC_LINK}>
              Getting started with mynaani
            </a>
          </li>
          <li>
            <a href="#how-it-works" style={TOC_LINK}>
              How mynaani works
            </a>
          </li>
          <li>
            <a href="#payments-gifts" style={TOC_LINK}>
              Payments and gifts
            </a>
          </li>
          <li>
            <a href="#your-account" style={TOC_LINK}>
              Your account and support
            </a>
          </li>
        </ol>
      </nav>

      <div style={DIVIDER} />

      <GettingStartedSection />
      <HowItWorksSection />
      <PaymentsGiftsSection />
      <YourAccountSection />
    </main>
  );
}

/* ------------------------------------------------------------------ */
/*  Section 1 — Getting Started                                       */
/* ------------------------------------------------------------------ */

function GettingStartedSection() {
  return (
    <section id="getting-started" style={SECTION}>
      <h2 style={H2}>Getting started with mynaani</h2>

      <div style={BODY}>
        <p>
          Mynaani is a calm, self-paced way to learn what AI is and how to
          use it. You do not need any background in technology. You do not
          need to be fast.
        </p>

        <h3 style={H3}>What you need</h3>
        <ul style={UL}>
          <li>A web browser on a computer, tablet, or phone.</li>
          <li>An email address you can access.</li>
          <li>A quiet moment. There is no time limit.</li>
        </ul>

        <h3 style={H3}>Creating your account</h3>
        <p>
          On the mynaani home page, select "Set up my account — free."
          You will see a short explanation of how mynaani works. After
          that, you can create an account with your email address.
        </p>
        <p>
          The account is free. No payment information is required to
          start learning.
        </p>

        <h3 style={H3}>Signing in and out</h3>
        <p>
          To sign in, select "Sign in" at the top of the page and enter
          your email. To sign out, select your name at the top of the
          page and choose "Sign out." You can sign in again at any time.
        </p>

        <h3 style={H3}>If signing in does not work</h3>
        <p>
          Make sure you are using the same email address you used when you
          created your account. Check your spam folder if you are
          waiting for a confirmation message.
        </p>
        <p>
          If you still cannot sign in, write to
          <a href="mailto:hello@mynaani.com" style={LINK}>
            hello@mynaani.com
          </a>
          and we will help you directly.
        </p>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Section 2 — How Mynaani Works                                     */
/* ------------------------------------------------------------------ */

function HowItWorksSection() {
  return (
    <section id="how-it-works" style={SECTION}>
      <h2 style={H2}>How mynaani works</h2>

      <div style={BODY}>
        <p>
          Mynaani is organized into modules. Each module covers one
          part of learning about AI. You move through the modules at
          your own pace.
        </p>

        <h3 style={H3}>The structure of each module</h3>
        <p>
          Every module contains units. Each unit contains pages that
          follow the same pattern:
        </p>
        <ul style={UL}>
          <li>
            <strong>Recap</strong> — a brief reminder of what the last
            unit covered.
          </li>
          <li>
            <strong>Principle</strong> — the main idea of this unit,
            stated in plain language.
          </li>
          <li>
            <strong>Example</strong> — a familiar situation that shows
            the principle in action.
          </li>
          <li>
            <strong>Retrieval</strong> — a question with two choices.
            You pick the one that fits what you learned. There is no
            time limit.
          </li>
        </ul>

        <h3 style={H3}>Free and paid modules</h3>
        <p>
          Modules 0, 1, 2, and 3 are free. Anyone with an account can
          read them. Modules 4 and 5 require a one-time purchase.
        </p>
        <p>
          When you finish Module 3, you will see a page that explains
          how to continue. You can buy access for yourself or receive
          access as a gift.
        </p>

        <h3 style={H3}>Picking up where you left off</h3>
        <p>
          Mynaani remembers which page you were reading. When you sign
          in again, you will return to that page automatically. You do
          not need to keep track yourself.
        </p>

        <h3 style={H3}>Navigating between units</h3>
        <p>
          At any time, you can open the lesson menu to see all units
          and modules. Select any unit to jump to it. The menu is
          available from the bar at the top of the page.
        </p>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Section 3 — Payments and Gifts                                    */
/* ------------------------------------------------------------------ */

function PaymentsGiftsSection() {
  return (
    <section id="payments-gifts" style={SECTION}>
      <h2 style={H2}>Payments and gifts</h2>

      <div style={BODY}>
        <p>
          Mynaani uses Stripe for payments. Stripe is a service that
          processes card payments securely. Mynaani does not store your
          card number.
        </p>

        <h3 style={H3}>Buying access for yourself</h3>
        <p>
          When you reach the end of Module 3, select "Buy access to
          Modules 4 and 5." You will be taken to a secure checkout
          page. After payment, you can continue reading immediately.
        </p>

        <h3 style={H3}>Buying access as a gift</h3>
        <p>
          You can buy mynaani access for another person. On the
          checkout page, select "Buy as a gift." After payment, you will
          receive a gift token. You can send that token to the
          recipient by email or by printing it.
        </p>

        <h3 style={H3}>Redeeming a gift token</h3>
        <p>
          If you received a gift token, sign in to your mynaani
          account and go to the gift redemption page. Enter the token
          exactly as it was given to you. Select "Redeem." Access will
          be added to your account immediately.
        </p>

        <h3 style={H3}>Refunds</h3>
        <p>
          If you change your mind after buying access, write to
          <a href="mailto:hello@mynaani.com" style={LINK}>
            hello@mynaani.com
          </a>
          within 14 days. We will refund your payment in full.
        </p>

        <h3 style={H3}>Payment security</h3>
        <p>
          Your card details are handled by Stripe, not by mynaani.
          Stripe meets the highest level of payment security
          certification (PCI DSS Level 1). We never see or store your
          card number.
        </p>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Section 4 — Your Account and Support                              */
/* ------------------------------------------------------------------ */

function YourAccountSection() {
  return (
    <section id="your-account" style={SECTION}>
      <h2 style={H2}>Your account and support</h2>

      <div style={BODY}>
        <h3 style={H3}>Signing out</h3>
        <p>
          To sign out, select your name at the top of the page and
          choose "Sign out." This does not delete anything. You can
          sign in again at any time.
        </p>

        <h3 style={H3}>Deleting your account</h3>
        <p>
          You can delete your account from the "Your account" page.
          You will see a clear explanation of what will happen.
          Deletion is scheduled for 30 days later. During those 30
          days, you can cancel the deletion and keep your account.
        </p>
        <p>
          After 30 days, your account and all associated data are
          removed permanently. This cannot be reversed.
        </p>

        <h3 style={H3}>Browser requirements</h3>
        <p>
          Mynaani works on any modern web browser. We recommend:
        </p>
        <ul style={UL}>
          <li>Chrome, version 90 or newer</li>
          <li>Firefox, version 88 or newer</li>
          <li>Safari, version 14 or newer</li>
          <li>Edge, version 90 or newer</li>
        </ul>
        <p>
          If a page does not load correctly, try refreshing the page
          or switching to a different browser.
        </p>

        <h3 style={H3}>Contacting support</h3>
        <p>
          If your question is not answered here, write to us at
          <a href="mailto:hello@mynaani.com" style={LINK}>
            hello@mynaani.com
          </a>
          . We read every message and reply within two business days.
        </p>
        <p>
          For the fastest response, include the email address
          associated with your account and a description of what you
          were doing when the issue occurred.
        </p>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Styles                                                             */
/* ------------------------------------------------------------------ */

const BACK_BTN: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  padding: `${SPACING.xs}px ${SPACING.md}px`,
  marginBottom: SPACING.md,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: 8,
  cursor: "pointer",
  fontFamily: TYPOGRAPHY.fontFamily,
};

const TOC: CSSProperties = {
  marginBottom: SPACING.lg,
};

const TOC_LIST: CSSProperties = {
  listStyle: "none",
  padding: 0,
  margin: 0,
  display: "flex",
  flexDirection: "column",
  gap: `${SPACING.sm}px`,
};

const TOC_LINK: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  color: COLORS.accentMutedBlue,
  textDecoration: "underline",
  fontFamily: TYPOGRAPHY.fontFamily,
};

const SECTION: CSSProperties = {
  marginBottom: SPACING.xl,
};

const H3: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level3,
  marginTop: SPACING.md,
  marginBottom: SPACING.sm,
  color: COLORS.textPrimary,
  fontFamily: TYPOGRAPHY.fontFamily,
};

const UL: CSSProperties = {
  paddingLeft: SPACING.lg,
  marginBottom: SPACING.md,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  textDecoration: "underline",
};
