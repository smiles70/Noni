/**
 * Noni root component.
 *
 * Simple view-state machine (no router). Sprint A8 adds account/billing
 * views; landing and curriculum are unchanged. The curriculum -> paywall
 * trigger is wired in once the curriculum renderer surfaces it; for now
 * the additional views are reachable in dev via direct setView calls
 * (e.g. from a debug surface or future settings entry on landing).
 */
import { Suspense, lazy, useEffect } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import SignInPage from "./components/SignInPage";
import AuthPendingBanner from "./components/AuthPendingBanner";
import AuthBlockedNotice from "./components/AuthBlockedNotice";
import LoadingSkeleton from "./components/LoadingSkeleton";
import RequireAuth from "./components/RequireAuth";
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

const App: React.FC = () => {
  // AuthProvider is the ONLY source of auth truth (FE Step-4 cutover).
  // App.tsx now orchestrates routes via React Router v6 (Series A Step 1).
  const { state, signOut: rawSignOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isReady = state?.status === "READY";

  // Series A Step 1: after explicit sign-out, redirect to landing so
  // the user is not left on a gated route in SIGNED_OUT state.
  const signOut = async () => {
    await rawSignOut();
    navigate("/", { replace: true });
  };

  // Series A Step 1: redirect after auth succeeds. If the URL has a
  // ?redirect= param (set by RequireAuth), forward the user there.
  // If the user signed in directly at /signin with no redirect, send
  // them to /curriculum as the natural post-auth destination.
  useEffect(() => {
    if (isReady) {
      const params = new URLSearchParams(location.search);
      const redirect = params.get("redirect");
      if (redirect) {
        navigate(redirect, { replace: true });
      } else if (location.pathname === "/signin") {
        navigate("/curriculum", { replace: true });
      }
    }
  }, [isReady, location.search, location.pathname, navigate]);

  const goLanding = () => navigate("/");
  const goSignIn = () => navigate("/signin");
  const goMenu = () => navigate("/menu");
  const goHelp = () => navigate("/help");

  // Gate: signed-out callers are routed through /signin with a redirect.
  const requireAuth = (path: string) => {
    if (isReady) {
      navigate(path);
    } else {
      navigate(`/signin?redirect=${encodeURIComponent(path)}`);
    }
  };

  // Cross-track resume: check saved progress and route to the correct
  // track so a returning learner picks up in M1-3 or M4-5 as appropriate.
  const goCurriculum = () => {
    const saved = readProgress();
    const target =
      saved && (saved.module === 4 || saved.module === 5)
        ? "/paid-curriculum"
        : "/curriculum";
    requireAuth(target);
  };

  const goPaywall = () => requireAuth("/paywall");
  const goAccount = () => requireAuth("/account");

  const handleSelectUnit = (module: number, unitId: string) => {
    writeProgress({ module: module as 0 | 1 | 2 | 3 | 4 | 5, unitId, pageIdx: 0 });
    goCurriculum();
  };

  // Always-mounted debug surface so we can observe AuthProvider state
  // even during BOOT / AUTHENTICATING / REJECTED early returns.
  const debug = IS_DEV ? <DebugAuth /> : null;

  // Global gates: AuthProvider state takes precedence over routes.
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
    const handleSignInAgain = async () => {
      try {
        await rawSignOut();
      } catch {
        /* idempotent */
      }
      navigate("/signin");
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

  // Sprint 28-B.1 + 28-B.8: loading fallback for lazy-loaded views.
  const loadFallback = <LoadingSkeleton />;

  const onSignInPage = (
    <SignInPage onSignedIn={() => {}} onCancel={goLanding} />
  );

  // F6: TRANSIENT_ERROR surfaces a non-alarming reconnect banner above
  // the current route. Per I-A, signed-in is sticky on transient backend
  // failures, so we keep rendering routes underneath.
  const transientBanner =
    status === "TRANSIENT_ERROR" ? (
      <AuthPendingBanner onRetry={() => window.location.reload()} />
    ) : null;

  return (
    <ViewportProvider>
      <ResponsiveContainer>
        <>
          <a href="#main-content" className="noni-skip-link">
            Skip to main content
          </a>
          {debug}
          {transientBanner}
          <div id="main-content">
            <Routes>
              <Route
                path="/"
                element={
                  <LandingPage
                    onBegin={goCurriculum}
                    onSignIn={goSignIn}
                    onContinuePaid={goPaywall}
                    onAccount={goAccount}
                    signedIn={isReady}
                    onSignOut={signOut}
                    onHelp={goHelp}
                  />
                }
              />
              <Route path="/signin" element={onSignInPage} />
              <Route
                path="/help"
                element={
                  <Suspense fallback={loadFallback}>
                    <HelpPage onBack={goLanding} />
                  </Suspense>
                }
              />
              <Route
                path="/curriculum"
                element={
                  <RequireAuth>
                    <Suspense fallback={loadFallback}>
                      <CurriculumRenderer
                        onSignIn={goSignIn}
                        onContinueGated={goPaywall}
                        onAccount={goAccount}
                        onOpenMenu={goMenu}
                        onHelp={goHelp}
                      />
                    </Suspense>
                  </RequireAuth>
                }
              />
              <Route
                path="/paid-curriculum"
                element={
                  <RequireAuth>
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
                  </RequireAuth>
                }
              />
              <Route
                path="/menu"
                element={
                  <RequireAuth>
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
                  </RequireAuth>
                }
              />
              <Route
                path="/paywall"
                element={
                  <RequireAuth>
                    <Suspense fallback={loadFallback}>
                      <PaywallPage
                        productCode="modules_4_5"
                        onRedeemGift={() => navigate("/gift-redeem")}
                        onBack={goLanding}
                        onHelp={goHelp}
                      />
                    </Suspense>
                  </RequireAuth>
                }
              />
              <Route
                path="/gift-redeem"
                element={
                  <RequireAuth>
                    <Suspense fallback={loadFallback}>
                      <GiftRedeemPage
                        onClaimed={goCurriculum}
                        onBack={() => navigate("/paywall")}
                        onHelp={goHelp}
                      />
                    </Suspense>
                  </RequireAuth>
                }
              />
              <Route
                path="/account"
                element={
                  <RequireAuth>
                    <Suspense fallback={loadFallback}>
                      <AccountSettingsPage
                        onSignedOut={signOut}
                        onDeleted={goLanding}
                        onBack={goLanding}
                        onHelp={goHelp}
                      />
                    </Suspense>
                  </RequireAuth>
                }
              />
              <Route
                path="/auth/callback"
                element={
                  <main aria-live="polite" data-component="PendingBanner">
                    <p>One moment — finishing sign in.</p>
                  </main>
                }
              />
            </Routes>
          </div>
        </>
      </ResponsiveContainer>
    </ViewportProvider>
  );
};

export default App;
