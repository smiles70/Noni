/**
 * Noni root component.
 *
 * Simple view-state machine (no router). Sprint A8 adds account/billing
 * views; landing and curriculum are unchanged. The curriculum -> paywall
 * trigger is wired in once the curriculum renderer surfaces it; for now
 * the additional views are reachable in dev via direct setView calls
 * (e.g. from a debug surface or future settings entry on landing).
 */
import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import LandingPage from "./components/LandingPage";
import CurriculumRenderer from "./components/CurriculumRenderer";
import SignInPage from "./components/SignInPage";
import PaywallPage from "./components/PaywallPage";
import GiftRedeemPage from "./components/GiftRedeemPage";
import AccountSettingsPage from "./components/AccountSettingsPage";
import ClerkAuthBridge from "./components/ClerkAuthBridge";
import { whoami } from "./api/auth";

// Build-time selector. Mock keeps the dev/test path; clerk turns on the
// ClerkAuthBridge + the <SignIn /> widget inside SignInPage.
const AUTH_PROVIDER =
  ((import.meta as unknown as { env?: { VITE_AUTH_PROVIDER?: string } }).env
    ?.VITE_AUTH_PROVIDER ?? "mock");

type View =
  | "landing"
  | "curriculum"
  | "signin"
  | "paywall"
  | "gift_redeem"
  | "account"
  | "oauth_finishing";

// Views that require an authenticated session. Unauthenticated users
// hitting these are bounced to "signin" and forwarded after success.
const GATED_VIEWS: ReadonlySet<View> = new Set<View>([
  "curriculum",
  "paywall",
  "gift_redeem",
  "account",
]);

const App: React.FC = () => {
  const [view, setView] = useState<View>("landing");
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  // Where to land after a successful sign-in (e.g. user clicked "Begin"
  // while signed out -> we remember "curriculum" and forward post-auth).
  const [pendingView, setPendingView] = useState<View | null>(null);

  // On mount: ask the backend whether a session already exists so route
  // gating works correctly. With AUTH_PROVIDER=mock the user explicitly
  // signs in via SignInPage; with Clerk (post-ADR-0024) Clerk's session
  // is exchanged for our HttpOnly cookie via POST /auth/callback before
  // this whoami runs.
  useEffect(() => {
    whoami()
      .then((res) => setSignedIn(res?.has_active_session === true))
      .catch(() => setSignedIn(false));
  }, []);

  const goLanding = () => setView("landing");
  // Gate: signed-out callers are routed through sign-in and forwarded.
  const requireAuth = (target: View) => {
    if (signedIn === false) {
      setPendingView(target);
      setView("signin");
    } else {
      setView(target);
    }
  };
  const goCurriculum = () => requireAuth("curriculum");
  const goSignIn = () => setView("signin");
  const goPaywall = () => requireAuth("paywall");
  const goAccount = () => requireAuth("account");

  // Successful sign-in: forward to the intent (e.g. curriculum) the user
  // had before being bounced. Falls back to curriculum so a returning user
  // who clicked "Sign in" lands inside the app, not back on marketing.
  const handleSignedIn = () => {
    setSignedIn(true);
    const next = pendingView ?? "curriculum";
    setPendingView(null);
    setView(next);
  };

  // ClerkAuthBridge is a render-null component that uses Clerk hooks to
  // forward Clerk's session token to our backend. Only mount it when
  // Clerk is the configured provider AND its provider is in the tree
  // (main.tsx). Mounting under mock would call useAuth() without a
  // ClerkProvider and crash.
  const authBridge =
    AUTH_PROVIDER === "clerk" ? <ClerkAuthBridge /> : null;

  // Resolve the active view to a React node, then wrap it together with
  // the bridge so we never duplicate the auth-bridge mount across six
  // separate return statements.
  let body: ReactNode;

  if (signedIn === null && view !== "oauth_finishing") {
    body = (
      <main aria-live="polite" data-component="PendingBanner">
        <p>One moment — loading.</p>
      </main>
    );
  } else if (signedIn === false && GATED_VIEWS.has(view)) {
    body = (
      <SignInPage onSignedIn={handleSignedIn} onCancel={goLanding} />
    );
  } else {
    switch (view) {
      case "landing":
        body = (
          <LandingPage
            onBegin={goCurriculum}
            onSignIn={goSignIn}
            onContinuePaid={goPaywall}
            onAccount={goAccount}
          />
        );
        break;
      case "curriculum":
        body = (
          <CurriculumRenderer
            onReturn={goLanding}
            onSignIn={goSignIn}
            onContinuePaid={goPaywall}
            onAccount={goAccount}
          />
        );
        break;
      case "signin":
        body = (
          <SignInPage onSignedIn={handleSignedIn} onCancel={goLanding} />
        );
        break;
      case "paywall":
        body = (
          <PaywallPage
            productCode="modules_4_5"
            onRedeemGift={() => setView("gift_redeem")}
            onBack={goLanding}
          />
        );
        break;
      case "gift_redeem":
        body = (
          <GiftRedeemPage
            onClaimed={goCurriculum}
            onBack={() => setView("paywall")}
          />
        );
        break;
      case "account":
        body = (
          <AccountSettingsPage
            onSignedOut={goLanding}
            onDeleted={goLanding}
            onBack={goLanding}
          />
        );
        break;
      case "oauth_finishing":
        body = (
          <main aria-live="polite" data-component="PendingBanner">
            <p>One moment — finishing sign in.</p>
          </main>
        );
        break;
    }
  }

  return (
    <>
      {authBridge}
      {body}
    </>
  );
};

export default App;
