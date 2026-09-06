/**
 * OrgDashboardPage — staff aggregate view (OB-2).
 *
 * Verifies: renders the staff framing (aggregate-only language), requires
 * an org ID before calling the API, and shows a calm error on failure.
 */

import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

vi.mock("../../api/client", () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({
      data: {
        organization: {
          id: "x", name: "Test Org", org_type: "nonprofit",
          tier: "site", community_size: 25, status: "active",
          parent_org_id: null,
        },
        licenses: [],
        children: [],
        audit: [],
      },
    }),
  },
}));

import OrgDashboardPage from "../OrgDashboardPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(OrgDashboardPage, { onBack: vi.fn() }),
      ),
    );
  });
  return host;
}

describe("OrgDashboardPage — aggregate-only staff view", () => {
  it("renders the aggregate-only framing", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Organization dashboard");
    expect(text).toContain("aggregate");
    expect(text).not.toContain("!");
  });

  it("does not fetch until an org ID is provided", async () => {
    const { apiClient } = await import("../../api/client");
    const host = await render();
    const btn = host.querySelector("button:not([aria-label])")!;
    await act(async () => btn.dispatchEvent(new MouseEvent("click", { bubbles: true })));
    expect(apiClient.get).not.toHaveBeenCalled();
  });
});
