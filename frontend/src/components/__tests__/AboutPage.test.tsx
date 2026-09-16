/**
 * AboutPage — public "About us" surface (footer nav target).
 *
 * Verifies the page renders the mission statement, the three
 * beliefs, and links to the learner, gift, partner, and help
 * surfaces. Geragogy contract: calm copy, no exclamation marks.
 */

import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import AboutPage from "../AboutPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(AboutPage, { onBack: vi.fn() }),
      ),
    );
  });
  return host;
}

describe("AboutPage — about surface", () => {
  it("renders the mission and why-mynaani copy", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("About mynaani");
    expect(text).toContain("geragogy");
    expect(text).toContain("at their own pace");
  });

  it("links to the learner, gift, partner, and help surfaces", async () => {
    const host = await render();
    const hrefs = [...host.querySelectorAll("a")].map((a) =>
      a.getAttribute("href"),
    );
    expect(hrefs).toContain("/");
    expect(hrefs).toContain("/gift");
    expect(hrefs).toContain("/for-communities");
    expect(hrefs).toContain("/help");
  });

  it("is geragogy-calm: no exclamation marks", async () => {
    const host = await render();
    expect(host.textContent ?? "").not.toContain("!");
  });
});
