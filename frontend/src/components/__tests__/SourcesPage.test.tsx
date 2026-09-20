/**
 * SourcesPage — /sources shared evidence surface (PS-BID17-004).
 * Persona-partitioned groups, all external links reachable-shaped,
 * footer link contract.
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import SourcesPage from "../SourcesPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(createElement(MemoryRouter, null, createElement(SourcesPage)));
  });
  return host;
}

describe("SourcesPage — shared evidence surface", () => {
  it("renders both persona-partitioned source groups", async () => {
    const host = await render();
    expect(host.textContent).toContain("For caregivers");
    expect(host.textContent).toContain("For communities");
    // Both source sets present.
    expect(host.textContent).toContain("Caregiver Action Network");
    expect(host.textContent).toContain("Pew Research Center");
    // All source entries are external links.
    const links = host.querySelectorAll('main a[href^="https://"]');
    expect(links.length).toBeGreaterThanOrEqual(13);
    for (const a of links) {
      expect(a.getAttribute("target")).toBe("_blank");
      expect(a.getAttribute("rel")).toContain("noopener");
    }
  });

  it("is reachable from the shared footer nav", async () => {
    const host = await render();
    const footer = host.querySelector("footer")!;
    const navLinks = [...footer.querySelectorAll("a")].map((a) =>
      a.getAttribute("href"),
    );
    expect(navLinks).toContain("/sources");
  });
});
