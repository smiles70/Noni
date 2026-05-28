/**
 * Noni root component.
 *
 * Simple view-state machine (no router). Sprint A8 adds account/billing
 * views; landing and curriculum are unchanged. The curriculum -> paywall
 * trigger is wired in once the curriculum renderer surfaces it; for now
 * the additional views are reachable in dev via direct setView calls
 * (e.g. from a debug surface or future settings entry on landing).
 */
import { Suspense, lazy, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import LandingPage from "./components/LandingPage";
import SignInPage from "./components/SignInPage";
import AuthPendingBanner from "./components/AuthPendingBanner";
import AuthBlockedNotice from "./components/AuthBlockedNotice";
import LoadingSkeleton from "./components/LoadingSkeleton";
import { useAuth } from "./auth/AuthProvider";
import { readProgress, writeProgress } from "./lib/progress";
import { IS_DEV } from "./lib/env";
import { ViewportProvider } from "./context/ViewportContext";
import { ResponsiveContainer } from "./components/ResponsiveContainer";

// Sprint 28-B.1: lazy-load non-landing views to reduce initial bundle.
const CurriculumRenderer = lazy(() => import("./components/CurriculumRenderer"));
const PaidLessonRenderer = lazy(() => import("./components/PaidLessonRenderer"));
const CurriculumMenu = lazy(() => import("./components/CurriculumMenu"));
const PaywallPage = lazy(() => import("./components/PaywallPage"));
const GiftRedeemPage = lazy(() => import("./components/GiftRedeemPage"));
const AccountSettingsPage = lazy(() => import("./components/AccountSettingsPage"));
const HelpPage = lazy(() => import("./components/HelpPage"));

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
  | "paid_curriculum"
  | "menu"
  | "signin"
  | "paywall"
  | "gift_redeem"
  | "account"
  | "help"
  | "oauth_finishing";

// Views that require an authenticated session. Unauthenticated users
// hitting these are bounced to "signin" and forwarded after success.
const GATED_VIEWS: ReadonlySet<View> = new Set<View>([
  "curriculum",
  "paid_curriculum",
  "paywall",
  "gift_redeem",
  "account",
]);

const App: React.FC = () => {
  // AuthProvider is the ONLY source of auth truth (FE Step-4 cutover).
  // App.tsx remains the orchestrator of routing + intent (pendingView).
  const { state, signOut } = useAuth();
  // Sprint 28-B.10: restore view from sessionStorage on boot so learners
  // resume where they left off after refresh.
  const [view, setView] = useState<View>(() => {
    try {
      const saved = sessionStorage.getItem("noni.view");
      if (saved && (GATED_VIEWS as ReadonlySet<string>).has(saved)) {
        return saved as View;
      }
    } catch {
      // private mode / quota — silently fall back to landing
    }
    return "landing";
  });
  // Where to land after a successful sign-in (e.g. user clicked "Begin"
  // while signed out -> we remember "curriculum" and forward post-auth).
  const [pendingView, setPendingView] = useState<View | null>(null);
  // Sprint 28 quick-win: race-condition guard so a flickering isReady
  // (e.g. Clerk token refresh) cannot consume pendingView twice.
  const pendingConsumedRef = useRef(false);

  // Persist view changes to sessionStorage.
  useEffect(() => {
    try {
      sessionStorage.setItem("noni.view", view);
    } catch {
      /* silently ignore quota errors */
    }
  }, [view]);

  const isReady = state?.status === "READY";

  // Resolve pendingView after AuthProvider transitions to READY.
  useEffect(() => {
    if (isReady && pendingView && !pendingConsumedRef.current) {
      pendingConsumedRef.current = true;
      setView(pendingView);
      setPendingView(null);
    }
  }, [isReady, pendingView]);

  const goLanding = () => setView("landing");
  const goSignIn = () => setView("signin");
  const goMenu = () => setView("menu");
  const goHelp = () => setView("help");
  // Gate: signed-out callers are routed through sign-in and forwarded.
  const requireAuth = (target: View) => {
    if (isReady) {
      setView(target);
    } else {
      setPendingView(target);
      setView("signin");
    }
  };
  // Cross-track resume: check saved progress and route to the correct
  // track so a returning learner picks up in M1-3 or M4-5 as appropriate.
  const goCurriculum = () => {
    const saved = readProgress();
    if (saved && (saved.module === 4 || saved.module === 5)) {
      requireAuth("paid_curriculum");
    } else {
      requireAuth("curriculum");
    }
  };
  const goPaywall = () => requireAuth("paywall");
  const goAccount = () => requireAuth("account");
  const handleSelectUnit = (module: number, unitId: string) => {
    writeProgress({ module: module as 0 | 1 | 2 | 3 | 4 | 5, unitId, pageIdx: 0 });
    goCurriculum();
  };

  // Always-mounted debug surface so we can observe AuthProvider state
  // even during BOOT / AUTHENTICATING / REJECTED early returns.
  // F1: dev-only — Vite strips this branch from prod bundles via the
  // `import.meta.env.DEV` constant, so internal state never leaks to
  // production users.
  const debug = IS_DEV ? <DebugAuth /> : null;

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

  // Sprint 28-B.1 + 28-B.8: loading fallback for lazy-loaded views.
  const loadFallback = <LoadingSkeleton />;

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
          onHelp={goHelp}
        />
      );
      break;
    case "curriculum":
      body = (
        <Suspense fallback={loadFallback}>
          <CurriculumRenderer
            onSignIn={goSignIn}
            onContinueGated={goPaywall}
            onAccount={goAccount}
            onOpenMenu={goMenu}
            onHelp={goHelp}
          />
        </Suspense>
      );
      break;
    case "menu":
      body = (
        <Suspense fallback={loadFallback}>
          <CurriculumMenu
            onContinue={goCurriculum}
            onSignIn={goSignIn}
            onContinuePaid={goPaywall}
            onAccount={goAccount}
            onSelectUnit={handleSelectUnit}
            onHelp={goHelp}
          />
        </Suspense>
      );
      break;
    case "signin":
      body = onSignInPage;
      break;
    case "paid_curriculum":
      body = (
        <Suspense fallback={loadFallback}>
          <PaidLessonRenderer
            onSignIn={goSignIn}
            onPaywall={goPaywall}
            onAccount={goAccount}
            onOpenMenu={goMenu}
            onSequenceComplete={goLanding}
            onHelp={goHelp}
          />
        </Suspense>
      );
      break;
    case "paywall":
      body = (
        <Suspense fallback={loadFallback}>
          <PaywallPage
            productCode="modules_4_5"
            onRedeemGift={() => setView("gift_redeem")}
            onBack={goLanding}
            onHelp={goHelp}
          />
        </Suspense>
      );
      break;
    case "gift_redeem":
      body = (
        <Suspense fallback={loadFallback}>
          <GiftRedeemPage
            onClaimed={goCurriculum}
            onBack={() => setView("paywall")}
            onHelp={goHelp}
          />
        </Suspense>
      );
      break;
    case "account":
      body = (
        <Suspense fallback={loadFallback}>
          <AccountSettingsPage
            onSignedOut={signOut}
            onDeleted={goLanding}
            onBack={goLanding}
            onHelp={goHelp}
          />
        </Suspense>
      );
      break;
    case "help":
      body = (
        <Suspense fallback={loadFallback}>
          <HelpPage onBack={goLanding} />
        </Suspense>
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
    <ViewportProvider>
      <ResponsiveContainer>
        <>
          {/* Sprint 28-D.7: skip-to-content link for keyboard users.
           *  Contract-compliant (CONTRACT Section I.A palette only;
           *  Section II — no spatial movement on focus). Uses the
           *  clip-path / size-collapse pattern so the element occupies
           *  zero visible space when unfocused and reveals in place on
           *  focus, with no position translation. */}
          <a
            href="#main-content"
            className="noni-skip-link"
          >
            Skip to main content
          </a>
          {debug}
          {transientBanner}
          <div id="main-content">{body}</div>
        </>
      </ResponsiveContainer>
    </ViewportProvider>
  );
};

export default App;
