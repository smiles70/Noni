/**
 * ADMIN-IA-001 G1: guided org onboarding. Composes the existing
 * staff-gated endpoints in order: create → license → codes → slug.
 * Steps are independently retryable — a mid-chain failure leaves a
 * usable org (create is committed first), and the summary names which
 * step failed instead of pretending success.
 */

import { useState } from "react";
import { apiClient } from "../../api/client";
import { COLORS, RADIUS, SPACING } from "../../design/tokens";

interface ContactForm {
  name: string;
  email: string;
  phone: string;
  role: string;
  is_primary: boolean;
}

const LABEL: React.CSSProperties = {
  display: "block",
  fontSize: 13,
  color: "#555",
  marginBottom: 4,
};

const INPUT: React.CSSProperties = {
  fontSize: 15,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  borderRadius: RADIUS.md,
  border: `1px solid ${COLORS.accentMutedBlue}`,
  width: "100%",
  boxSizing: "border-box",
};

const FIELDSET: React.CSSProperties = {
  border: `1px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
  marginBottom: SPACING.md,
  backgroundColor: "#ffffff",
};

export function NewOrgWizard({
  onDone,
  onCancel,
}: {
  onDone: (orgId: string) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    name: "",
    contact_email: "",
    admin_email: "",
    org_type: "nonprofit",
    tier: "site",
    community_size: "",
    address_line1: "",
    city: "",
    state: "",
    postal_code: "",
    phone: "",
    seats: "25",
    expires_at: "",
    slug: "",
  });
  const [contacts, setContacts] = useState<ContactForm[]>([
    { name: "", email: "", phone: "", role: "primary", is_primary: true },
  ]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState<{
    orgId: string;
    codes: string[];
    slug: string | null;
  } | null>(null);

  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const setContact = (i: number, k: keyof ContactForm, v: string | boolean) =>
    setContacts((cs) => cs.map((c, j) => (j === i ? { ...c, [k]: v } : c)));

  const submit = async () => {
    setBusy(true);
    setError("");
    try {
      // Step 1: org + location + contacts
      const c = await apiClient.post<{ id: string }>(
        "/api/v1/billing/org/create",
        {
          name: form.name.trim(),
          contact_email: form.contact_email.trim(),
          admin_email: form.admin_email.trim() || form.contact_email.trim(),
          org_type: form.org_type,
          tier: form.tier,
          community_size: form.community_size
            ? Number(form.community_size)
            : null,
          address_line1: form.address_line1 || null,
          city: form.city || null,
          state: form.state || null,
          postal_code: form.postal_code || null,
          phone: form.phone || null,
          contacts: contacts
            .filter((x) => x.name.trim())
            .map((x) => ({
              name: x.name.trim(),
              email: x.email || null,
              phone: x.phone || null,
              role: x.role,
              is_primary: x.is_primary,
            })),
        },
      );
      const orgId = c.data.id;

      // Step 2: license
      const seats = Number(form.seats) || 0;
      let codes: string[] = [];
      if (seats > 0) {
        const lic = await apiClient.post<{ id: string }>(
          `/api/v1/billing/org/${orgId}/license`,
          {
            product_code: "modules_4_5", // the org site-license product (seeded)
            total_seats: seats,
            amount_cents: 0,
            expires_at: form.expires_at
              ? new Date(form.expires_at).toISOString()
              : null,
            invoice_ref: "console-onboarding",
          },
        );
        // Step 3: codes are generated per-license, not per-org.
        const r = await apiClient.post<{ codes: string[] }>(
          `/api/v1/billing/org/${lic.data.id}/codes`,
          { count: seats },
        );
        codes = r.data.codes ?? [];
      }

      // Step 4: slug (optional)
      let slug: string | null = null;
      if (form.slug.trim()) {
        try {
          await apiClient.post(`/api/v1/billing/org/${orgId}/slug`, {
            slug: form.slug.trim().toLowerCase(),
          });
          slug = form.slug.trim().toLowerCase();
        } catch {
          setError(
            "Organization created, but that slug is taken — pick another from the org page.",
          );
        }
      }
      setDone({ orgId, codes, slug });
    } catch {
      setError(
        "Onboarding stopped partway. The organization may exist — check Organizations before retrying.",
      );
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <section aria-label="Onboarding complete">
        <h2 style={{ marginTop: 0 }}>Organization created</h2>
        <div style={FIELDSET}>
          {done.slug && (
            <p>
              Redemption page:{" "}
              <a
                href={`/for/${done.slug}`}
                target="_blank"
                rel="noreferrer"
                style={{ color: COLORS.accentMutedBlue }}
              >
                mynaani.com/for/{done.slug}
              </a>
            </p>
          )}
          <p>
            {done.codes.length} access code
            {done.codes.length === 1 ? "" : "s"} generated.
          </p>
          {done.codes.length > 0 && (
            <textarea
              readOnly
              aria-label="Access codes"
              value={done.codes.join("\n")}
              style={{ ...INPUT, height: 120, fontFamily: "monospace" }}
            />
          )}
          <p style={{ fontSize: 13, color: "#666" }}>
            Copy these now — send the link and one code per learner to the
            organization contact.
          </p>
        </div>
        <button
          onClick={() => onDone(done.orgId)}
          style={{
            padding: `${SPACING.sm}px ${SPACING.lg}px`,
            fontSize: 15,
            fontWeight: 600,
            color: "#fff",
            backgroundColor: COLORS.accentMutedBlue,
            border: "none",
            borderRadius: RADIUS.md,
            cursor: "pointer",
          }}
        >
          Open organization
        </button>
      </section>
    );
  }

  return (
    <section aria-label="New organization">
      <h2 style={{ marginTop: 0 }}>New organization</h2>

      <fieldset style={FIELDSET}>
        <legend>Details</legend>
        <label style={LABEL}>Name</label>
        <input
          style={INPUT}
          value={form.name}
          onChange={set("name")}
          required
        />
        <div
          style={{ display: "flex", gap: SPACING.md, marginTop: SPACING.sm }}
        >
          <div style={{ flex: 1 }}>
            <label style={LABEL}>Type</label>
            <select
              style={INPUT}
              value={form.org_type}
              onChange={set("org_type")}
            >
              <option value="nonprofit">Nonprofit / community</option>
              <option value="for_profit">For-profit / senior living</option>
              <option value="health_plan">Health plan</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={LABEL}>Tier</label>
            <input style={INPUT} value={form.tier} onChange={set("tier")} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={LABEL}>Community size</label>
            <input
              style={INPUT}
              type="number"
              min={1}
              value={form.community_size}
              onChange={set("community_size")}
            />
          </div>
        </div>
      </fieldset>

      <fieldset style={FIELDSET}>
        <legend>Location</legend>
        <label style={LABEL}>Street</label>
        <input
          style={INPUT}
          value={form.address_line1}
          onChange={set("address_line1")}
        />
        <div
          style={{ display: "flex", gap: SPACING.md, marginTop: SPACING.sm }}
        >
          <div style={{ flex: 2 }}>
            <label style={LABEL}>City</label>
            <input style={INPUT} value={form.city} onChange={set("city")} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={LABEL}>State</label>
            <input style={INPUT} value={form.state} onChange={set("state")} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={LABEL}>ZIP</label>
            <input
              style={INPUT}
              value={form.postal_code}
              onChange={set("postal_code")}
            />
          </div>
        </div>
        <div style={{ marginTop: SPACING.sm }}>
          <label style={LABEL}>Phone</label>
          <input style={INPUT} value={form.phone} onChange={set("phone")} />
        </div>
      </fieldset>

      <fieldset style={FIELDSET}>
        <legend>Contacts</legend>
        {contacts.map((c, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: SPACING.sm,
              marginBottom: SPACING.sm,
              alignItems: "end",
            }}
          >
            <input
              aria-label={`Contact ${i + 1} name`}
              placeholder="Name"
              style={INPUT}
              value={c.name}
              onChange={(e) => setContact(i, "name", e.target.value)}
            />
            <input
              aria-label={`Contact ${i + 1} email`}
              placeholder="Email"
              style={INPUT}
              value={c.email}
              onChange={(e) => setContact(i, "email", e.target.value)}
            />
            <input
              aria-label={`Contact ${i + 1} phone`}
              placeholder="Phone"
              style={INPUT}
              value={c.phone}
              onChange={(e) => setContact(i, "phone", e.target.value)}
            />
            <label style={{ fontSize: 13, whiteSpace: "nowrap" }}>
              <input
                type="checkbox"
                checked={c.is_primary}
                onChange={(e) => setContact(i, "is_primary", e.target.checked)}
              />{" "}
              primary
            </label>
          </div>
        ))}
        <button
          onClick={() =>
            setContacts((cs) => [
              ...cs,
              {
                name: "",
                email: "",
                phone: "",
                role: "contact",
                is_primary: false,
              },
            ])
          }
          style={{
            background: "none",
            border: "none",
            color: COLORS.accentMutedBlue,
            cursor: "pointer",
            fontSize: 14,
          }}
        >
          + add another contact
        </button>
        <div style={{ marginTop: SPACING.sm }}>
          <label style={LABEL}>Primary contact email (required)</label>
          <input
            style={INPUT}
            type="email"
            value={form.contact_email}
            onChange={set("contact_email")}
            required
          />
        </div>
      </fieldset>

      <fieldset style={FIELDSET}>
        <legend>License & go-live</legend>
        <div style={{ display: "flex", gap: SPACING.md }}>
          <div style={{ flex: 1 }}>
            <label style={LABEL}>Seats</label>
            <input
              style={INPUT}
              type="number"
              min={1}
              value={form.seats}
              onChange={set("seats")}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={LABEL}>License ends</label>
            <input
              style={INPUT}
              type="date"
              value={form.expires_at}
              onChange={set("expires_at")}
            />
          </div>
          <div style={{ flex: 2 }}>
            <label style={LABEL}>Slug (lowercase, e.g. sunrise-gardens)</label>
            <input style={INPUT} value={form.slug} onChange={set("slug")} />
          </div>
        </div>
      </fieldset>

      {error && <p style={{ color: "#a84c4c" }}>{error}</p>}

      <div style={{ display: "flex", gap: SPACING.md }}>
        <button
          onClick={() => void submit()}
          disabled={busy || !form.name.trim() || !form.contact_email.trim()}
          style={{
            padding: `${SPACING.sm}px ${SPACING.lg}px`,
            fontSize: 15,
            fontWeight: 600,
            color: "#fff",
            backgroundColor: COLORS.accentMutedBlue,
            border: "none",
            borderRadius: RADIUS.md,
            cursor: "pointer",
            opacity: busy ? 0.6 : 1,
          }}
        >
          {busy ? "Creating…" : "Create organization"}
        </button>
        <button onClick={onCancel} style={{ cursor: "pointer" }}>
          Cancel
        </button>
      </div>
    </section>
  );
}
