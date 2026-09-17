/**
 * LandingFooter — mini-footer strip inside the fixed hero
 * (LEGAL-NAV-001).
 *
 * Verifies the strip renders the legal minimum — copyright plus
 * Privacy/Terms/Help — as a top-level contentinfo landmark. Runs
 * against the static fallback (the jsdom test environment cannot reach
 * /api/site/footer), which is exactly the content users see if the
 * endpoint is unreachable.
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import LandingFooter from "../LandingFooter";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(MemoryRouter, null, createElement(LandingFooter)),
    );
  });
  return host;
}

describe("LandingFooter — landing mini strip", () => {
  it("renders a contentinfo footer", async () => {
    const host = await render();
    expect(host.querySelector("footer")).toBeTruthy();
  });

  it("exposes Privacy, Terms, Help, and Contact links", async () => {
    const host = await render();
    const links = [...host.querySelectorAll("footer a")];
    const hrefs = links.map((a) => a.getAttribute("href"));
    expect(hrefs).toContain("/privacy");
    expect(hrefs).toContain("/terms");
    expect(hrefs).toContain("/help");
    const labels = links.map((a) => a.textContent);
    expect(labels).toContain("Contact");
  });

  it("shows copyright", async () => {
    const host = await render();
    const text = host.querySelector("footer")?.textContent ?? "";
    expect(text).toContain(`© ${new Date().getFullYear()} mynaani`);
  });
});
