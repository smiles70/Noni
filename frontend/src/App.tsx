/**
 * Noni root component.
 * Landing is the default view; primary CTA advances to the curriculum view.
 * Per the Reversibility architectural rule, the curriculum view exposes a
 * "Return to start" affordance that brings the user back to landing.
 */
import { useState } from "react";
import LandingPage from "./components/LandingPage";
import CurriculumRenderer from "./components/CurriculumRenderer";

type View = "landing" | "curriculum";

const App: React.FC = () => {
  const [view, setView] = useState<View>("landing");
  if (view === "landing") {
    return <LandingPage onBegin={() => setView("curriculum")} />;
  }
  return <CurriculumRenderer onReturn={() => setView("landing")} />;
};

export default App;
