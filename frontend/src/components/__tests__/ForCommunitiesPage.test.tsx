/**
 * ForCommunitiesPage — B2B marketing surface (B2B-LANDING-001, ADR-0030).
 *
 * Verifies the Candoo-pattern structure: outcome headline, contact CTA to
 * the real address, outcome cards with labelled icons, program list,
 * honest founding-partner framing (no invented stats/logos), and the
 * marketing exemption marker.
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import ForCommunitiesPage from "../ForCommunitiesPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(MemoryRouter, null, createElement(ForCommunitiesPage)),
    );
  });
  return host;
}

describe("ForCommunitiesPage — B2B marketing surface", () => {
  it("carries the marketing exemption marker and learner-safe structure", async () => {
    const host = await render();
    const page = host.querySelector<HTMLElement>(
      '[data-contract-exemption="marketing.b2b"]',
    );
    expect(page).not.toBeNull();
    // Outcome headline + sections exist.
    expect(page!.textContent).toContain("Geragogy");
    expect(page!.textContent).toContain("Why communities partner with mynaani");
    expect(page!.textContent).toContain("founding partnership");
    // Three outcome cards, each icon + text label.
    expect(page!.querySelectorAll("h3").length).toBe(3);
    expect(page!.querySelectorAll("svg[aria-hidden]").length).toBe(3);
  });

  it("leads with the geragogy + patent-pending differentiator", async () => {
    const host = await render();
    const text = host.textContent!;
    expect(text).toContain("Geragogy");
    expect(text).toContain("geragogy");
    expect(text).toContain("patent-pending");
    expect(text).toContain("What geragogy is");
    expect(text).toContain("How geragogy shapes every layer");
    // Cited evidence, not invented proof.
    expect(text).toContain("Pew Research Center");
    expect(text).toContain("Hasher");
  });

  it("routes contact to the real address — no invented proof", async () => {
    const host = await render();
    const ctas = host.querySelectorAll<HTMLAnchorElement>(
      'a[href^="mailto:hello@mynaani.com"]',
    );
    expect(ctas.length).toBeGreaterThanOrEqual(2);
    // Honesty guard: stats present are attributed; no fabricated social
    // proof or urgency copy.
    expect(host.textContent).toMatch(/Pew Research Center/);
    expect(host.textContent).not.toMatch(/trusted by|limited time|act now/i);
    // Way back to the learner surface exists (header + hero + footer).
    const learnerLinks = host.querySelectorAll('a[href="/"]');
    expect(learnerLinks.length).toBeGreaterThanOrEqual(2);
  });
});
