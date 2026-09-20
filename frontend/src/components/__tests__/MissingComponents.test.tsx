/**
 * Backfill tests for small, previously-untested components.
 *
 * Rack 3.1 of TEST-MATURITY-004: raises coverage and regression protection
 * for simple state/rendering components before tackling larger pages.
 */
import { describe, it, expect, vi } from "vitest";
import { Component, type ReactNode, createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Routes, Route } from "react-router-dom";

import PurchaseCancelPage from "../PurchaseCancelPage";
import EmptyState from "../EmptyState";
import LoadingSkeleton from "../LoadingSkeleton";
import { ErrorBoundary } from "../ErrorBoundary";

async function renderWithRouter(
  element: ReactNode,
  initialEntries: string[] = ["/"],
  routePath = "/",
) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries },
        createElement(
          Routes,
          null,
          createElement(Route, { path: routePath, element: element }),
          createElement(Route, {
            path: "/curriculum",
            element: createElement("div", null, "Free curriculum"),
          }),
          createElement(Route, {
            path: "/paywall",
            element: createElement("div", null, "Paywall"),
          }),
          createElement(Route, {
            path: "/",
            element: createElement("div", null, "Home"),
          }),
        ),
      ),
    );
  });
  return { host, root };
}

describe("PurchaseCancelPage — abandoned-checkout routing", () => {
  it("offers the free modules path", async () => {
    const { host } = await renderWithRouter(
      createElement(PurchaseCancelPage),
      ["/purchase/cancel"],
      "/purchase/cancel",
    );
    expect(host.textContent).toContain("Payment not completed");
    const freeBtn = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Continue with free modules"),
    );
    expect(freeBtn).toBeDefined();
    await act(async () => freeBtn!.click());
    expect(host.textContent).toContain("Free curriculum");
  });

  it("offers the return-to-paywall path", async () => {
    const { host } = await renderWithRouter(
      createElement(PurchaseCancelPage),
      ["/purchase/cancel"],
      "/purchase/cancel",
    );
    const paywallBtn = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Return to paywall"),
    );
    expect(paywallBtn).toBeDefined();
    await act(async () => paywallBtn!.click());
    expect(host.textContent).toContain("Paywall");
  });
});

describe("EmptyState", () => {
  it("renders title and optional description", async () => {
    const { host } = await renderWithRouter(
      createElement(EmptyState, {
        title: "No data",
        description: "Nothing here yet.",
      }),
    );
    expect(host.textContent).toContain("No data");
    expect(host.textContent).toContain("Nothing here yet.");
  });

  it("renders action button when callback provided", async () => {
    const action = vi.fn();
    const { host } = await renderWithRouter(
      createElement(EmptyState, {
        title: "Try again",
        actionLabel: "Retry",
        onAction: action,
      }),
    );
    const button = host.querySelector("button");
    expect(button).not.toBeNull();
    expect(button!.textContent).toBe("Retry");
    await act(async () => button!.click());
    expect(action).toHaveBeenCalledTimes(1);
  });
});

describe("LoadingSkeleton", () => {
  it("renders polite loading announcement", async () => {
    const { host } = await renderWithRouter(createElement(LoadingSkeleton));
    expect(host.textContent).toContain("One moment — loading.");
    expect(host.querySelector('[aria-busy="true"]')).not.toBeNull();
  });
});

class Thrower extends Component<{ throwNow: boolean }> {
  render() {
    if (this.props.throwNow) {
      throw new Error("boom");
    }
    return createElement("div", null, "OK");
  }
}

describe("ErrorBoundary", () => {
  it("renders children when no error occurs", async () => {
    const { host } = await renderWithRouter(
      createElement(ErrorBoundary, {
        children: createElement("div", null, "child content"),
      }),
    );
    expect(host.textContent).toContain("child content");
  });

  it("catches render errors and shows fallback", async () => {
    const consoleError = vi
      .spyOn(console, "error")
      .mockImplementation(() => undefined);
    const { host } = await renderWithRouter(
      createElement(ErrorBoundary, {
        children: createElement(Thrower, { throwNow: true }),
      }),
    );
    expect(host.textContent).toContain("Something went wrong");
    consoleError.mockRestore();
  });
});
