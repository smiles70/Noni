/**
 * Footer — shared fat footer (MKT-FOOTER-001).
 *
 * Verifies the GetSetUp-aligned structure: contentinfo landmark, brand
 * mark, doormat nav row covering every public surface, and the legal
 * row (Privacy + Terms + copyright). Copy falls back to the static
 * legal minimum when /api/site/footer is unreachable — which it is in
 * the jsdom test environment — so these assertions run against the
 * fallback content.
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import Footer from "../Footer";

async function render(currentPath?: string) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(MemoryRouter, null, createElement(Footer, { currentPath })),
    );
  });
  return host;
}

describe("Footer — shared site footer", () => {
  it("renders a single contentinfo landmark", async () => {
    const host = await render();
    const footers = host.querySelectorAll("footer");
    expect(footers.length).toBe(1);
  });

  it("carries the brand mark", async () => {
    const host = await render();
    const img = host.querySelector('footer img[alt="mynaani"]');
    expect(img).toBeTruthy();
  });

  it("exposes the doormat nav row for all public surfaces", async () => {
    const host = await render();
    const nav = host.querySelector('footer nav[aria-label="Site"]');
    expect(nav).toBeTruthy();
    const text = nav?.textContent ?? "";
    for (const label of [
      "For learners",
      "For caregivers",
      "Be our partner",
      "Gift",
      "About us",
      "Help",
    ]) {
      expect(text).toContain(label);
    }
  });

  it("exposes Privacy and Terms in the legal row (CCPA conspicuous link)", async () => {
    const host = await render();
    const links = [...host.querySelectorAll("footer a")].map((a) =>
      a.getAttribute("href"),
    );
    expect(links).toContain("/privacy");
    expect(links).toContain("/terms");
  });

  it("shows copyright with the current year", async () => {
    const host = await render();
    const text = host.querySelector("footer")?.textContent ?? "";
    expect(text).toContain(`© ${new Date().getFullYear()} mynaani`);
  });

  it("shows a calm contact line with phone and email links", async () => {
    const host = await render();
    const footer = host.querySelector("footer");
    const text = footer?.textContent ?? "";
    expect(text).toContain("connect with you");
    const hrefs = [...(footer?.querySelectorAll("a") ?? [])].map((a) =>
      a.getAttribute("href"),
    );
    expect(hrefs).toContain("tel:+18774094144");
    expect(hrefs).toContain("mailto:help@mynaani.com");
  });

  it("marks the current page link with aria-current", async () => {
    const host = await render("/caregiver");
    const current = host.querySelector('footer a[aria-current="page"]');
    expect(current?.getAttribute("href")).toBe("/caregiver");
  });
});
