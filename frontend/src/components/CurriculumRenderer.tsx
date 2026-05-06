/**
 * Passive renderer for ISCS-approved curriculum states.
 * Contains zero business logic. UI complexity is server-governed.
 */
import { useEffect, useState } from "react";
import { loadWhatIsAI, ApprovedUIState } from "../api/interfaceController";

export default function CurriculumRenderer() {
  const [state, setState] = useState<ApprovedUIState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWhatIsAI()
      .then(setState)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  if (error) {
    return (
      <div style={{ padding: "2rem", maxWidth: "600px", fontSize: "1.25rem" }}>
        <p>We're having trouble reaching the lesson. Please try again in a moment.</p>
        <p style={{ color: "#888", fontSize: "0.9rem" }}>{error}</p>
      </div>
    );
  }

  if (!state) {
    return <p style={{ padding: "2rem", fontSize: "1.25rem" }}>Loading...</p>;
  }

  const page = state.ui_state;

  return (
    <div
      style={{
        padding: "2rem",
        maxWidth: "640px",
        margin: "0 auto",
        fontSize: "1.25rem",
        lineHeight: 1.6,
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2rem" }}>{page.title}</h1>
      {page.content.map((line, i) => (
        <p key={i}>{line}</p>
      ))}
    </div>
  );
}
