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
import CurriculumMenu from "./components/CurriculumMenu";
import SignInPage from "./components/SignInPage";
import PaywallPage from "./components/PaywallPage";
import GiftRedeemPage from "./components/GiftRedeemPage";
import AccountSettingsPage from "./components/AccountSettingsPage";
import AuthPendingBanner from "./components/AuthPendingBanner";
import AuthBlockedNotice from "./components/AuthBlockedNotice";
import { useAuth } from "./auth/AuthProvider";

// Step 3 of the FE cutover plan: temporary debug surface that prints
// the AuthProvider state in the corner of every page so we can watch
// the BOOT -> AUTHENTICATING -> READY (or REJECTED / TRANSIENT_ERROR)
// transitions happen live. Removed in Step 12.
function DebugAuth() {
  const ctx = useAuth();
  const state = ctx?.state ?? { status: "no-context" };
  return (
    <pre
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        zIndex: 9999,
        margin: 0,
        padding: "6px 8px",
        background: "rgba(0,0,0,0.75)",
        color: "#0f0",
        font: "11px/1.3 ui-monospace, monospace",
        maxWidth: "40vw",
        whiteSpace: "pre-wrap",
        pointerEvents: "none",
      }}
    >
      {JSON.stringify(state, null, 2)}
    </pre>
  );
}

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
  // AuthProvider is the ONLY source of auth truth (FE Step-4 cutover).
  // App.tsx remains the orchestrator of routing + intent (pendingView).
  const { state, signOut } = useAuth();
  const [view, setView] = useState<View>("landing");
  // Where to land after a successful sign-in (e.g. user clicked "Begin"
  // while signed out -> we remember "curriculum" and forward post-auth).
  const [pendingView, setPendingView] = useState<View | null>(null);

  const isReady = state?.status === "READY";

  // Resolve pendingView after AuthProvider transitions to READY.
  useEffect(() => {
    if (isReady && pendingView) {
      setView(pendingView);
      setPendingView(null);
    }
  }, [isReady, pendingView]);

  const goLanding = () => setView("landing");
  const goSignIn = () => setView("signin");
  const goMenu = () => setView("menu");
  // Gate: signed-out callers are routed through sign-in and forwarded.
  const requireAuth = (target: View) => {
    if (isReady) {
      setView(target);
    } else {
      setPendingView(target);
      setView("signin");
    }
  };
  const goCurriculum = () => requireAuth("curriculum");
  const goPaywall = () => requireAuth("paywall");
  const goAccount = () => requireAuth("account");

  // Always-mounted debug surface so we can observe AuthProvider state
  // even during BOOT / AUTHENTICATING / REJECTED early returns.
  // F1: dev-only — Vite strips this branch from prod bundles via the
  // `import.meta.env.DEV` constant, so internal state never leaks to
  // production users.
  const debug = (import.meta as unknown as { env?: { DEV?: boolean } }).env
    ?.DEV
    ? <DebugAuth />
    : null;

  // Global gates: AuthProvider state takes precedence over `view`.
  const status = state?.status;
  if (status === "BOOT" || status === "AUTHENTICATING") {
    return (
      <>
        {debug}
        <main aria-live="polite" data-component="PendingBanner">
          <p>One moment — loading.</p>
        </main>
      </>
    );
  }
  if (status === "REJECTED") {
    // F6: discriminated, dignified copy per AuthError code; raw codes
    // never reach the user. onSignIn clears the rejected credential
    // (-> SIGNED_OUT) and routes to the sign-in page.
    const handleSignInAgain = async () => {
      try { await signOut(); } catch { /* idempotent */ }
      setView("signin");
    };
    return (
      <>
        {debug}
        <main data-component="BlockedNotice">
          <AuthBlockedNotice
            errorCode={state?.errorCode}
            onSignIn={handleSignInAgain}
          />
        </main>
      </>
    );
  }

  // SIGNED_OUT + TRANSIENT_ERROR + READY all reach the view switch.
  // Public views (landing, menu, signin) render in any state.
  // Gated views (curriculum, paywall, gift_redeem, account) render only
  // when state.status === "READY"; otherwise we show SignInPage so the
  // user can sign in and pendingView forwards them once READY fires.
  const onSignInPage = (
    <SignInPage onSignedIn={() => {}} onCancel={goLanding} />
  );

  if (!isReady && GATED_VIEWS.has(view)) {
    return (
      <>
        {debug}
        {onSignInPage}
      </>
    );
  }

  let body: ReactNode;
  switch (view) {
    case "landing":
      body = (
        <LandingPage
          onBegin={goCurriculum}
          onSignIn={goSignIn}
          onContinuePaid={goPaywall}
          onAccount={goAccount}
          signedIn={isReady}
          onSignOut={signOut}
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
      body = onSignInPage;
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
          onSignedOut={signOut}
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

  // F6: TRANSIENT_ERROR surfaces a non-alarming reconnect banner above
  // the current view. Per I-A, signed-in is sticky on transient backend
  // failures, so we keep rendering `body` underneath. Retry = full reload
  // (simple, predictable; AuthProvider re-runs the boot probe).
  const transientBanner =
    status === "TRANSIENT_ERROR" ? (
      <AuthPendingBanner onRetry={() => window.location.reload()} />
    ) : null;

  return (
    <>
      {debug}
      {transientBanner}
      {body}
    </>
  );
};

export default App;
