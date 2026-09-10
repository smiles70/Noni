/**
 * PurchaseSuccessPage journey contract.
 *
 * Verifies that the post-purchase primary CTA sends the learner to the
 * correct next track so we do not accidentally drop an entitled learner
 * back onto the free track (which would loop them to the paywall).
 */
import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import PurchaseSuccessPage from "../PurchaseSuccessPage";

async function render(initialPath: string) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries: [initialPath] },
        createElement(
          Routes,
          null,
          createElement(Route, {
            path: "/purchase/success",
            element: createElement(PurchaseSuccessPage),
          }),
          createElement(Route, {
            path: "/paid-curriculum",
            element: createElement("div", null, "Paid curriculum"),
          }),
          createElement(Route, {
            path: "/",
            element: createElement("div", null, "Home"),
          }),
        ),
      ),
    );
  });
  return host;
}

describe("PurchaseSuccessPage — post-purchase routing", () => {
  it("self-purchase CTA goes to /paid-curriculum", async () => {
    const host = await render(
      "/purchase/success?purchase=test&product=modules_4_5&provider=stripe&is_gift=false",
    );
    const primary = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Continue to the paid modules"),
    );
    expect(primary).toBeDefined();
    await act(async () => primary!.click());
    expect(host.textContent).toContain("Paid curriculum");
  });

  it("gift purchase CTA returns to home", async () => {
    const host = await render(
      "/purchase/success?purchase=test&product=modules_4_5&provider=stripe&is_gift=true",
    );
    const primary = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Return to home"),
    );
    expect(primary).toBeDefined();
    await act(async () => primary!.click());
    expect(host.textContent).toContain("Home");
  });
});
