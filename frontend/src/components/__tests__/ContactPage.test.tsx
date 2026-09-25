/**
 * ContactPage — the "Talk to us" destination (/contact).
 *
 * Shared surface for both personas: heading, toll-free phone, and a
 * minimal form (first name, last name, email, phone) that posts to
 * /api/v1/site/contact-inquiry with a mailto fallback.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import ContactPage from "../ContactPage";

let origFetch: typeof fetch;

beforeEach(() => {
  origFetch = window.fetch;
  window.fetch = (async () =>
    ({
      ok: true,
      json: async () => ({ contact_phone: "+1 (877) 409-4144" }),
    }) as Response) as typeof fetch;
});

afterEach(() => {
  window.fetch = origFetch;
});

async function render(onBack = () => {}) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(MemoryRouter, null, createElement(ContactPage, { onBack })),
    );
  });
  return host;
}

function setInput(input: HTMLInputElement, v: string) {
  const setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype,
    "value",
  )!.set!;
  setter.call(input, v);
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

describe("ContactPage — talk-to-us destination", () => {
  it("greets with the invitation and lists the phone", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("We'd love to hear from you");
    expect(text).toContain("+1 (877) 409-4144");
    const tel = host.querySelector('a[href^="tel:"]');
    expect(tel?.getAttribute("href")).toBe("tel:+18774094144");
  });

  it("captures first name, last name, email, and phone", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    for (const label of ["First name", "Last name", "Email", "Phone number"]) {
      expect(text).toContain(label);
    }
  });

  it("is geragogy-calm: no exclamation marks in copy", async () => {
    const host = await render();
    expect(host.textContent ?? "").not.toContain("!");
  });

  it("uses the bid-17 marketing grammar and stays widget-free", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Talk to us");
    const btn = host.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    expect(btn.style.backgroundColor).toMatch(/#c9a24d|201, *162, *77/i);
    // shared surface — no retell widget must mount
    expect(
      host.querySelector('[id*="retell"], script[src*="retell"]'),
    ).toBeNull();
  });

  it("posts the inquiry to the backend and shows thank-you", async () => {
    const host = await render();
    const calls: string[] = [];
    window.fetch = (async (_input: RequestInfo | URL) => {
      calls.push(String(_input));
      return {
        ok: true,
        json: async () => ({ status: "received" }),
      } as Response;
    }) as typeof fetch;

    const inputs = [...host.querySelectorAll("input")].filter(
      (i) => i.name !== "website",
    );
    const values = ["Maya", "Rivera", "maya@example.com", "+1 555 0100"];
    await act(async () => {
      inputs.forEach((input, i) =>
        setInput(input as HTMLInputElement, values[i] ?? ""),
      );
      (
        host.querySelector('button[type="submit"]') as HTMLButtonElement
      ).click();
    });

    expect(calls.some((u) => u.includes("/api/v1/site/contact-inquiry"))).toBe(
      true,
    );
    expect(host.textContent ?? "").toContain("Thank you");
  });
});
