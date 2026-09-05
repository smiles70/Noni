/**
 * Landing page brand mark — BRAND-LOGO-001.
 *
 * Verifies the logo renders in the NN/g-validated top-left landmark
 * position, non-interactive, with alt text, inside the contract-exempt
 * hero (ADR-0029).
 *
 * Evidence: .ai/intake/2026-09-05-hero-logo-placement-001.md
 */

import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

vi.mock("../../api/landing", () => ({
  loadLandingPage: vi.fn(async () => ({
    hero: { headline: "H", subheadline: "S" },
    introduction: { title: "", body: "" },
    what_mynaani_does: { title: "", items: [] },
    how_it_feels: { title: "", items: [] },
    trust_and_safety: { title: "", body: "" },
    call_to_action: { primary: { label: "Begin" } },
    closing: { body: "" },
  })),
}));

vi.mock("../../api/envelope", () => ({
  loadEnvelope: vi.fn(async () => ({
    state_id: "landing.page",
    authorized_components: [
      "Heading",
      "Body",
      "Button",
      "Card",
      "Field",
      "List",
      "Divider",
      "Indicator",
      "ConfirmDialog",
      "PendingBanner",
      "BlockedNotice",
    ],
    interaction_limits: {
      max_primary_actions: 5,
      max_irreversible_actions: 1,
      max_highlighted_recommendations: 1,
      max_visible_text_levels: 3,
    },
    layout_constraints: {
      grid_base_px: 8,
      allowed_spacing_px: [4, 8, 16, 24, 32, 48],
      spatial_stability: true,
      reflow_permitted: false,
    },
    transition_permissions: [],
  })),
}));

import LandingPage from "../LandingPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(LandingPage, { onBegin: () => {} }),
      ),
    );
  });
  return host;
}

describe("LandingPage — brand logo (BRAND-LOGO-001)", () => {
  it("renders the mynaani logo in the upper-left, non-interactive", async () => {
    const host = await render();
    const logo = host.querySelector<HTMLImageElement>('img[alt="mynaani"]');
    expect(logo).not.toBeNull();
    expect(logo!.src).toContain("/mynaani-logo.webp");
    // Non-interactive: not wrapped in a link or button.
    expect(logo!.closest("a")).toBeNull();
    expect(logo!.closest("button")).toBeNull();
    // Marked inside the ADR-0029 contract exemption for audit.
    expect(logo!.dataset.contractExemption).toBe("landing.hero");
  });
});

describe("LandingPage — brand plate (BRAND-LOGO-002)", () => {
  it("sits the logo on a calm surface plate in the upper-left landmark", async () => {
    const host = await render();
    const logo = host.querySelector<HTMLImageElement>('img[alt="mynaani"]');
    expect(logo).not.toBeNull();
    const plate = logo!.closest<HTMLElement>(
      '[data-brand-plate="landing.hero"]',
    );
    expect(plate).not.toBeNull();
    // Landmark position preserved (NN/g top-left).
    expect(plate!.style.position).toBe("absolute");
    expect(plate!.style.top).toBe("32px");
    expect(plate!.style.left).toBe("32px");
    // Surface plate: COLORS.surface (#FAFAF8) at 85% opacity, RADIUS.lg.
    expect(plate!.style.backgroundColor).toBe("rgba(250, 250, 248, 0.85)");
    expect(plate!.style.borderRadius).toBe("12px");
    // Contract audit markers retained on plate and mark.
    expect(plate!.dataset.contractExemption).toBe("landing.hero");
    // Plate is non-interactive too.
    expect(plate!.closest("a")).toBeNull();
    expect(plate!.closest("button")).toBeNull();
  });
});

describe("LandingPage — B2B pathway entry (B2B-LANDING-001)", () => {
  it("offers a calm top-right text link to /for-communities", async () => {
    const host = await render();
    const link = host.querySelector<HTMLAnchorElement>(
      'a[href="/for-communities"]',
    );
    expect(link).not.toBeNull();
    expect(link!.textContent).toBe("For senior living communities");
    expect(link!.style.position).toBe("absolute");
    expect(link!.style.top).toBe("32px");
    expect(link!.style.right).toBe("32px");
    // Audit marker inside the ADR-0029 exempt hero.
    expect(link!.dataset.contractExemption).toBe("landing.hero");
    // B2B-ENTRY-001: ghost-button affordance (bordered, still secondary).
    expect(link!.style.border).toContain("1px solid");
  });
});
