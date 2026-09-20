/**
 * ForCommunitiesPage — bid-17 B2B marketing surface (ADR-0034 dark
 * marketing palette).
 *
 * Verifies the bid-17 structure: charcoal hero + proof grid + objection
 * block + business-case section + research cards + pricing table + CTA
 * band, the marketing exemption marker, preserved integrations (facility
 * chat journey, /partners routing, tel: line, founding-partner pricing),
 * and honest evidence-first copy.
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

describe("ForCommunitiesPage — bid-17 B2B marketing surface", () => {
  it("carries the marketing exemption marker and bid-17 structure", async () => {
    const host = await render();
    const page = host.querySelector<HTMLElement>(
      '[data-contract-exemption="marketing.b2b"]',
    );
    expect(page).not.toBeNull();
    expect(page!.textContent).toContain(
      "AI learning your residents actually finish",
    );
    expect(page!.textContent).toContain("Staff hours you never spend");
    expect(page!.textContent).toContain("The case, in numbers");
    expect(page!.textContent).toContain("The business case");
    // Five proof cards with real evidence.
    expect(page!.textContent).toContain("57→28");
    expect(page!.textContent).toContain("80%");
    expect(page!.textContent).toContain("55→75");
    // Logo: K-6 linework icon on dark nav.
    expect(
      page!.querySelector('img[src="/mynaani-icon-linework-dark.svg"]'),
    ).not.toBeNull();
  });

  it("leads with the geragogy differentiator and published pricing", async () => {
    const host = await render();
    const text = host.textContent!;
    expect(text).toContain("geragogy");
    expect(text).toContain("patent-pending");
    // Cited evidence — linked Sources section.
    expect(text).toContain("Pew Research Center");
    expect(text).toContain("Hasher");
    const sourceLinks = host.querySelectorAll(
      '#b2b-sources ~ ul a[href^="https://"]',
    );
    expect(sourceLinks.length).toBeGreaterThanOrEqual(5);
    // Downloadable research briefs.
    expect(
      host.querySelector('a[href="/whitepapers/the-ai-gap.pdf"]'),
    ).not.toBeNull();
    expect(
      host.querySelector(
        'a[href="/whitepapers/geragogy-the-key-to-learning.pdf"]',
      ),
    ).not.toBeNull();
    // Published founding-partner pricing (B2B-PRICING-003/004).
    expect(text).toContain("Founding Partner rates");
    expect(text).toContain("$375 / year");
    expect(text).toContain("$850 / year");
    expect(text).toContain("Working with procurement");
    // Pricing reachable from nav.
    expect(host.querySelector('a[href="#pricing"]')).not.toBeNull();
  });

  it("routes contact to real forms — no mailto pickers, no invented proof", async () => {
    const host = await render();
    // No mailto pickers anywhere.
    const mailtoCtas = host.querySelectorAll<HTMLAnchorElement>(
      'a[href^="mailto:hello@mynaani.com"]',
    );
    expect(mailtoCtas.length).toBe(0);
    // "Start a conversation" routes to the senior-care form.
    const convo = [...host.querySelectorAll("a")].filter(
      (a) => a.textContent?.trim() === "Start a conversation",
    );
    expect(convo.length).toBeGreaterThanOrEqual(2);
    const hrefs = convo.map((a) => a.getAttribute("href"));
    expect(hrefs).toContain("/partners");
    // Toll-free line.
    expect(host.querySelector('a[href="tel:+18774094144"]')).not.toBeNull();
    // Honesty guard: no fabricated social proof or urgency copy.
    expect(host.textContent).toMatch(/Pew Research Center/);
    expect(host.textContent).not.toMatch(/trusted by|limited time|act now/i);
    // Way back to the learner surface.
    const learnerLinks = host.querySelectorAll('a[href="/"]');
    expect(learnerLinks.length).toBeGreaterThanOrEqual(1);
  });
});
