/**
 * HowItWorksDialog modal contract tests.
 *
 * Rack 3.4 of TEST-MATURITY-004: exercises the landing-page modal,
 * focus, close interactions, and B2B community entry link.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, createElement } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import HowItWorksDialog from "../HowItWorksDialog";
import type { LandingPageContent } from "../../api/landing";

const mockContent: LandingPageContent = {
  hero: { headline: "", subheadline: "" },
  introduction: {
    title: "Introduction",
    body: "Para one.\n\nPara two.",
  },
  what_mynaani_does: {
    title: "What Mynaani does",
    items: ["Learn", "Practice"],
  },
  how_it_feels: {
    title: "How it feels",
    items: ["Calm", "Clear"],
  },
  trust_and_safety: {
    title: "Trust",
    body: "We protect your data.",
  },
  call_to_action: { primary: { label: "Start" } },
  closing: { body: "Ready when you are." },
};

async function render(
  props: Partial<{
    onClose: () => void;
    onBegin: () => void;
  }> = {},
) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  const onClose = props.onClose ?? vi.fn();
  const onBegin = props.onBegin;

  await act(async () => {
    root.render(
      createElement(
        MemoryRouter,
        { initialEntries: ["/"] },
        createElement(
          Routes,
          null,
          createElement(Route, {
            path: "/",
            element: createElement(HowItWorksDialog, {
              content: mockContent,
              onClose,
              onBegin,
            }),
          }),
          createElement(Route, {
            path: "/for-communities",
            element: createElement("div", null, "B2B page"),
          }),
        ),
      ),
    );
  });

  return { host, root, onClose };
}

describe("HowItWorksDialog", () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout"] });
  });

  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = "";
  });

  it("renders dialog with content sections", async () => {
    const { host } = await render();
    expect(host.textContent).toContain("How Mynaani works");
    expect(host.textContent).toContain("Introduction");
    expect(host.textContent).toContain("Para one");
    expect(host.textContent).toContain("What Mynaani does");
    expect(host.textContent).toContain("Learn");
    expect(host.textContent).toContain("How it feels");
    expect(host.textContent).toContain("Trust");
    expect(host.textContent).toContain("Ready when you are");
  });

  it("closes when the close button is clicked", async () => {
    const { host, onClose } = await render();
    const closeBtn = host.querySelector('[aria-label="Close"]') as HTMLElement;
    expect(closeBtn).toBeDefined();
    await act(async () => closeBtn.click());
    expect(onClose).toHaveBeenCalled();
  });

  it("closes when the Escape key is pressed", async () => {
    const { onClose } = await render();
    await act(async () => {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    });
    expect(onClose).toHaveBeenCalled();
  });

  it("closes when the backdrop is clicked", async () => {
    const { host, onClose } = await render();
    const backdrop = host.querySelector(
      '[data-component="HowItWorksBackdrop"]',
    );
    expect(backdrop).toBeDefined();
    await act(async () => (backdrop as HTMLElement).click());
    expect(onClose).toHaveBeenCalled();
  });

  it("does not close when the panel is clicked", async () => {
    const { host, onClose } = await render();
    const panel = host.querySelector('[role="dialog"]') as HTMLElement;
    await act(async () => panel.click());
    expect(onClose).not.toHaveBeenCalled();
  });

  it("renders Continue CTA when onBegin is provided and calls both callbacks", async () => {
    const onBegin = vi.fn();
    const { host, onClose } = await render({ onBegin });
    const continueBtn = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Continue to my account"),
    );
    expect(continueBtn).toBeDefined();
    await act(async () => continueBtn!.click());
    expect(onBegin).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });

  it("renders Got it CTA when onBegin is omitted", async () => {
    const { host } = await render();
    const gotItBtn = Array.from(host.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Got it"),
    );
    expect(gotItBtn).toBeDefined();
  });

  it("exposes the B2B community entry link", async () => {
    const { host, onClose } = await render();
    const link = Array.from(host.querySelectorAll("a")).find((a) =>
      a.textContent?.includes("For senior living communities"),
    );
    expect(link).toBeDefined();
    expect(link?.getAttribute("href")).toBe("/for-communities");
    expect(link?.getAttribute("data-b2b-entry")).toBe("how-it-works");
    await act(async () => link!.click());
    expect(onClose).toHaveBeenCalled();
  });
});
