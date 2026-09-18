/**
 * HelpCard unit tests — the "Call me" learner help surface.
 * Renders via createRoot + act (no testing-library — repo convention).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, createElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import HelpCard from "../HelpCard";

describe("HelpCard", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    localStorage.clear();
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    vi.restoreAllMocks();
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
    localStorage.clear();
  });

  function renderCard() {
    act(() => {
      root.render(createElement(HelpCard));
    });
  }

  function button(label: string): HTMLButtonElement | null {
    return (
      Array.from(container.querySelectorAll("button")).find(
        (b) => b.textContent?.trim() === label,
      ) ?? null
    );
  }

  async function submitNumber(value: string) {
    const input = container.querySelector<HTMLInputElement>("#help-phone");
    expect(input).toBeTruthy();
    await act(async () => {
      // React controlled inputs need the native setter + input event.
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        "value",
      )!.set!;
      setter.call(input, value);
      input!.dispatchEvent(new Event("input", { bubbles: true }));
    });
    await act(async () => {
      button("Call me now")!.click();
      await Promise.resolve();
    });
  }

  it("opens with a single Call me action and no field", () => {
    renderCard();
    expect(container.textContent).toMatch(/Get help with this lesson/);
    expect(button("Call me")).toBeTruthy();
    expect(container.querySelector("#help-phone")).toBeNull();
  });

  it("reveals the phone field only after Call me is tapped", async () => {
    renderCard();
    await act(async () => {
      button("Call me")!.click();
    });
    expect(container.querySelector("#help-phone")).toBeTruthy();
    expect(button("Call me now")).toBeTruthy();
  });

  it("confirms the call after submit and saves the number", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({ status: "calling", calling: true }),
      })),
    );
    renderCard();
    await act(async () => {
      button("Call me")!.click();
    });
    await submitNumber("555-123-4567");
    await act(async () => {
      await Promise.resolve();
    });
    expect(container.textContent).toMatch(/we are calling you now/i);
    expect(localStorage.getItem("mynaani_help_phone")).toBe("555-123-4567");
  });

  it("shows the queued state when the call cannot be placed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({ status: "queued", calling: false }),
      })),
    );
    renderCard();
    await act(async () => {
      button("Call me")!.click();
    });
    await submitNumber("555-123-4567");
    await act(async () => {
      await Promise.resolve();
    });
    expect(container.textContent).toMatch(/our team has your request/i);
  });
});
