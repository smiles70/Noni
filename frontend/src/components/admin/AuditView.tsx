/** ADMIN-IA-001 G6: searchable staff audit feed across all orgs. */

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, SPACING } from "../../design/tokens";

interface AuditEntry {
  action: string;
  detail: string;
  org_id: string;
  org_name: string;
  actor: string;
  created_at: string | null;
}

const TH: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "8px 10px",
  textAlign: "left",
  backgroundColor: "#fafaf8",
};
const TD: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "8px 10px",
};

export function AuditView({ onOpenOrg }: { onOpenOrg: (id: string) => void }) {
  const [q, setQ] = useState("");
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");
  const limit = 50;

  const load = useCallback(async (query: string, off: number) => {
    try {
      const r = await apiClient.get<{ entries: AuditEntry[] }>(
        `/api/v1/admin/audit?limit=${limit}&offset=${off}${query ? `&q=${encodeURIComponent(query)}` : ""}`,
      );
      setEntries(r.data.entries);
      setOffset(off);
    } catch {
      setError("Couldn't load the audit feed.");
    }
  }, []);

  useEffect(() => {
    void load("", 0);
  }, [load]);

  return (
    <section aria-label="Audit feed">
      <h2 style={{ marginTop: 0 }}>Audit</h2>
      <div style={{ display: "flex", gap: SPACING.sm }}>
        <input
          aria-label="Search audit"
          placeholder="Filter by action, detail, or org"
          style={{
            fontSize: 15,
            padding: `${SPACING.sm}px ${SPACING.md}px`,
            borderRadius: 8,
            border: `1px solid ${COLORS.accentMutedBlue}`,
            flex: 1,
          }}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void load(q.trim(), 0)}
        />
        <button
          onClick={() => void load(q.trim(), 0)}
          style={{ cursor: "pointer" }}
        >
          Filter
        </button>
      </div>
      {error && <p style={{ color: "#a84c4c" }}>{error}</p>}
      {entries.length === 0 ? (
        <p style={{ color: "#666" }}>Nothing recorded.</p>
      ) : (
        <>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: 14,
              marginTop: SPACING.md,
            }}
          >
            <thead>
              <tr>
                <th style={TH}>When</th>
                <th style={TH}>Actor</th>
                <th style={TH}>Action</th>
                <th style={TH}>Organization</th>
                <th style={TH}>Detail</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((a, i) => (
                <tr key={i}>
                  <td style={{ ...TD, whiteSpace: "nowrap" }}>
                    {a.created_at?.slice(0, 16).replace("T", " ") ?? "—"}
                  </td>
                  <td style={TD}>{a.actor}</td>
                  <td style={TD}>{a.action}</td>
                  <td style={TD}>
                    <button
                      onClick={() => onOpenOrg(a.org_id)}
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
                      {a.org_name}
                    </button>
                  </td>
                  <td style={TD}>{a.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div
            style={{ marginTop: SPACING.sm, display: "flex", gap: SPACING.md }}
          >
            <button
              disabled={offset === 0}
              onClick={() => void load(q.trim(), Math.max(0, offset - limit))}
              style={{ cursor: "pointer" }}
            >
              ← Newer
            </button>
            <button
              disabled={entries.length < limit}
              onClick={() => void load(q.trim(), offset + limit)}
              style={{ cursor: "pointer" }}
            >
              Older →
            </button>
          </div>
        </>
      )}
    </section>
  );
}
