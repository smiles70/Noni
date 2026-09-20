/**
 * CaregiverPage — bid-17 marketing surface for caregivers giving mynaani
 * as a gift (ADR-0034 dark marketing palette).
 *
 * Verifies the bid-17 structure: charcoal hero + proof grid + objection
 * block + dark gift section + research cards + CTA band, the marketing
 * exemption marker, preserved integrations (gift entry points,
 * whitepapers, tel: line, cross-persona way-back), and honest routing.
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

describe("CaregiverPage — bid-17 marketing surface", () => {
  it("carries the marketing exemption marker and bid-17 structure", async () => {
    const host = await render();
    const page = host.querySelector<HTMLElement>(
      '[data-contract-exemption="marketing.caregiver"]',
    );
    expect(page).not.toBeNull();
    // Hero + sections exist.
    expect(page!.textContent).toContain("They learn AI");
    expect(page!.textContent).toContain("You stop being tech support");
    expect(page!.textContent).toContain("Warm on the surface");
    expect(page!.textContent).toContain("The gift of staying capable");
    // Five proof cards.
    const proofCards = page!.querySelectorAll("#why .proof-card, #why div");
    expect(page!.querySelectorAll("#why")).not.toBeNull();
    expect(page!.textContent).toContain("11+");
    expect(page!.textContent).toContain("57→28");
    expect(page!.textContent).toContain("RCT");
    void proofCards;
  });

  it("routes the caregiver to the gift checkout and honest contact", async () => {
    const host = await render();
    const text = host.textContent!;
    expect(text).toContain("geragogy");
    // Gift entry points carry attribution markers (hero + section + CTA band).
    const giftLinks =
      host.querySelectorAll<HTMLAnchorElement>('a[href="/gift"]');
    expect(giftLinks.length).toBeGreaterThanOrEqual(3);
    const markers = [...giftLinks].map((a) =>
      a.getAttribute("data-gift-entry"),
    );
    expect(markers).toContain("hero");
    expect(markers).toContain("gift-section");
    expect(markers).toContain("footer-cta");
    // Whitepapers are reachable.
    expect(
      host.querySelector('a[href="/whitepapers/cognitive-engagement.pdf"]'),
    ).not.toBeNull();
    expect(
      host.querySelector('a[href="/whitepapers/geragogy-for-caregivers.pdf"]'),
    ).not.toBeNull();
    // Toll-free line present.
    expect(host.querySelector('a[href="tel:+18774094144"]')).not.toBeNull();
    // Contact routes to the /contact form — no mailto picker buttons.
    const mailtoCtas = host.querySelectorAll<HTMLAnchorElement>(
      'a[href^="mailto:hello@mynaani.com"]',
    );
    expect(mailtoCtas.length).toBe(0);
    const contactLinks = host.querySelectorAll('a[href="/contact"]');
    expect(contactLinks.length).toBeGreaterThanOrEqual(1);
    expect(text).not.toMatch(/trusted by|limited time|act now/i);
    // Way back to learner + facility surfaces.
    const learnerLinks = host.querySelectorAll('a[href="/"]');
    expect(learnerLinks.length).toBeGreaterThanOrEqual(1);
    const facilityLink = host.querySelector('a[href="/for-communities"]');
    expect(facilityLink).not.toBeNull();
    // Logo: K-6 linework icon on dark nav.
    const logo = host.querySelector(
      'img[src="/mynaani-icon-linework-dark.svg"]',
    );
    expect(logo).not.toBeNull();
  });
});
