/**
 * PartnershipInquiryPage — public partner contact form.
 *
 * Verifies the GetSetUp-aligned field set, labels, and calm copy; the
 * mailto: interim submit path is documented in the intake.
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

  it("is geragogy-calm: no exclamation marks in copy", async () => {
    const host = await render();
    expect(host.textContent ?? "").not.toContain("!");
  });

  it("shows a thank-you state after submit (mailto interim)", async () => {
    const host = await render();
    // jsdom enforces required-field validation; fill via the native
    // value setter so React's controlled inputs pick the change up.
    const inputs = host.querySelectorAll("input");
    const values = [
      "Maya",
      "Rivera",
      "maya@example.com",
      "",
      "Sunrise Senior Living",
      "Director",
    ];
    await act(async () => {
      inputs.forEach((input, i) => {
        const setter = Object.getOwnPropertyDescriptor(
          window.HTMLInputElement.prototype,
          "value",
        )!.set!;
        setter.call(input, values[i] ?? "");
        input.dispatchEvent(new Event("input", { bubbles: true }));
      });
      (
        host.querySelector('button[type="submit"]') as HTMLButtonElement
      ).click();
    });
    expect(host.textContent ?? "").toContain("Thank you");
    expect(host.textContent ?? "").toContain("partnerships@mynaani.com");
  });
});
