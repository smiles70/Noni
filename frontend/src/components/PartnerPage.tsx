/* Hosted partner page (/c/:slug). A calm branded doorway for a
 * community's residents: org name, one line of welcome, and the
 * access-code path. Public — shows the org's name only. */

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import {
  COLORS,
  MARKETING,
  RADIUS,
  SPACING,
  TYPOGRAPHY,
} from "../design/tokens";
import ChatWidget from "./ChatWidget";
import SupportContact from "./SupportContact";

const PAGE: React.CSSProperties = {
  minHeight: "100vh",
  backgroundColor: MARKETING.paper,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
};
const CARD: React.CSSProperties = {
  maxWidth: 560,
  margin: "0 auto",
  padding: SPACING.xl,
  backgroundColor: MARKETING.paperCard,
  border: `1px solid ${MARKETING.paperEdge}`,
  borderRadius: RADIUS.lg,
  marginTop: SPACING.xl,
};
const H1: React.CSSProperties = { fontSize: 32, marginBottom: SPACING.md };
const BODY: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx + 2,
  lineHeight: 1.6,
};
const BTN: React.CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx + 2,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  background: MARKETING.gold,
  color: MARKETING.charcoalDeep,
  border: "none",
  borderRadius: 28,
  fontWeight: 700,
  cursor: "pointer",
};

export default function PartnerPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState<string | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    apiClient
      .get(`/api/v1/billing/org/by-slug/${slug}`)
      .then((r) => setName((r.data as { name: string }).name))
      .catch(() => setMissing(true));
  }, [slug]);

  if (missing) {
    return (
      <main style={PAGE}>
        <div style={CARD}>
          <h1 style={H1}>We could not find that community</h1>
          <p style={BODY}>
            The link may be old. You can still sign in or write to us at
            help@mynaani.com.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main style={PAGE}>
      <div style={CARD}>
        <h1 style={H1}>{name ?? "Welcome"}</h1>
        <p style={BODY}>
          Your community has arranged free access to mynaani for you. All you
          need is the access code your community gave you — no card, no payment,
          no password to remember.
        </p>
        <button style={BTN} onClick={() => navigate("/signin")}>
          I have my access code — sign me in
        </button>
        <div style={{ marginTop: SPACING.lg }}>
          <SupportContact />
          <ChatWidget journey="facility" />
        </div>
      </div>
    </main>
  );
}
