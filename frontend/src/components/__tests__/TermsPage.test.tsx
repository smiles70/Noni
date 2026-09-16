/**
 * TermsPage — public legal surface (MKT-FOOTER-001 / legal row target).
 *
 * Verifies the plain-language terms render with the clauses that matter
 * for mynaani's actual product: one-time (non-subscription) purchase,
 * the 30-day refund window, gift-token rules, and governing law.
 * Geragogy contract: calm copy — no exclamation marks in body text.
 */

import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import TermsPage from "../TermsPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(TermsPage, { onBack: vi.fn() }),
      ),
    );
  });
  return host;
}

describe("TermsPage — plain-language terms", () => {
  it("renders the heading and last-updated notice", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Terms of Service");
    expect(text).toContain("last updated");
  });

  it("states purchase is one-time, not a subscription", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("one-time purchase");
    expect(text).toContain("not a subscription");
    expect(text).toContain("Stripe");
  });

  it("states the 30-day refund window and gift rule", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("30 days");
    expect(text).toContain("refund goes to the person who paid");
  });

  it("states eligibility, acceptable use, and governing law", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("18 years old");
    expect(text).toContain("Delaware");
    expect(text).toContain("do not share");
  });

  it("is geragogy-calm: no exclamation marks", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).not.toContain("!");
  });
});
