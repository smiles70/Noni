/**
 * Staff admin console — /admin. Internal ops surface; enterprise density,
 * not geragogy. Gated by /api/v1/admin/whoami-check; the login card is
 * rendered by this page itself (the route is deliberately outside
 * RequireAuth — ADMIN-LOGIN-001). Navigation is organized by staff jobs
 * (Overview / Organizations / Accounts / Flags / Audit), per the
 * ADMIN-IA-001 research synthesis. Aggregate-only: never shows
 * individual learner progress — the boundary is structural.
 */

import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../design/tokens";
import OverviewView from "./admin/OverviewView";
import { OrgsView } from "./admin/OrgsView";
import { NewOrgWizard } from "./admin/NewOrgWizard";
import { AccountsView } from "./admin/AccountsView";
import { AuditView } from "./admin/AuditView";

const PAGE: React.CSSProperties = {
  minHeight: "100vh",
  backgroundColor: COLORS.surface,
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
};

const INPUT: React.CSSProperties = {
  fontSize: 15,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  borderRadius: RADIUS.md,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  width: 320,
};

const CELL: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "8px 10px",
  textAlign: "left",
};

const TABLE: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: 14,
  marginTop: SPACING.md,
};

interface FlagRow {
  id: string;
  account_id: string;
  flag: string;
  detail: string;
  created_at: string | null;
}

type View = "overview" | "orgs" | "accounts" | "flags" | "audit" | "new-org";

const NAV: { id: View; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "orgs", label: "Organizations" },
  { id: "accounts", label: "Accounts" },
  { id: "flags", label: "Flags" },
  { id: "audit", label: "Audit" },
];

export default function AdminConsolePage() {
  const [state, setState] = useState<"loading" | "staff" | "denied">("loading");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [busy, setBusy] = useState(false);
  const [view, setView] = useState<View>("overview");
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null);
  const [flags, setFlags] = useState<FlagRow[]>([]);

  useEffect(() => {
    apiClient
      .get<{ staff: boolean }>("/api/v1/admin/whoami-check")
      .then((r) => setState(r.data.staff ? "staff" : "denied"))
      .catch(() => setState("denied"));
  }, []);

  useEffect(() => {
    if (state === "staff" && view === "flags") {
      apiClient
        .get<{ flags: FlagRow[] }>("/api/v1/admin/flags")
        .then((r) => setFlags(r.data.flags))
        .catch(() => setFlags([]));
    }
  }, [state, view]);

  if (state === "loading")
    return <main style={{ ...PAGE, padding: SPACING.xl }}>Loading…</main>;

  const login = async () => {
    setBusy(true);
    setLoginError("");
    try {
      const r = await apiClient.post<{ staff: boolean; token: string }>(
        "/api/v1/admin/login",
        { username, password },
      );
      localStorage.setItem("mynaani.staff_token", r.data.token);
      setState("staff");
    } catch {
      setLoginError("That username or password didn't match. Try again.");
    } finally {
      setBusy(false);
    }
  };

  const signOut = () => {
    localStorage.removeItem("mynaani.staff_token");
    setState("denied");
  };

  const openOrg = (id: string) => {
    setSelectedOrg(id);
    setView("orgs");
  };

  if (state === "denied")
    return (
      <main
        style={{
          ...PAGE,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <form
          aria-label="Staff sign in"
          onSubmit={(e) => {
            e.preventDefault();
            void login();
          }}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: SPACING.md,
            padding: SPACING.xl,
            borderRadius: RADIUS.lg,
            backgroundColor: "#ffffff",
            border: `1px solid ${COLORS.accentMutedBlue}`,
            minWidth: 340,
          }}
        >
          <img
            src="/mynaani-logo.webp"
            alt="mynaani"
            style={{ width: 120, height: "auto" }}
          />
          <h1 style={{ fontSize: 18, margin: 0, fontWeight: 600 }}>
            Staff sign in
          </h1>
          <input
            aria-label="Username"
            style={{ ...INPUT, width: "100%", boxSizing: "border-box" }}
            placeholder="Username"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            aria-label="Password"
            style={{ ...INPUT, width: "100%", boxSizing: "border-box" }}
            placeholder="Password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            type="submit"
            disabled={busy}
            style={{
              width: "100%",
              padding: `${SPACING.sm}px ${SPACING.md}px`,
              borderRadius: RADIUS.md,
              border: "none",
              backgroundColor: COLORS.accentMutedBlue,
              color: "#fff",
              fontSize: 15,
              cursor: busy ? "default" : "pointer",
            }}
          >
            {busy ? "Signing in…" : "Log in"}
          </button>
          {loginError && (
            <p
              role="alert"
              style={{ color: COLORS.errorConfirm, fontSize: 14, margin: 0 }}
            >
              {loginError}
            </p>
          )}
        </form>
      </main>
    );

  return (
    <main style={PAGE} data-component="AdminConsole">
      {/* top bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: `${SPACING.md}px ${SPACING.xl}px`,
          borderBottom: "1px solid #e3e3de",
          backgroundColor: "#fafaf8",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm }}>
          <img
            src="/mynaani-logo.webp"
            alt="mynaani"
            style={{ width: 80, height: "auto" }}
          />
          <h1 style={{ fontSize: 18, margin: 0, fontWeight: 600 }}>
            staff console
          </h1>
        </div>
        <button type="button" onClick={signOut} style={{ fontSize: 13 }}>
          Sign out
        </button>
      </div>

      <div style={{ display: "flex", minHeight: "calc(100vh - 64px)" }}>
        {/* left nav — jobs, not tables */}
        <nav
          aria-label="Staff console sections"
          style={{
            width: 180,
            borderRight: "1px solid #e3e3de",
            padding: SPACING.lg,
            flexShrink: 0,
          }}
        >
          {NAV.map((n) => (
            <button
              key={n.id}
              onClick={() => {
                setView(n.id);
                if (n.id !== "orgs") setSelectedOrg(null);
              }}
              aria-current={view === n.id ? "page" : undefined}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                padding: `${SPACING.sm}px ${SPACING.md}px`,
                marginBottom: 2,
                fontSize: 15,
                fontWeight: view === n.id ? 600 : 400,
                color:
                  view === n.id ? COLORS.accentMutedBlue : COLORS.textPrimary,
                backgroundColor: view === n.id ? "#eef1f6" : "transparent",
                border: "none",
                borderRadius: RADIUS.md,
                cursor: "pointer",
              }}
            >
              {n.label}
            </button>
          ))}
        </nav>

        {/* work surface */}
        <div style={{ flex: 1, padding: SPACING.xl, minWidth: 0 }}>
          {view === "overview" && (
            <OverviewView
              onNewOrg={() => setView("new-org")}
              onOpenOrg={openOrg}
            />
          )}
          {view === "orgs" && (
            <OrgsView
              selected={selectedOrg}
              onSelect={setSelectedOrg}
              onNewOrg={() => setView("new-org")}
            />
          )}
          {view === "accounts" && <AccountsView />}
          {view === "audit" && <AuditView onOpenOrg={openOrg} />}
          {view === "new-org" && (
            <NewOrgWizard onDone={openOrg} onCancel={() => setView("orgs")} />
          )}
          {view === "flags" && (
            <section aria-label="Account flags">
              <h2 style={{ marginTop: 0 }}>Flags — sharing signals</h2>
              {flags.length === 0 ? (
                <p style={{ fontSize: 14, color: COLORS.disabled }}>
                  No flags — the weekly scan has found nothing to review.
                </p>
              ) : (
                <table style={TABLE}>
                  <thead>
                    <tr>
                      {["Account", "Flag", "Detail", "Date"].map((h) => (
                        <th key={h} style={CELL}>
                          {h}
                        </th>
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
          )}

          <p
            style={{
              marginTop: SPACING.xl,
              fontSize: 13,
              color: COLORS.disabled,
            }}
          >
            Internal ops. Aggregate data only — no individual learner records.
          </p>
        </div>
      </div>
    </main>
  );
}
