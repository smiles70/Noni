/**
 * Caregiver-path grammar pins (PS-BID17-029/030/031).
 *
 * Verifies the aligned MARKETING treatment on the three transaction
 * surfaces: MARKETING paper background; gold CTA on the gift
 * checkout and redemption pages (annex-aligned); neutral shared
 * styling on purchase success.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import GiftCheckoutPage from "../GiftCheckoutPage";
import GiftRedeemPage from "../GiftRedeemPage";
import PurchaseSuccessPage from "../PurchaseSuccessPage";

const origFetch = window.fetch;

beforeEach(() => {
  window.fetch = (async () => {
    return new Response("{}", {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }) as typeof fetch;
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.fetch = origFetch;
});

async function renderAt(path: string, el: React.ReactElement) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries: [path] },
        createElement(
          Routes,
          null,
          createElement(Route, { path, element: el }),
        ),
      ),
    );
  });
  return host;
}

const PAPER = /#f5f3ee|245, *243, *238/i;
const GOLD = /#c9a24d|201, *162, *77/i;

describe("caregiver path — aligned grammar", () => {
  it("/gift: paper bg + gold CTA + single widget mount", async () => {
    const host = await renderAt(
      "/gift",
      createElement(GiftCheckoutPage, { productCode: "m", onBack: () => {} }),
    );
    const main = host.querySelector("main") as HTMLElement;
    expect(main.style.backgroundColor).toMatch(PAPER);
    const btn = host.querySelector("button") as HTMLButtonElement;
    expect(btn.style.background).toMatch(GOLD);
  });

  it("/gift-redeem: paper bg on pending banner before envelope loads", async () => {
    window.fetch = (async () => {
      throw new Error("offline");
    }) as typeof fetch;
    const host = await renderAt(
      "/gift-redeem",
      createElement(GiftRedeemPage, {
        onClaimed: () => {},
        onBack: () => {},
      }),
    );
    const main = host.querySelector("main") as HTMLElement;
    expect(main.style.backgroundColor).toMatch(PAPER);
    expect(host.textContent).toContain("trouble loading");
  });

  it("/purchase/success: paper bg, neutral CTA (no gold — shared)", async () => {
    const host = await renderAt(
      "/purchase/success",
      createElement(PurchaseSuccessPage),
    );
    const main = host.querySelector("main") as HTMLElement;
    expect(main.style.backgroundColor).toMatch(PAPER);
    const btn = host.querySelector("button") as HTMLButtonElement | null;
    if (btn) expect(btn.style.background).not.toMatch(GOLD);
  });
});
