/**
 * PartnershipInquiryPage — public partner contact form.
 *
 * Verifies the GetSetUp-aligned field set: branded hero, radio group for
 * organization type, labels, calm copy, and the backend POST submit path
 * (mailto fallback preserved for unreachable-endpoint cases).
 */

import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import PartnershipInquiryPage from "../PartnershipInquiryPage";

async function render(onBack = () => {}) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(PartnershipInquiryPage, { onBack }),
      ),
    );
  });
  return host;
}

function setInput(input: HTMLInputElement | HTMLTextAreaElement, v: string) {
  const proto =
    input instanceof HTMLTextAreaElement
      ? window.HTMLTextAreaElement.prototype
      : window.HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, "value")!.set!;
  setter.call(input, v);
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

describe("PartnershipInquiryPage — partner contact form", () => {
  it("renders the heading and required labels", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Partner with mynaani");
    for (const label of [
      "First name",
      "Last name",
      "Work email",
      "Organization",
      "Your role",
      "How can we help?",
    ]) {
      expect(text).toContain(label);
    }
  });

  it("asks organization type with visible radio choices", async () => {
    const host = await render();
    const radios = host.querySelectorAll('input[type="radio"]');
    expect(radios.length).toBe(4);
    const text = host.textContent ?? "";
    expect(text).toContain("What best describes your organization?");
    expect(text).toContain("Senior living community");
    expect(text).toContain("Health plan or insurer");
  });

  it("is geragogy-calm: no exclamation marks in copy", async () => {
    const host = await render();
    expect(host.textContent ?? "").not.toContain("!");
  });

  it("posts the inquiry to the backend and shows thank-you", async () => {
    const host = await render();
    const calls: string[] = [];
    const origFetch = window.fetch;
    window.fetch = (async (_input: RequestInfo | URL) => {
      calls.push(String(_input));
      return {
        ok: true,
        json: async () => ({ status: "received" }),
      } as Response;
    }) as typeof fetch;

    const radios = host.querySelectorAll('input[type="radio"]');
    const textInputs = [...host.querySelectorAll("input")].filter(
      (i) => i.type !== "radio" && i.name !== "website",
    );
    const values = [
      "Maya",
      "Rivera",
      "maya@example.com",
      "Sunrise Senior Living",
      "Director",
      "",
    ];
    await act(async () => {
      textInputs.forEach((input, i) =>
        setInput(input as HTMLInputElement, values[i] ?? ""),
      );
      (radios[0] as HTMLInputElement).click();
      (
        host.querySelector('button[type="submit"]') as HTMLButtonElement
      ).click();
    });

    window.fetch = origFetch;
    expect(calls.some((u) => u.includes("/api/v1/site/partner-inquiry"))).toBe(
      true,
    );
    expect(host.textContent ?? "").toContain("Thank you");
  });
});
