/**
 * PurchaseSuccessPage journey contract.
 *
 * Verifies that the post-purchase primary CTA sends the learner to the
 * correct next track so we do not accidentally drop an entitled learner
 * back onto the free track (which would loop them to the paywall).
 */
import { beforeEach, describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import PurchaseSuccessPage from "../PurchaseSuccessPage";
import { mockCheckoutComplete } from "../../api/billing";

vi.mock("../../api/billing", () => ({
  mockCheckoutComplete: vi.fn(),
}));

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
  beforeEach(() => {
    (mockCheckoutComplete as ReturnType<typeof vi.fn>).mockReset();
  });

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

  it("go-home secondary CTA returns to home", async () => {
    const host = await render(
      "/purchase/success?purchase=test&product=modules_4_5&provider=stripe&is_gift=false",
    );
    const homeBtn = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Go home"),
    );
    expect(homeBtn).toBeDefined();
    await act(async () => homeBtn!.click());
    expect(host.textContent).toContain("Home");
  });
});

describe("PurchaseSuccessPage — mock checkout completion", () => {
  beforeEach(() => {
    (mockCheckoutComplete as ReturnType<typeof vi.fn>).mockReset();
  });

  it("activates access for mock self-purchase", async () => {
    (mockCheckoutComplete as ReturnType<typeof vi.fn>).mockResolvedValue({
      granted: true,
    });
    const host = await render(
      "/purchase/success?purchase=test&product=modules_4_5&provider=mock&is_gift=false",
    );

    await act(async () => {
      await Promise.resolve();
    });

    expect(host.textContent).toContain("activated");
    expect(mockCheckoutComplete).toHaveBeenCalledWith("test");
  });

  it("shows an error when mock completion is not granted", async () => {
    (mockCheckoutComplete as ReturnType<typeof vi.fn>).mockResolvedValue({
      granted: false,
    });
    const host = await render(
      "/purchase/success?purchase=test&product=modules_4_5&provider=mock&is_gift=false",
    );

    await act(async () => {
      await Promise.resolve();
    });

    expect(host.textContent).toContain("We could not activate your access");
  });

  it("shows an error when mock completion fails", async () => {
    (mockCheckoutComplete as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("boom"),
    );
    const host = await render(
      "/purchase/success?purchase=test&product=modules_4_5&provider=mock&is_gift=false",
    );

    await act(async () => {
      await Promise.resolve();
    });

    expect(host.textContent).toContain(
      "Something went wrong while completing the test payment",
    );
  });
});
