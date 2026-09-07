/** ADMIN-REPORTING-001 — B2B activity reporting surface.
 *
 * Analytical, not operational: every number carries context — a named
 * window and, where a benchmark exists (seat utilization), the healthy
 * band. Aggregate-only by contract: counts and timestamps per org,
 * never learner names, unit rows, or confidence values.
 */
import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, RADIUS, SPACING } from "../../design/tokens";

interface OrgRow {
  org_id: string;
  org_name: string;
  status: string;
  tier: string | null;
  seats_total: number;
  seats_used: number;
  utilization_pct: number;
  codes_issued: number;
  codes_claimed_total: number;
  codes_claimed_in_window: number;
  learners_enrolled: number;
  active_learners_in_window: number;
  units_completed_in_window: number;
  last_activity_utc: string | null;
  staff_audit_events_in_window: number;
}

interface Report {
  window_days: number;
  generated_at_utc: string;
  orgs: OrgRow[];
}

interface OrgOption {
  id: string;
  name: string;
}

const CARD: React.CSSProperties = {
  backgroundColor: "#ffffff",
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
  minWidth: 160,
};

const TABLE: React.CSSProperties = {
  borderCollapse: "collapse",
  width: "100%",
  fontSize: 14,
  marginTop: SPACING.md,
};

const CELL: React.CSSProperties = {
  borderBottom: "1px solid #eee",
  padding: "8px 10px",
  textAlign: "left",
  verticalAlign: "top",
};

/** Utilization framing from RevOS benchmarks: <50% at-risk, 60–85%
 * healthy, >90% expansion signal. */
function utilizationLabel(pct: number): { text: string; color: string } {
  if (pct < 50) return { text: `${pct}% — at risk`, color: "#b3543f" };
  if (pct <= 85)
    return { text: `${pct}% — healthy`, color: COLORS.accentDesatGreen };
  return { text: `${pct}% — expansion`, color: COLORS.accentMutedBlue };
}

export default function ReportsView() {
  const [orgs, setOrgs] = useState<OrgOption[]>([]);
  const [orgId, setOrgId] = useState("");
  const [days, setDays] = useState(30);
  const [report, setReport] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient
      .get<OrgOption[]>("/api/v1/admin/orgs?q=")
      .then((r) => setOrgs(r.data))
      .catch(() => setOrgs([]));
  }, []);

  const run = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      const params = new URLSearchParams({ days: String(days) });
      if (orgId) params.set("org_id", orgId);
      const r = await apiClient.get<Report>(
        `/api/v1/admin/reports/org-activity?${params}`,
      );
      setReport(r.data);
    } catch {
      setError("Report failed — check the API.");
    } finally {
      setBusy(false);
    }
  }, [days, orgId]);

  return (
    <section aria-label="Reports">
      <h2 style={{ marginTop: 0 }}>Reports — customer activity</h2>
      <p style={{ fontSize: 14, color: COLORS.disabled, maxWidth: 640 }}>
        Aggregate org-level rollups over a sliding window. Counts and timestamps
        only — never individual learner records, unit detail, or confidence
        values. “Active learner” = a claimed seat with progress activity in the
        window.
      </p>

      <div
        style={{
          display: "flex",
          gap: SPACING.sm,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <label style={{ fontSize: 14 }}>
          Organization{" "}
          <select
            aria-label="Report scope"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
          >
            <option value="">All organizations</option>
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        </label>
        <label style={{ fontSize: 14 }}>
          Window{" "}
          <select
            aria-label="Report window"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            {[7, 30, 90, 365].map((d) => (
              <option key={d} value={d}>
                last {d} days
              </option>
            ))}
          </select>
        </label>
        <button
          onClick={() => void run()}
          disabled={busy}
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
          {busy ? "Running…" : "Run report"}
        </button>
      </div>
      {error && <p role="alert">{error}</p>}

      {report && (
        <>
          <p style={{ fontSize: 13, color: COLORS.disabled }}>
            Window: last {report.window_days} days · generated{" "}
            {report.generated_at_utc.slice(0, 19)}Z · {report.orgs.length}{" "}
            organization(s)
          </p>
          <div
            style={{
              display: "flex",
              gap: SPACING.md,
              flexWrap: "wrap",
            }}
          >
            <div style={CARD}>
              <div style={{ fontSize: 13, color: COLORS.disabled }}>
                Learners enrolled
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>
                {report.orgs.reduce((s, o) => s + o.learners_enrolled, 0)}
              </div>
            </div>
            <div style={CARD}>
              <div style={{ fontSize: 13, color: COLORS.disabled }}>
                Active in window
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>
                {report.orgs.reduce(
                  (s, o) => s + o.active_learners_in_window,
                  0,
                )}
              </div>
            </div>
            <div style={CARD}>
              <div style={{ fontSize: 13, color: COLORS.disabled }}>
                Units completed
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>
                {report.orgs.reduce(
                  (s, o) => s + o.units_completed_in_window,
                  0,
                )}
              </div>
            </div>
            <div style={CARD}>
              <div style={{ fontSize: 13, color: COLORS.disabled }}>
                Codes claimed in window
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>
                {report.orgs.reduce((s, o) => s + o.codes_claimed_in_window, 0)}
              </div>
            </div>
          </div>

          <table style={TABLE}>
            <thead>
              <tr>
                {[
                  "Organization",
                  "Status",
                  "Seats used",
                  "Utilization",
                  "Enrolled",
                  "Active",
                  "Units done",
                  "Last activity",
                ].map((h) => (
                  <th key={h} style={CELL}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {report.orgs.map((o) => {
                const u = utilizationLabel(o.utilization_pct);
                return (
                  <tr key={o.org_id}>
                    <td style={CELL}>{o.org_name}</td>
                    <td style={CELL}>{o.status}</td>
                    <td style={CELL}>
                      {o.seats_used}/{o.seats_total}
                    </td>
                    <td style={{ ...CELL, color: u.color }}>{u.text}</td>
                    <td style={CELL}>{o.learners_enrolled}</td>
                    <td style={CELL}>{o.active_learners_in_window}</td>
                    <td style={CELL}>{o.units_completed_in_window}</td>
                    <td style={CELL}>
                      {o.last_activity_utc?.slice(0, 10) ?? "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
