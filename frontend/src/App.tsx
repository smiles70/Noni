/**
 * Noni root component.
 *
 * Simple view-state machine (no router). Sprint A8 adds account/billing
 * views; landing and curriculum are unchanged. The curriculum -> paywall
 * trigger is wired in once the curriculum renderer surfaces it; for now
 * the additional views are reachable in dev via direct setView calls
 * (e.g. from a debug surface or future settings entry on landing).
 */
import { useState } from "react";
import LandingPage from "./components/LandingPage";
import CurriculumRenderer from "./components/CurriculumRenderer";
import SignInPage from "./components/SignInPage";
import PaywallPage from "./components/PaywallPage";
import GiftRedeemPage from "./components/GiftRedeemPage";
import AccountSettingsPage from "./components/AccountSettingsPage";

type View =
  | "landing"
  | "curriculum"
  | "signin"
  | "paywall"
  | "gift_redeem"
  | "account";

const App: React.FC = () => {
  const [view, setView] = useState<View>("landing");

  const goLanding = () => setView("landing");
  const goCurriculum = () => setView("curriculum");

  switch (view) {
    case "landing":
      return <LandingPage onBegin={goCurriculum} />;
    case "curriculum":
      return <CurriculumRenderer onReturn={goLanding} />;
    case "signin":
      return <SignInPage onSignedIn={goCurriculum} onCancel={goLanding} />;
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
  }
};

export default App;
