/**
 * ResponsiveContainer — learner measure cap + marketing full-bleed
 * exemption (PS-BID17-001 / ADR-0030/0034).
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import { ResponsiveContainer } from "../ResponsiveContainer";
import { ViewportProvider } from "../../context/ViewportContext";

async function render(path: string) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries: [path] },
        createElement(
          ViewportProvider,
          null,
          createElement(ResponsiveContainer, null, "content"),
        ),
      ),
    );
  });
  return host.firstElementChild as HTMLElement;
}

describe("ResponsiveContainer — full-bleed exemption", () => {
  it("renders edge-to-edge on the bid-17 marketing routes", async () => {
    for (const path of ["/caregiver", "/for-communities"]) {
      const el = await render(path);
      expect(el.style.maxWidth).toBe("100%");
      expect(el.style.padding).toBe("0px");
      // overflowX guard must remain so bands can't cause page scroll.
      expect(el.style.overflowX).toBe("hidden");
    }
  });

  it("keeps the learner measure cap on all other routes", async () => {
    for (const path of ["/", "/curriculum", "/partners", "/contact"]) {
      const el = await render(path);
      expect(el.style.maxWidth).not.toBe("100%");
      expect(el.style.padding).not.toBe("0px");
    }
  });
});
