/**
 * PurchaseCancelPage — journey-guard pins (PS-BID17-032).
 *
 * An entitled user must never be routed back to the paywall. The page
 * probes entitlement via loadPaidUnit; when the probe says the user is
 * entitled, the primary CTA routes to /paid-curriculum and the paywall
 * CTA is suppressed. On probe failure the page falls back to the
 * original behavior (free-modules CTA + paywall CTA).
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import PurchaseCancelPage from "../PurchaseCancelPage";

const apiCalls: string[] = [];

beforeEach(() => {
  apiCalls.length = 0;
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.fetch = origFetch;
});

const origFetch = window.fetch;

function stubFetch(status: number) {
  window.fetch = (async (input: RequestInfo | URL) => {
    apiCalls.push(String(input));
    if (status === 402) {
      return new Response(
        JSON.stringify({
          detail: {
            envelope_id: "billing.purchase_required",
            product_code: "modules_4_5",
          },
        }),
        { status: 402, headers: { "Content-Type": "application/json" } },
      );
    }
    return new Response(
      JSON.stringify({ module: 3, unit_id: "module3-unit-1", title: "t" }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }) as typeof fetch;
}

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries: ["/purchase/cancel"] },
        createElement(
          Routes,
          null,
          createElement(Route, {
            path: "/purchase/cancel",
            element: createElement(PurchaseCancelPage),
          }),
        ),
      ),
    );
  });
  return host;
}

describe("PurchaseCancelPage — journey guard", () => {
  it("suppresses the paywall CTA when the user is entitled", async () => {
    stubFetch(200);
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Continue to the paid modules");
    expect(text).not.toContain("Return to paywall");
  });

  it("keeps the paywall CTA when the user is not entitled", async () => {
    stubFetch(402);
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Continue with free modules");
    expect(text).toContain("Return to paywall");
  });
});
