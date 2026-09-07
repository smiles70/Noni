/**
 * ADMIN-IA-001 G4: organizations list + detail. Detail surfaces
 * licenses, seats, codes, location, contacts, audit — all aggregate.
 */

import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, RADIUS, SPACING } from "../../design/tokens";

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

interface OrgDetail {
  org: {
    id: string;
    name: string;
    contact_email: string;
    admin_email: string;
    status: string;
    org_type: string;
    tier: string;
    slug: string | null;
    community_size: number | null;
    address_line1: string | null;
    address_line2: string | null;
    city: string | null;
    state: string | null;
    postal_code: string | null;
    phone: string | null;
  };
  contacts: {
    id: string;
    name: string;
    email: string | null;
    phone: string | null;
    role: string;
    is_primary: boolean;
  }[];
  licenses: {
    id: string;
    product_code: string;
    total_seats: number;
    used_seats: number;
    expires_at: string | null;
    status?: string;
    suspension_reason?: string | null;
  }[];
  codes_issued: number;
  audit: { action: string; detail: string; created_at: string | null }[];
}

const CARD: React.CSSProperties = {
  backgroundColor: "#ffffff",
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
};

const INPUT: React.CSSProperties = {
  fontSize: 15,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  borderRadius: RADIUS.md,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  flex: 1,
};

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

export function OrgsView({
  selected,
  onSelect,
  onNewOrg,
}: {
  selected: string | null;
  onSelect: (id: string | null) => void;
  onNewOrg: () => void;
}) {
  const [q, setQ] = useState("");
  const [orgs, setOrgs] = useState<OrgRow[]>([]);
  const [detail, setDetail] = useState<OrgDetail | null>(null);
  const [error, setError] = useState("");

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

  const reload = useCallback((id: string) => {
    apiClient
      .get<OrgDetail>(`/api/v1/admin/orgs/${id}`)
      .then((r) => setDetail(r.data))
      .catch(() => setError("Couldn't load that organization."));
  }, []);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    reload(selected);
  }, [selected, reload]);

  if (detail) {
    const o = detail.org;
    const address = [
      o.address_line1,
      o.address_line2,
      o.city,
      o.state,
      o.postal_code,
    ]
      .filter(Boolean)
      .join(", ");
    const seatsTotal = detail.licenses.reduce((n, l) => n + l.total_seats, 0);
    const seatsUsed = detail.licenses.reduce((n, l) => n + l.used_seats, 0);
    return (
      <section aria-label={`Organization ${o.name}`}>
        <button
          onClick={() => onSelect(null)}
          style={{
            background: "none",
            border: "none",
            color: COLORS.accentMutedBlue,
            cursor: "pointer",
            fontSize: 14,
            padding: 0,
          }}
        >
          ← Organizations
        </button>
        <div style={{ ...CARD, marginTop: SPACING.md }}>
          <h2 style={{ margin: 0 }}>
            {o.name}{" "}
            <span style={{ fontSize: 13, color: "#666" }}>[{o.status}]</span>
          </h2>
          <p style={{ margin: "4px 0", color: "#555", fontSize: 14 }}>
            {o.org_type} · {o.tier} tier
            {o.community_size ? ` · size ${o.community_size}` : ""}
          </p>
          <p style={{ margin: "4px 0", fontSize: 14 }}>
            Contact: {o.contact_email}
            {o.phone ? ` · ${o.phone}` : ""}
          </p>
          {address && (
            <p style={{ margin: "4px 0", fontSize: 14 }}>{address}</p>
          )}
          {o.slug && (
            <p style={{ margin: "4px 0", fontSize: 14 }}>
              Public page:{" "}
              <a
                href={`/for/${o.slug}`}
                target="_blank"
                rel="noreferrer"
                style={{ color: COLORS.accentMutedBlue }}
              >
                mynaani.com/for/{o.slug}
              </a>
            </p>
          )}
        </div>

        <div
          style={{
            display: "flex",
            gap: SPACING.md,
            marginTop: SPACING.md,
            flexWrap: "wrap",
          }}
        >
          <div style={{ ...CARD, flex: 1 }}>
            <div style={{ fontSize: 13, color: "#555" }}>Seats</div>
            <div style={{ fontSize: 24, fontWeight: 600 }}>
              {seatsUsed} / {seatsTotal} used
            </div>
            <div style={{ fontSize: 13, color: "#666" }}>
              {detail.codes_issued} codes issued
            </div>
          </div>
          <div style={{ ...CARD, flex: 1 }}>
            <div style={{ fontSize: 13, color: "#555" }}>Licenses</div>
            {detail.licenses.length === 0 ? (
              <div style={{ fontSize: 14, color: "#666" }}>None yet.</div>
            ) : (
              detail.licenses.map((l) => (
                <LicenseRow
                  key={l.id}
                  license={l}
                  onChanged={() => reload(o.id)}
                />
              ))
            )}
          </div>
        </div>

        {detail.contacts.length > 0 && (
          <>
            <h3 style={{ marginTop: SPACING.lg }}>Contacts</h3>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: 14,
              }}
            >
              <tbody>
                {detail.contacts.map((c) => (
                  <tr key={c.id}>
                    <td style={TD}>
                      {c.name}
                      {c.is_primary ? " (primary)" : ""}
                    </td>
                    <td style={TD}>{c.email ?? "—"}</td>
                    <td style={TD}>{c.phone ?? "—"}</td>
                    <td style={TD}>{c.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        <h3 style={{ marginTop: SPACING.lg }}>Audit trail</h3>
        {detail.audit.length === 0 ? (
          <p style={{ color: "#666" }}>Nothing recorded yet.</p>
        ) : (
          <table
            style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}
          >
            <tbody>
              {detail.audit.map((a, i) => (
                <tr key={i}>
                  <td style={{ ...TD, whiteSpace: "nowrap" }}>
                    {a.created_at?.slice(0, 16).replace("T", " ") ?? "—"}
                  </td>
                  <td style={TD}>{a.action}</td>
                  <td style={TD}>{a.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    );
  }

  return (
    <section aria-label="Organizations">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h2 style={{ marginTop: 0 }}>Organizations</h2>
        <button
          onClick={onNewOrg}
          style={{
            padding: `${SPACING.sm}px ${SPACING.md}px`,
            fontSize: 14,
            fontWeight: 600,
            color: "#fff",
            backgroundColor: COLORS.accentMutedBlue,
            border: "none",
            borderRadius: RADIUS.md,
            cursor: "pointer",
          }}
        >
          + New organization
        </button>
      </div>
      <div style={{ display: "flex", gap: SPACING.sm }}>
        <input
          aria-label="Search organizations"
          placeholder="Search name, email, or slug"
          style={INPUT}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void search()}
        />
        <button onClick={() => void search()} style={{ cursor: "pointer" }}>
          Search
        </button>
      </div>
      {error && <p style={{ color: COLORS.errorConfirm }}>{error}</p>}
      {orgs.length > 0 && (
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
              <th style={TH}>Name</th>
              <th style={TH}>Status</th>
              <th style={TH}>Type</th>
              <th style={TH}>Tier</th>
              <th style={TH}>Slug</th>
              <th style={TH}>Seats</th>
            </tr>
          </thead>
          <tbody>
            {orgs.map((o) => (
              <tr key={o.id}>
                <td style={TD}>
                  <button
                    onClick={() => onSelect(o.id)}
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
                    {o.name}
                  </button>
                </td>
                <td style={TD}>{o.status}</td>
                <td style={TD}>{o.org_type}</td>
                <td style={TD}>{o.tier}</td>
                <td style={TD}>{o.slug ?? "—"}</td>
                <td style={TD}>
                  {o.seats_used}/{o.seats_total}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

const ACT: React.CSSProperties = {
  fontSize: 13,
  color: COLORS.accentMutedBlue,
  background: "none",
  border: "none",
  cursor: "pointer",
  padding: "0 6px 0 0",
};

/**
 * One license row with lifecycle actions: edit seats/expiry, suspend or
 * reinstate, and top up codes. Every action maps to a staff-gated API
 * and writes an audit entry (ADMIN-OPS E1).
 */
function LicenseRow({
  license: l,
  onChanged,
}: {
  license: OrgDetail["licenses"][number];
  onChanged: () => void;
}) {
  const [msg, setMsg] = useState("");
  const suspended = l.status === "suspended";

  const run = async (fn: () => Promise<unknown>, ok: string) => {
    setMsg("");
    try {
      await fn();
      setMsg(ok);
      onChanged();
    } catch {
      setMsg("That didn't go through — try again.");
    }
  };

  const edit = () => {
    const seats = window.prompt("Seats (total):", String(l.total_seats));
    if (seats === null) return;
    const n = parseInt(seats, 10);
    if (!Number.isFinite(n) || n < 1) {
      setMsg("Seats must be a whole number ≥ 1.");
      return;
    }
    const expiry = window.prompt(
      "License end date (YYYY-MM-DD, blank keeps current):",
      l.expires_at?.slice(0, 10) ?? "",
    );
    if (expiry === null) return;
    void run(
      () =>
        apiClient.patch(`/api/v1/billing/org/license/${l.id}`, {
          total_seats: n,
          expires_at: expiry ? `${expiry}T00:00:00Z` : undefined,
        }),
      "Saved.",
    );
  };

  const addCodes = () => {
    const c = window.prompt("How many additional codes?", "5");
    if (c === null) return;
    const n = parseInt(c, 10);
    if (!Number.isFinite(n) || n < 1 || n > 1000) {
      setMsg("Codes must be 1–1000.");
      return;
    }
    void run(async () => {
      const r = await apiClient.post<{ codes: string[] }>(
        `/api/v1/billing/org/${l.id}/codes`,
        { count: n },
      );
      setMsg(`${n} new codes — copy now: ${r.data.codes.join(", ")}`);
    }, "");
  };

  const toggle = () => {
    if (suspended) {
      void run(
        () =>
          apiClient.post(`/api/v1/billing/org/license/${l.id}/reinstate`, {}),
        "License reinstated.",
      );
      return;
    }
    const reason = window.prompt(
      "Suspend this license? Learners keep existing access; new code redemption stops. Reason:",
      "",
    );
    if (!reason) return;
    void run(
      () =>
        apiClient.post(`/api/v1/billing/org/license/${l.id}/suspend`, {
          reason,
        }),
      "License suspended.",
    );
  };

  return (
    <div style={{ fontSize: 14, marginBottom: SPACING.sm }}>
      <div>
        {l.used_seats}/{l.total_seats} seats · ends{" "}
        {l.expires_at?.slice(0, 10) ?? "—"}
        {suspended && (
          <span style={{ color: COLORS.errorConfirm }}> · suspended</span>
        )}
      </div>
      {suspended && l.suspension_reason && (
        <div style={{ fontSize: 12, color: "#666" }}>
          reason: {l.suspension_reason}
        </div>
      )}
      <div>
        <button style={ACT} onClick={edit}>
          edit
        </button>
        <button style={ACT} onClick={addCodes}>
          +codes
        </button>
        <button style={ACT} onClick={toggle}>
          {suspended ? "reinstate" : "suspend"}
        </button>
      </div>
      {msg && (
        <div
          role="status"
          style={{ fontSize: 12, color: COLORS.accentDesatGreen, marginTop: 2 }}
        >
          {msg}
        </div>
      )}
    </div>
  );
}
