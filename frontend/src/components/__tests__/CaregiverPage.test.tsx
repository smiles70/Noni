/**
 * CaregiverPage — marketing surface for caregivers giving mynaani as a gift.
 *
 * Verifies the mirrored structure: hero, outcome cards, how-it-works,
 * gift CTA, whitepaper cards, source list, marketing exemption marker,
 * and honest contact routing.
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import CaregiverPage from "../CaregiverPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(MemoryRouter, null, createElement(CaregiverPage)),
    );
  });
  return host;
}

describe("CaregiverPage — marketing surface", () => {
  it("carries the marketing exemption marker and caregiver structure", async () => {
    const host = await render();
    const page = host.querySelector<HTMLElement>(
      '[data-contract-exemption="marketing.caregiver"]',
    );
    expect(page).not.toBeNull();
    // Hero + sections exist.
    expect(page!.textContent).toContain("Give calm, self-paced AI learning");
    expect(page!.textContent).toContain("How gifting works");
    expect(page!.textContent).toContain("What the gift includes");
    expect(page!.textContent).toContain("Sources");
    // Three outcome cards.
    const outcomes = page!.querySelector("#caregiver-difference")!
      .parentElement as HTMLElement;
    expect(outcomes.querySelectorAll("h3").length).toBe(3);
  });

  it("routes the caregiver to the gift checkout and honest contact", async () => {
    const host = await render();
    const text = host.textContent!;
    expect(text).toContain("geragogy");
    // Gift CTA appears in hero, header, and gift section.
    const giftLinks =
      host.querySelectorAll<HTMLAnchorElement>('a[href="/gift"]');
    expect(giftLinks.length).toBeGreaterThanOrEqual(3);
    expect(giftLinks[0]!.textContent).toMatch(/Gift mynaani/i);
    // Whitepapers are reachable.
    expect(
      host.querySelector('a[href="/whitepapers/the-ai-gap.pdf"]'),
    ).not.toBeNull();
    expect(
      host.querySelector(
        'a[href="/whitepapers/geragogy-the-key-to-learning.pdf"]',
      ),
    ).not.toBeNull();
    // Sources are linked.
    const sourceLinks = host.querySelectorAll(
      '#caregiver-sources ~ ul a[href^="https://"]',
    );
    expect(sourceLinks.length).toBeGreaterThanOrEqual(5);
    // Contact is the real address, no invented proof.
    const ctas = host.querySelectorAll<HTMLAnchorElement>(
      'a[href^="mailto:hello@mynaani.com"]',
    );
    expect(ctas.length).toBeGreaterThanOrEqual(2);
    expect(text).not.toMatch(/trusted by|limited time|act now/i);
    // Way back to learner + facility surfaces.
    const learnerLinks = host.querySelectorAll('a[href="/"]');
    expect(learnerLinks.length).toBeGreaterThanOrEqual(2);
    const facilityLink = host.querySelector('a[href="/for-communities"]');
    expect(facilityLink).not.toBeNull();
  });
});
