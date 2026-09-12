/* Hosted partner page (/c/:slug). A calm branded doorway for a
 * community's residents: org name, one line of welcome, and the
 * access-code path. Public — shows the org's name only. */

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import { COLORS, SPACING, TYPOGRAPHY } from "../design/tokens";
import ChatWidget from "./ChatWidget";

const PAGE: React.CSSProperties = {
  maxWidth: 560,
  margin: "0 auto",
  padding: SPACING.xl,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
};
const H1: React.CSSProperties = { fontSize: 32, marginBottom: SPACING.md };
const BODY: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx + 2,
  lineHeight: 1.6,
};
const BTN: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx + 2,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  background: COLORS.accentMutedBlue,
  color: "#FFFFFF",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
};

export default function PartnerPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState<string | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    apiClient
      .get(`/api/v1/org/by-slug/${slug}`)
      .then((r) => setName((r.data as { name: string }).name))
      .catch(() => setMissing(true));
  }, [slug]);

  if (missing) {
    return (
      <main style={PAGE}>
        <h1 style={H1}>We could not find that community</h1>
        <p style={BODY}>
          The link may be old. You can still sign in or write to us at
          help@mynaani.com.
        </p>
      </main>
    );
  }

  return (
    <main style={PAGE}>
      <h1 style={H1}>{name ?? "Welcome"}</h1>
      <p style={BODY}>
        Your community has arranged free access to mynaani for you. All you need
        is the access code your community gave you — no card, no payment, no
        password to remember.
      </p>
      <button style={BTN} onClick={() => navigate("/signin")}>
        I have my access code — sign me in
      </button>
      <div style={{ marginTop: SPACING.lg }}>
        <ChatWidget />
      </div>
    </main>
  );
}
