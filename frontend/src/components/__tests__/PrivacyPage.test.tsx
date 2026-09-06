/**
 * PrivacyPage — public trust surface (TRUST_PRIVACY_RUBRIC_001 T1).
 *
 * Verifies the plain-language privacy statement renders with the four
 * required claims: minimal collection ("that is the whole list"), the
 * never-collect list, the org-visibility boundary, and the deletion path.
 * Geragogy contract: calm copy, no urgency — tested via absence of
 * exclamation marks in body text.
 */

import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";

import PrivacyPage from "../PrivacyPage";

async function render() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        null,
        createElement(PrivacyPage, { onBack: vi.fn() }),
      ),
    );
  });
  return host;
}

describe("PrivacyPage — trust surface", () => {
  it("states what we keep and that the list is complete", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("Your privacy on mynaani");
    expect(text).toContain("email address");
    expect(text).toContain("That is the whole list");
  });

  it("states what we never collect, including card details", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("What we never collect");
    expect(text).toContain("card or bank details");
    expect(text).toContain("location");
  });

  it("states the org-visibility boundary and the deletion path", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).toContain("cannot see your lessons");
    expect(text).toContain("delete your account");
    expect(text).toContain("hello@mynaani.com");
  });

  it("is geragogy-calm: no exclamation marks, no urgency language", async () => {
    const host = await render();
    const text = host.textContent ?? "";
    expect(text).not.toContain("!");
    for (const banned of ["act now", "limited time", "hurry", "don't miss"]) {
      expect(text.toLowerCase()).not.toContain(banned);
    }
  });
});
