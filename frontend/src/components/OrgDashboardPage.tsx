/**
 * OrgDashboardPage — staff-facing aggregate-only org view (OB-2).
 *
 * Shows organization info, license seats, code counts, expiry state,
 * child-site aggregates, and the audit trail. Deliberately contains no
 * per-learner data — the privacy boundary is the feature.
 *
 * Geragogy contract: calm, token-only styles, existing components only.
 * Staff-only — the API enforces `require_staff`; this page renders what
 * the API returns or a calm error.
 */

import { useState } from "react";
import type { CSSProperties } from "react";
import { apiClient } from "../api/client";
import {
  BODY,
  CARD,
  FIELD,
  FIELD_LABEL,
  H1,
  H2,
  PAGE,
  PRIMARY_BTN,
  STACK,
} from "./AccountStyles";
import { COLORS, SPACING } from "../design/tokens";

interface License {
  license_id: string;
  product_code: string;
  total_seats: number;
  used_seats: number;
  codes_issued: number;
  codes_claimed: number;
  expires_at: string | null;
  expired: boolean;
  expiring_soon: boolean;
}

interface Dashboard {
  organization: {
    id: string;
    name: string;
    org_type: string;
    tier: string;
    community_size: number | null;
    status: string;
    parent_org_id: string | null;
  };
  licenses: License[];
  children: { id: string; name: string; status: string }[];
  audit: { action: string; detail: string; at: string }[];
}

export default function OrgDashboardPage({ onBack }: { onBack: () => void }) {
  const [orgId, setOrgId] = useState("");
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    if (!orgId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<Dashboard>(
        `/api/v1/billing/org/${orgId.trim()}/dashboard`,
      );
      setData(res.data);
    } catch {
      setError(
        "We could not load that organization. Check the ID and your staff access, then try again.",
      );
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={PAGE}>
      <button type="button" onClick={onBack} style={BACK_BTN} aria-label="Go back">
        ← Back
      </button>

      <h1 style={H1}>Organization dashboard</h1>
      <p style={BODY}>
        Staff view. Shows aggregate information only — seats and codes, never
        what individual learners do.
      </p>

      <div style={STACK}>
        <label htmlFor="org-id" style={FIELD_LABEL}>
          Organization ID
        </label>
        <input
          id="org-id"
          value={orgId}
          onChange={(e) => setOrgId(e.target.value)}
          style={FIELD}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        />
        <button
          type="button"
          onClick={load}
          disabled={loading || !orgId.trim()}
          style={PRIMARY_BTN}
        >
          {loading ? "Loading…" : "Load organization"}
        </button>
      </div>

      {error && (
        <p style={{ ...BODY, color: COLORS.errorConfirm }} role="alert">
          {error}
        </p>
      )}

      {data && (
        <>
          <section style={CARD}>
            <h2 style={H2}>{data.organization.name}</h2>
            <p style={BODY}>
              Type: {data.organization.org_type} · Tier: {data.organization.tier}
              {data.organization.community_size != null &&
                ` · Community size: ${data.organization.community_size}`}
              {" · Status: "}
              {data.organization.status}
            </p>
          </section>

          {data.licenses.map((l) => (
            <section key={l.license_id} style={CARD}>
              <h2 style={H2}>License — {l.product_code}</h2>
              <p style={BODY}>
                Seats: {l.used_seats} of {l.total_seats} used · Codes:{" "}
                {l.codes_claimed} of {l.codes_issued} claimed
              </p>
              <p style={BODY}>
                {l.expires_at
                  ? `Expires ${new Date(l.expires_at).toLocaleDateString()}${
                      l.expired
                        ? " — expired"
                        : l.expiring_soon
                          ? " — expires within 30 days"
                          : ""
                    }`
                  : "No expiry set"}
              </p>
            </section>
          ))}

          {data.children.length > 0 && (
            <section style={CARD}>
              <h2 style={H2}>Sites in this portfolio</h2>
              <ul>
                {data.children.map((c) => (
                  <li key={c.id} style={BODY}>
                    {c.name} — {c.status}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {data.audit.length > 0 && (
            <section style={CARD}>
              <h2 style={H2}>Recent activity</h2>
              <ul>
                {data.audit.map((a, i) => (
                  <li key={i} style={BODY}>
                    {new Date(a.at).toLocaleString()} — {a.action}
                    {a.detail ? ` (${a.detail})` : ""}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </main>
  );
}

const BACK_BTN: CSSProperties = {
  padding: `${SPACING.xs}px ${SPACING.md}px`,
  marginBottom: SPACING.md,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: 8,
  cursor: "pointer",
  fontSize: 16,
};
