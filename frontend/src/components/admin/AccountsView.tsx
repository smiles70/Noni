/** ADMIN-IA-001: account support lookup — read-only per charter. */

import { useCallback, useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, SPACING } from "../../design/tokens";

interface AccountRow {
  id: string;
  email: string | null;
  display_name: string | null;
  deleted_at: string | null;
  purchase_count: number;
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

export function AccountsView() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<AccountRow[]>([]);
  const [error, setError] = useState("");

  const search = useCallback(async () => {
    if (q.trim().length < 3) {
      setError("Type at least 3 characters.");
      return;
    }
    setError("");
    try {
      const r = await apiClient.get<AccountRow[]>(
        `/api/v1/admin/accounts?q=${encodeURIComponent(q.trim())}`,
      );
      setRows(r.data);
    } catch {
      setError("Search failed — check the API.");
    }
  }, [q]);

  return (
    <section aria-label="Accounts">
      <h2 style={{ marginTop: 0 }}>Accounts</h2>
      <p style={{ fontSize: 13, color: "#666", marginTop: 0 }}>
        Support lookup — read-only. Individual learning progress is never shown
        here.
      </p>
      <div style={{ display: "flex", gap: SPACING.sm }}>
        <input
          aria-label="Search accounts"
          placeholder="Search email or name"
          style={{
            fontSize: 15,
            padding: `${SPACING.sm}px ${SPACING.md}px`,
            borderRadius: 8,
            border: `1px solid ${COLORS.accentMutedBlue}`,
            flex: 1,
          }}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void search()}
        />
        <button onClick={() => void search()} style={{ cursor: "pointer" }}>
          Search
        </button>
      </div>
      {error && <p style={{ color: "#a84c4c" }}>{error}</p>}
      {rows.length > 0 && (
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
              <th style={TH}>Email</th>
              <th style={TH}>Name</th>
              <th style={TH}>Purchases</th>
              <th style={TH}>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td style={TD}>{a.email ?? "—"}</td>
                <td style={TD}>{a.display_name ?? "—"}</td>
                <td style={TD}>{a.purchase_count}</td>
                <td style={TD}>
                  {a.deleted_at ? "deletion scheduled" : "active"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
