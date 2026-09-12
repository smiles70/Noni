/**
 * HelpPage — contact-surface facts (intake 013).
 *
 * Locks the canonical contact facts: help@mynaani.com (never hello@),
 * the toll-free line presented with tel: + AI-answered disclosure, and
 * the 30-day refund window matching the KB source of truth.
 */

import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import HelpPage from "../HelpPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(HelpPage, { onBack: vi.fn() }),
      ),
    );
  });
  return host;
}

describe("HelpPage — contact facts", () => {
  it("uses the canonical help@ address everywhere", async () => {
    const host = await render();
    expect(host.textContent).toContain("help@mynaani.com");
    expect(host.textContent).not.toContain("hello@mynaani.com");
    const bad = host.querySelector('a[href^="mailto:hello@"]');
    expect(bad).toBeNull();
  });

  it("presents the toll-free line with AI disclosure", async () => {
    const host = await render();
    const tel = host.querySelector('a[href="tel:+18774094144"]');
    expect(tel).not.toBeNull();
    expect(tel?.textContent).toContain("1 (877) 409-4144");
    expect(tel?.getAttribute("aria-label")).toContain("toll free");
    expect(host.textContent).toContain("answered by our AI receptionist");
    expect(host.textContent).toContain("call may be stored");
  });

  it("states the 30-day refund window", async () => {
    const host = await render();
    expect(host.textContent).toContain("within 30 days");
    expect(host.textContent).not.toContain("within 14 days");
  });
});
