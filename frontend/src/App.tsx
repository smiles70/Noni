/**
 * Noni root component.
 *
 * Simple view-state machine (no router). Sprint A8 adds account/billing
 * views; landing and curriculum are unchanged. The curriculum -> paywall
 * trigger is wired in once the curriculum renderer surfaces it; for now
 * the additional views are reachable in dev via direct setView calls
 * (e.g. from a debug surface or future settings entry on landing).
 */
import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import LandingPage from "./components/LandingPage";
import CurriculumRenderer from "./components/CurriculumRenderer";
import CurriculumMenu from "./components/CurriculumMenu";
import SignInPage from "./components/SignInPage";
import PaywallPage from "./components/PaywallPage";
import GiftRedeemPage from "./components/GiftRedeemPage";
import AccountSettingsPage from "./components/AccountSettingsPage";
import ClerkAuthSync from "./components/ClerkAuthSync";
import { whoami } from "./api/auth";

// Build-time selector. Mock keeps the dev/test path; clerk turns on the
// <SignIn /> widget inside SignInPage and mounts ClerkAuthSync to
// observe Clerk's hook-based auth state (ADR 0024).
const AUTH_PROVIDER =
  ((import.meta as unknown as { env?: { VITE_AUTH_PROVIDER?: string } }).env
    ?.VITE_AUTH_PROVIDER ?? "mock");

type View =
  | "landing"
  | "curriculum"
  | "menu"
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

  // Single source of truth for the auth check. Called on mount (mock
  // mode) or by ClerkAuthSync once Clerk has hydrated (clerk mode), and
  // re-called after every sign-in / sign-out transition.
  const refreshAuth = useCallback(async () => {
    try {
      const me = await whoami();
      setSignedIn(me?.has_active_session === true);
    } catch {
      setSignedIn(false);
    }
  }, []);

  useEffect(() => {
    // In clerk mode we deliberately defer the first whoami until
    // ClerkAuthSync fires its onAuthChanged: window.Clerk.session
    // isn't available until the SDK finishes hydrating, so an
    // immediate call would race the SDK and resolve signed-out for
    // ~100-500ms (causing a CTA flicker on the landing page).
    if (AUTH_PROVIDER === "mock") {
      void refreshAuth();
    }
  }, [refreshAuth]);

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
  // Menu is intentionally public: a visitor may browse the syllabus
  // before signing up. The unit renderer (curriculum view) is still
  // gated, so following Continue from the menu still routes through
  // requireAuth via goCurriculum.
  const goMenu = () => setView("menu");

  // Successful sign-in: forward to the intent (e.g. curriculum) the
  // user had before being bounced. Falls back to curriculum so a
  // returning user who clicked "Sign in" lands inside the app, not
  // back on marketing. Awaits refreshAuth so the next render sees
  // signedIn=true and gated views actually render.
  const handleSignedIn = async () => {
    await refreshAuth();
    const next = pendingView ?? "curriculum";
    setPendingView(null);
    setView(next);
  };

  const handleSignedOut = async () => {
    await refreshAuth();
    setView("landing");
  };

  // Clerk's hook state changes are asynchronous: ClerkAuthSync may
  // fire because (a) the SDK just finished hydrating on a returning
  // visit, (b) the user just signed in via the <SignIn /> widget, or
  // (c) the user signed out in another tab. We treat them all the
  // same — re-fetch whoami — except we only auto-advance the view
  // when the user is on the signin screen (case b).
  const handleClerkAuthChanged = useCallback(async () => {
    await refreshAuth();
    if (view === "signin") {
      const next = pendingView ?? "curriculum";
      setPendingView(null);
      setView(next);
    }
  }, [refreshAuth, view, pendingView]);

  // ClerkAuthSync is render-null and uses Clerk hooks; only mount it
  // under ClerkProvider (i.e. when AUTH_PROVIDER === "clerk"). Mounting
  // in mock mode would crash because there's no ClerkProvider in the
  // tree.
  const clerkSync =
    AUTH_PROVIDER === "clerk" ? (
      <ClerkAuthSync onAuthChanged={handleClerkAuthChanged} />
    ) : null;

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
            signedIn={signedIn === true}
            onSignOut={handleSignedOut}
          />
        );
        break;
      case "curriculum":
        body = (
          <CurriculumRenderer
            onSignIn={goSignIn}
            onContinueGated={goPaywall}
            onAccount={goAccount}
            onOpenMenu={goMenu}
          />
        );
        break;
      case "menu":
        body = (
          <CurriculumMenu
            onContinue={goCurriculum}
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
            onSignedOut={handleSignedOut}
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
      {clerkSync}
      {body}
    </>
  );
};

export default App;
