/**
 * Passive renderer for the landing page.
 * All copy comes from the backend; no text is hardcoded here.
 */
import { useEffect, useState } from "react";
import { loadLandingPage, LandingPageContent } from "../api/landing";

interface Props {
  onBegin: () => void;
}

function paragraphs(text: string) {
  return text.split("\n\n").map((p, i) => <p key={i}>{p}</p>);
}

const PAGE: React.CSSProperties = {
  padding: "2rem",
  maxWidth: "680px",
  margin: "0 auto",
  fontSize: "1.25rem",
  lineHeight: 1.6,
  fontFamily: "system-ui, -apple-system, sans-serif",
  color: "#1a1a1a",
};

const PRIMARY_BTN: React.CSSProperties = {
  fontSize: "1.25rem",
  padding: "0.9rem 1.6rem",
  background: "#2a5d8f",
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
};

const SECONDARY_BTN: React.CSSProperties = {
  fontSize: "1.25rem",
  padding: "0.9rem 1.6rem",
  background: "transparent",
  color: "#2a5d8f",
  border: "2px solid #2a5d8f",
  borderRadius: "6px",
  cursor: "pointer",
};

const CTA_NOTE: React.CSSProperties = {
  fontSize: "1rem",
  color: "#555",
  marginTop: "0.5rem",
};

export default function LandingPage({ onBegin }: Props) {
  const [content, setContent] = useState<LandingPageContent | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLandingPage()
      .then(setContent)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, []);

  if (error) {
    return (
      <main style={PAGE}>
        <p>We are having trouble loading this page. Please try again in a moment.</p>
      </main>
    );
  }

  if (!content) {
    return (
      <main style={PAGE}>
        <p>Loading...</p>
      </main>
    );
  }

  const scrollToIntro = () => {
    const el = document.getElementById("introduction");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <main style={PAGE}>
      <header>
        <h1 style={{ fontSize: "2.25rem", marginBottom: "0.5rem" }}>
          {content.hero.headline}
        </h1>
        <p style={{ fontSize: "1.35rem", color: "#444" }}>{content.hero.subheadline}</p>
      </header>

      <section aria-labelledby="introduction-heading" style={{ marginTop: "3rem" }}>
        <h2 id="introduction-heading">{content.introduction.title}</h2>
        <div id="introduction">{paragraphs(content.introduction.body)}</div>
      </section>

      <section aria-labelledby="what-noni-does-heading" style={{ marginTop: "2rem" }}>
        <h2 id="what-noni-does-heading">{content.what_noni_does.title}</h2>
        <ul>
          {content.what_noni_does.items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="how-it-feels-heading" style={{ marginTop: "2rem" }}>
        <h2 id="how-it-feels-heading">{content.how_it_feels.title}</h2>
        <ul>
          {content.how_it_feels.items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="trust-heading" style={{ marginTop: "2rem" }}>
        <h2 id="trust-heading">{content.trust_and_safety.title}</h2>
        {paragraphs(content.trust_and_safety.body)}
      </section>

      <section
        aria-label="Next steps"
        style={{
          marginTop: "3rem",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
        }}
      >
        <div>
          <button type="button" onClick={onBegin} style={PRIMARY_BTN}>
            {content.call_to_action.primary.label}
          </button>
          <p style={CTA_NOTE}>{content.call_to_action.primary.note}</p>
        </div>
        <div>
          <button type="button" onClick={scrollToIntro} style={SECONDARY_BTN}>
            {content.call_to_action.secondary.label}
          </button>
          <p style={CTA_NOTE}>{content.call_to_action.secondary.note}</p>
        </div>
      </section>

      <footer
        style={{
          marginTop: "3rem",
          borderTop: "1px solid #e5e5e5",
          paddingTop: "2rem",
        }}
      >
        {paragraphs(content.closing.body)}
      </footer>
    </main>
  );
}
