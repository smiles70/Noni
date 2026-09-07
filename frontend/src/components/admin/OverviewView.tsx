/**
 * ADMIN-IA-001 G2: operational landing. Aggregate counts only —
 * the learner-privacy boundary applies here too.
 */

import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, RADIUS, SPACING } from "../../design/tokens";

interface Overview {
  orgs_total: number;
  seats_total: number;
  seats_used: number;
  flags_total: number;
  licenses_expiring: {
    org_id: string;
    org_name: string;
    total_seats: number;
    expires_at: string | null;
  }[];
  recent_audit: {
    action: string;
    detail: string;
    org_name: string;
    actor: string;
    created_at: string | null;
  }[];
}

const CARD: React.CSSProperties = {
  backgroundColor: "#ffffff",
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
  minWidth: 150,
};

export default function OverviewView({
  onNewOrg,
  onOpenOrg,
}: {
  onNewOrg: () => void;
  onOpenOrg: (id: string) => void;
}) {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient
      .get<Overview>("/api/v1/admin/overview")
      .then((r) => setData(r.data))
      .catch(() => setError("Couldn't load the overview — check the API."));
  }, []);

  if (error) return <p>{error}</p>;
  if (!data) return <p>Loading…</p>;

  const kpis: [string, string | number][] = [
    ["Organizations", data.orgs_total],
    ["Seats used", `${data.seats_used} / ${data.seats_total}`],
    ["Flags pending", data.flags_total],
    ["Licenses expiring ≤30d", data.licenses_expiring.length],
  ];

  return (
    <section aria-label="Overview">
      <h2 style={{ marginTop: 0 }}>Needs attention</h2>
      <div style={{ display: "flex", gap: SPACING.md, flexWrap: "wrap" }}>
        {kpis.map(([label, value]) => (
          <div key={label} style={CARD}>
            <div style={{ fontSize: 13, color: COLORS.disabled }}>{label}</div>
            <div style={{ fontSize: 28, fontWeight: 600 }}>{value}</div>
          </div>
        ))}
      </div>

      <button
        onClick={onNewOrg}
        style={{
          marginTop: SPACING.lg,
          padding: `${SPACING.sm}px ${SPACING.lg}px`,
          fontSize: 15,
          fontWeight: 600,
          color: "#fff",
          backgroundColor: COLORS.accentMutedBlue,
          border: "none",
          borderRadius: RADIUS.md,
          cursor: "pointer",
          width: "100%",
          textAlign: "left",
        }}
      >
        + New organization
      </button>

      {data.licenses_expiring.length > 0 && (
        <>
          <h3 style={{ marginTop: SPACING.xl }}>Expiring soon</h3>
          <table
            style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}
          >
            <tbody>
              {data.licenses_expiring.map((l) => (
                <tr key={l.org_id}>
                  <td style={{ padding: "6px 8px" }}>
                    <button
                      onClick={() => onOpenOrg(l.org_id)}
                      style={{
                        background: "none",
                        border: "none",
                        color: COLORS.accentMutedBlue,
                        cursor: "pointer",
                        fontSize: 14,
                        padding: 0,
                        textDecoration: "underline",
                      }}
                    >
                      {l.org_name}
                    </button>
                  </td>
                  <td style={{ padding: "6px 8px" }}>{l.total_seats} seats</td>
                  <td style={{ padding: "6px 8px" }}>
                    ends {l.expires_at?.slice(0, 10) ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h3 style={{ marginTop: SPACING.xl }}>Recent activity</h3>
      {data.recent_audit.length === 0 ? (
        <p style={{ color: "#666" }}>Nothing recorded yet.</p>
      ) : (
        <table
          style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}
        >
          <tbody>
            {data.recent_audit.map((a, i) => (
              <tr key={i}>
                <td style={{ padding: "6px 8px", whiteSpace: "nowrap" }}>
                  {a.created_at?.slice(11, 16) ?? "—"}
                </td>
                <td style={{ padding: "6px 8px" }}>{a.actor}</td>
                <td style={{ padding: "6px 8px" }}>{a.action}</td>
                <td style={{ padding: "6px 8px" }}>{a.org_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
