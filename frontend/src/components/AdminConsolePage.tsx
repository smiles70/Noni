/**
 * Staff admin console — /admin. Internal ops surface; enterprise density,
 * not geragogy. Gated by /api/v1/admin/whoami-check. Never shows
 * individual learner progress — aggregate boundary is structural.
 */

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";

const PAGE: React.CSSProperties = {
  minHeight: "100vh",
  backgroundColor: COLORS.surface,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  padding: SPACING.xl,
};

const INPUT: React.CSSProperties = {
  fontSize: 15,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  borderRadius: RADIUS.md,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  width: 320,
};

const TABLE: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: 14,
  marginTop: SPACING.md,
};

const CELL: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "8px 10px",
  textAlign: "left",
};

interface OrgRow {
  id: string;
  name: string;
  contact_email: string;
  status: string;
  org_type: string;
  tier: string;
  slug: string | null;
  seats_total: number;
  seats_used: number;
}

interface FlagRow {
  id: string;
  account_id: string;
  flag: string;
  detail: string;
  created_at: string | null;
}

export default function AdminConsolePage() {
  const [state, setState] = useState<"loading" | "staff" | "denied">("loading");
  const [q, setQ] = useState("");
  const [orgs, setOrgs] = useState<OrgRow[]>([]);
  const [flags, setFlags] = useState<FlagRow[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient.get<{ staff: boolean }>("/api/v1/admin/whoami-check")
      .then((r) => setState(r.data.staff ? "staff" : "denied"))
      .catch(() => setState("denied"));
  }, []);

  useEffect(() => {
    if (state === "staff") {
      apiClient.get<{ flags: FlagRow[] }>("/api/v1/admin/flags")
        .then((r) => setFlags(r.data.flags))
        .catch(() => setFlags([]));
    }
  }, [state]);

  const search = useCallback(async () => {
    if (q.trim().length < 3) {
      setError("Type at least 3 characters.");
      return;
    }
    setError("");
    try {
      const r = await apiClient.get<OrgRow[]>(
        `/api/v1/admin/orgs?q=${encodeURIComponent(q.trim())}`,
      );
      setOrgs(r.data);
    } catch {
      setError("Search failed — check the API.");
    }
  }, [q]);

  if (state === "loading") return <main style={PAGE}>Loading…</main>;
  if (state === "denied")
    return <main style={PAGE}>This area is for mynaani staff.</main>;

  return (
    <main style={PAGE} data-component="AdminConsole">
      <h1 style={{ fontSize: 22, margin: 0 }}>mynaani staff console</h1>
      <p style={{ color: COLORS.disabled, fontSize: 13 }}>
        Internal ops. Aggregate data only — no individual learner records.
      </p>

      <section aria-label="Organization search">
        <h2 style={{ fontSize: 16 }}>Organizations</h2>
        <input
          style={INPUT}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          placeholder="Search name, email, or slug"
          aria-label="Search organizations"
        />{" "}
        <button type="button" onClick={search}>
          Search
        </button>
        {error && <p role="alert" style={{ color: "#a33" }}>{error}</p>}
        {orgs.length > 0 && (
          <table style={TABLE}>
            <thead>
              <tr>
                {["Name", "Contact", "Status", "Type", "Tier", "Slug", "Seats"].map(
                  (h) => (
                    <th key={h} style={CELL}>{h}</th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {orgs.map((o) => (
                <tr key={o.id}>
                  <td style={CELL}>{o.name}</td>
                  <td style={CELL}>{o.contact_email}</td>
                  <td style={CELL}>{o.status}</td>
                  <td style={CELL}>{o.org_type}</td>
                  <td style={CELL}>{o.tier}</td>
                  <td style={CELL}>{o.slug ?? "—"}</td>
                  <td style={CELL}>
                    {o.seats_used}/{o.seats_total}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section aria-label="Account flags" style={{ marginTop: SPACING.xl }}>
        <h2 style={{ fontSize: 16 }}>Account flags (sharing signals)</h2>
        {flags.length === 0 ? (
          <p style={{ fontSize: 14, color: COLORS.disabled }}>
            No flags — the weekly scan has found nothing to review.
          </p>
        ) : (
          <table style={TABLE}>
            <thead>
              <tr>
                {["Account", "Flag", "Detail", "Date"].map((h) => (
                  <th key={h} style={CELL}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {flags.map((f) => (
                <tr key={f.id}>
                  <td style={CELL}>{f.account_id.slice(0, 8)}…</td>
                  <td style={CELL}>{f.flag}</td>
                  <td style={CELL}>{f.detail}</td>
                  <td style={CELL}>{f.created_at?.slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
