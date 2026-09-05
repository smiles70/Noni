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

vi.mock("../../api/landing", () => ({
  loadLandingPage: vi.fn(async () => ({
    hero: { headline: "H", subheadline: "S" },
    introduction: { title: "Intro title", body: "Intro body." },
    what_mynaani_does: { title: "What title", items: ["Item A", "Item B"] },
    how_it_feels: { title: "Feel title", items: ["Item C"] },
    trust_and_safety: { title: "Trust title", body: "Trust body." },
    call_to_action: { primary: { label: "Begin" } },
    closing: { body: "Closing body." },
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
    root.render(createElement(LandingPage, { onBegin: () => {} }));
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

describe("LandingPage — scroll depth (SCROLL-DEPTH-001)", () => {
  it("offers a calm scroll affordance and renders all five content sections", async () => {
    const host = await render();

    // Scroll affordance: a text link in the action stack pointing at the
    // details region. Native anchor jump — no smooth-scroll motion.
    const link = host.querySelector<HTMLAnchorElement>(
      'a[href="#mynaani-details"]',
    );
    expect(link).not.toBeNull();
    expect(link!.textContent).toBe("More about mynaani");

    // Details region exists as a sibling AFTER the hero section.
    const details = host.querySelector<HTMLElement>("#mynaani-details");
    expect(details).not.toBeNull();
    expect(details!.tagName).toBe("MAIN");

    // All five API sections render — including trust_and_safety, the
    // legitimacy content previously gated behind a click.
    const sections = details!.querySelectorAll("section");
    expect(sections.length).toBe(5);
    const headings = details!.querySelectorAll("h2");
    expect(headings.length).toBe(4);
    expect(details!.textContent).toContain("Trust title");
    expect(details!.textContent).toContain("Item A");
    expect(details!.textContent).toContain("Closing body.");

    // Contract components only: lists and straight dividers present.
    expect(details!.querySelectorAll("ul").length).toBe(2);
    expect(details!.querySelectorAll("hr").length).toBe(4);
  });

  it("keeps the hero a full-viewport first screen in document flow", async () => {
    const host = await render();
    const hero = host.querySelector<HTMLElement>(
      'section[data-contract-exemption="landing.hero"]',
    );
    expect(hero).not.toBeNull();
    // In-flow (not fixed) so content can follow it; still one viewport tall.
    expect(hero!.style.position).toBe("relative");
    expect(hero!.style.height).toBe("100vh");
    // Details come after the hero in DOM order.
    const details = host.querySelector("#mynaani-details");
    expect(
      hero!.compareDocumentPosition(details!) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });
});
