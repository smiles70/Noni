/** ADMIN-IA-001: account support lookup — read-only per charter. */

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, SPACING } from "../../design/tokens";

interface AccountRow {
  id: string;
  email: string | null;
  display_name: string | null;
  deleted_at: string | null;
  suspended_at: string | null;
  suspension_reason: string | null;
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

export function AccountsView({ canWrite = true }: { canWrite?: boolean }) {
  const [staff, setStaff] = useState<
    {
      id: string;
      display_name: string | null;
      email: string | null;
      role: string | null;
    }[]
  >([]);

  const loadStaff = useCallback(() => {
    if (!canWrite) return;
    apiClient
      .get<typeof staff>("/api/v1/admin/staff")
      .then((r) => setStaff(r.data))
      .catch(() => setStaff([]));
  }, [canWrite]);

  useEffect(() => {
    loadStaff();
  }, [loadStaff]);

  const setRole = (id: string, role: string) =>
    apiClient
      .post(`/api/v1/admin/staff/${id}/role`, { role })
      .then(loadStaff)
      .catch((e) => {
        const msg =
          (e as { response?: { data?: { detail?: { envelope_id?: string } } } })
            ?.response?.data?.detail?.envelope_id ?? "admin.role_failed";
        setError(
          msg === "admin.cannot_change_own_role"
            ? "You can't change your own role."
            : msg === "admin.last_admin"
              ? "There must be at least one admin."
              : "Role change failed.",
        );
      });

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

  const act = useCallback(
    async (
      accountId: string,
      verb: "suspend" | "reinstate" | "cancel-deletion",
    ) => {
      let body: object | undefined;
      if (verb === "suspend") {
        const reason = window.prompt("Reason (visible in the audit log):");
        if (!reason) return;
        body = { reason };
      } else if (!window.confirm(`${verb.replace("-", " ")} this account?`)) {
        return;
      }
      try {
        await apiClient.post(
          `/api/v1/admin/accounts/${accountId}/${verb}`,
          body,
        );
        await search();
      } catch {
        setError("Action failed — check the API.");
      }
    },
    [search],
  );

  return (
    <section aria-label="Accounts">
      <h2 style={{ marginTop: 0 }}>Accounts</h2>
      {canWrite && staff.length > 0 && (
        <div style={{ marginBottom: SPACING.md }}>
          <h3 style={{ fontSize: 15 }}>Staff roles</h3>
          <table style={{ borderCollapse: "collapse", fontSize: 13 }}>
            <tbody>
              {staff.map((p) => (
                <tr key={p.id}>
                  <td style={{ padding: "4px 10px" }}>{p.display_name}</td>
                  <td style={{ padding: "4px 10px" }}>{p.role}</td>
                  <td style={{ padding: "4px 10px" }}>
                    <select
                      value={p.role ?? ""}
                      onChange={(e) => setRole(p.id, e.target.value)}
                    >
                      <option value="admin">admin</option>
                      <option value="support">support</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p style={{ fontSize: 13, color: "#666", marginTop: 0 }}>
        Support lookup with account actions. Individual learning progress is
        never shown here.
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
              <th style={TH}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td style={TD}>{a.email ?? "—"}</td>
                <td style={TD}>{a.display_name ?? "—"}</td>
                <td style={TD}>{a.purchase_count}</td>
                <td style={TD}>
                  {a.deleted_at
                    ? "deleted"
                    : a.suspended_at
                      ? `suspended${a.suspension_reason ? ` — ${a.suspension_reason}` : ""}`
                      : "active"}
                </td>
                <td style={TD}>
                  {canWrite && (
                    <div style={{ display: "flex", gap: 6 }}>
                      {a.deleted_at ? (
                        <button
                          style={{ cursor: "pointer" }}
                          onClick={() => void act(a.id, "cancel-deletion")}
                        >
                          Restore
                        </button>
                      ) : a.suspended_at ? (
                        <button
                          style={{ cursor: "pointer" }}
                          onClick={() => void act(a.id, "reinstate")}
                        >
                          Reinstate
                        </button>
                      ) : (
                        <button
                          style={{ cursor: "pointer" }}
                          onClick={() => void act(a.id, "suspend")}
                        >
                          Suspend
                        </button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
