/**
 * Passive renderer for ISCS-approved curriculum states.
 * Contains zero business logic. UI complexity is server-governed.
 */
import { useEffect, useState } from "react";
import { loadWhatIsAI, ApprovedUIState } from "../api/interfaceController";

interface Props {
  onReturn?: () => void;
}

const PAGE: React.CSSProperties = {
  padding: "2rem",
  maxWidth: "680px",
  margin: "0 auto",
  fontSize: "1.25rem",
  lineHeight: 1.6,
  color: "var(--noni-text)",
};

const RETURN_BTN: React.CSSProperties = {
  fontSize: "1rem",
  padding: "0.4rem 0.9rem",
  background: "transparent",
  color: "var(--noni-accent)",
  border: "1px solid var(--noni-accent)",
  borderRadius: "4px",
};

const ERROR_DETAIL: React.CSSProperties = {
  color: "var(--noni-muted)",
  fontSize: "1rem",
  marginTop: "0.5rem",
};

export default function CurriculumRenderer({ onReturn }: Props) {
  const [state, setState] = useState<ApprovedUIState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWhatIsAI()
      .then(setState)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, []);

  const Nav = () =>
    onReturn ? (
      <nav aria-label="Lesson navigation" style={{ marginBottom: "1.5rem" }}>
        <button type="button" onClick={onReturn} style={RETURN_BTN}>
          Return to start
        </button>
      </nav>
    ) : null;

  if (error) {
    return (
      <main style={PAGE} aria-live="polite">
        <Nav />
        <p>We are having trouble reaching the lesson. Please try again in a moment.</p>
        <p style={ERROR_DETAIL}>{error}</p>
      </main>
    );
  }

  if (!state) {
    return (
      <main style={PAGE} aria-live="polite">
        <Nav />
        <p>Loading...</p>
      </main>
    );
  }

  const page = state.ui_state;

  return (
    <main style={PAGE}>
      <Nav />
      <header>
        <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>{page.title}</h1>
      </header>
      <section aria-label="Lesson content">
        {page.content.map((line, i) => (
          <p key={i}>{line}</p>
        ))}
      </section>
    </main>
  );
}
