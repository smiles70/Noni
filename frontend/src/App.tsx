/**
 * Noni root component.
 * Default view is the landing page; primary CTA advances to the curriculum view.
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
  return <CurriculumRenderer />;
};

export default App;
