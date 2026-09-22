/**
 * PartnerPage — hosted partner doorway (/c/:slug).
 *
 * Pins the aligned-doorway grammar (PS-BID17-020 residual): MARKETING
 * paper page + paperCard panel + gold CTA, while keeping the page a
 * calm branded doorway — no hero band, facility ChatWidget mounted,
 * access-code path intact.
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import PartnerPage from "../PartnerPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries: ["/c/pines"] },
        createElement(
          Routes,
          null,
          createElement(Route, {
            path: "/c/:slug",
            element: createElement(PartnerPage),
          }),
        ),
      ),
    );
  });
  return host;
}

describe("PartnerPage — hosted doorway", () => {
  it("keeps the access-code doorway content", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("access code");
    expect(text).toContain("sign me in");
  });

  it("uses the aligned-doorway grammar (paper bg + gold CTA)", async () => {
    const host = await render();
    const main = host.querySelector("main") as HTMLElement;
    expect(main.style.backgroundColor).toMatch(/#f5f3ee|245, *243, *238/i);
    const btn = host.querySelector("button") as HTMLButtonElement;
    expect(btn.style.background).toMatch(/#c9a24d|201, *162, *77/i);
  });
});
