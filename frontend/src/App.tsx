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
import LandingPage from "./components/LandingPage";
import CurriculumRenderer from "./components/CurriculumRenderer";
import SignInPage from "./components/SignInPage";
import PaywallPage from "./components/PaywallPage";
import GiftRedeemPage from "./components/GiftRedeemPage";
import AccountSettingsPage from "./components/AccountSettingsPage";
import { signIn } from "./api/auth";
import { consumeOAuthFragment } from "./api/oauth";

type View =
  | "landing"
  | "curriculum"
  | "signin"
  | "paywall"
  | "gift_redeem"
  | "account"
  | "oauth_finishing";

const App: React.FC = () => {
  const [view, setView] = useState<View>("landing");

  // Sprint B2: if Supabase returned the user with an access_token in the URL
  // fragment, exchange it for a session cookie before the app renders any
  // signed-in chrome. Runs exactly once at mount.
  useEffect(() => {
    const fragment = consumeOAuthFragment();
    if (!fragment) return;
    setView("oauth_finishing");
    signIn(fragment.accessToken)
      .then(() => setView("landing"))
      .catch(() => setView("signin"));
  }, []);

  const goLanding = () => setView("landing");
  const goCurriculum = () => setView("curriculum");
  const goSignIn = () => setView("signin");
  const goPaywall = () => setView("paywall");
  const goAccount = () => setView("account");

  switch (view) {
    case "landing":
      return (
        <LandingPage
          onBegin={goCurriculum}
          onSignIn={goSignIn}
          onContinuePaid={goPaywall}
          onAccount={goAccount}
        />
      );
    case "curriculum":
      return (
        <CurriculumRenderer
          onReturn={goLanding}
          onSignIn={goSignIn}
          onContinuePaid={goPaywall}
          onAccount={goAccount}
        />
      );
    case "signin":
      return <SignInPage onSignedIn={goLanding} onCancel={goLanding} />;
    case "paywall":
      return (
        <PaywallPage
          productCode="modules_4_5"
          onRedeemGift={() => setView("gift_redeem")}
          onBack={goLanding}
        />
      );
    case "gift_redeem":
      return (
        <GiftRedeemPage
          onClaimed={goCurriculum}
          onBack={() => setView("paywall")}
        />
      );
    case "account":
      return (
        <AccountSettingsPage
          onSignedOut={goLanding}
          onDeleted={goLanding}
          onBack={goLanding}
        />
      );
    case "oauth_finishing":
      return (
        <main aria-live="polite" data-component="PendingBanner">
          <p>One moment — finishing sign in.</p>
        </main>
      );
  }
};

export default App;
