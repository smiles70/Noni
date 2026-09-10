/**
 * PageTypes component render tests.
 *
 * Rack 3.5 of TEST-MATURITY-004: exercises the JSX sub-renderers to close
 * the branch-coverage gap left by the proposal-only test file.
 */
import { afterEach, describe, expect, it } from "vitest";
import { act, createElement } from "react";
import { createRoot } from "react-dom/client";
import {
  RecapPage,
  ContextPage,
  PrinciplePage,
  ExamplePage,
  RetrievalPage,
} from "../PageTypes";
import type {
  CurriculumPage,
  ExampleBlock,
  RetrievalBlock,
} from "../../../api/curriculum";

function makePage(overrides: Partial<CurriculumPage> = {}): CurriculumPage {
  return {
    id: "p1",
    title: "Page title",
    content: ["Line one.", "Line two."],
    complexity: 1,
    ...overrides,
  };
}

const example: ExampleBlock = {
  situation: "The user is stuck.",
  claude_says: "Try this.",
  takeaway: "Keep it simple.",
};

const retrieval: RetrievalBlock = {
  prompt: "Pick the safest option.",
  choices: [
    { id: "a", text: "A" },
    { id: "b", text: "B" },
  ],
  correct_id: "a",
  explanation: "Because it is reversible.",
};

async function render(element: React.ReactElement) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  await act(async () => {
    root.render(element);
  });
  return { host, root };
}

describe("PageTypes renderers", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("RecapPage renders title and content", async () => {
    const { host } = await render(
      createElement(RecapPage, { page: makePage({ page_type: "recap" }) }),
    );
    expect(host.textContent).toContain("Page title");
    expect(host.textContent).toContain("Line one");
    expect(host.querySelector('[data-page-type="recap"]')).toBeTruthy();
  });

  it("ContextPage renders title and content", async () => {
    const { host } = await render(
      createElement(ContextPage, { page: makePage({ page_type: "context" }) }),
    );
    expect(host.textContent).toContain("Page title");
    expect(host.querySelector('[data-page-type="context"]')).toBeTruthy();
  });

  it("PrinciplePage renders principle card when principle is present", async () => {
    const { host } = await render(
      createElement(PrinciplePage, {
        page: makePage({
          page_type: "principle",
          principle: "Claude offers words.",
        }),
      }),
    );
    expect(host.textContent).toContain("The rule:");
    expect(host.textContent).toContain("Claude offers words.");
    expect(host.querySelector('[data-component="Card"]')).toBeTruthy();
  });

  it("PrinciplePage omits card when principle is absent", async () => {
    const { host } = await render(
      createElement(PrinciplePage, {
        page: makePage({ page_type: "principle" }),
      }),
    );
    expect(host.textContent).not.toContain("The rule:");
    expect(host.querySelector('[data-component="Card"]')).toBeFalsy();
  });

  it("ExamplePage renders the example card with all sections", async () => {
    const { host } = await render(
      createElement(ExamplePage, {
        page: makePage({ page_type: "example" }),
        example,
      }),
    );
    expect(host.textContent).toContain("The situation:");
    expect(host.textContent).toContain("What Claude might write:");
    expect(host.textContent).toContain("The takeaway:");
    expect(host.textContent).toContain("Keep it simple");
    expect(host.querySelectorAll('[data-component="Divider"]').length).toBe(2);
  });

  it("RetrievalPage renders prompt and omits feedback before an answer", async () => {
    const { host } = await render(
      createElement(RetrievalPage, {
        page: makePage({ page_type: "retrieval" }),
        retrieval,
        answered: null,
      }),
    );
    expect(host.textContent).toContain("Pick the safest option");
    expect(host.querySelector('[role="status"]')).toBeFalsy();
  });

  it("RetrievalPage shows correct feedback after a correct answer", async () => {
    const { host } = await render(
      createElement(RetrievalPage, {
        page: makePage({ page_type: "retrieval" }),
        retrieval,
        answered: "a",
      }),
    );
    expect(host.textContent).toContain("That fits the rule");
    expect(host.textContent).toContain("Because it is reversible");
    expect(
      host.querySelector('[role="status"]')?.getAttribute("aria-label"),
    ).toBe("That fits the rule.");
  });

  it("RetrievalPage shows incorrect feedback after a wrong answer", async () => {
    const { host } = await render(
      createElement(RetrievalPage, {
        page: makePage({ page_type: "retrieval" }),
        retrieval,
        answered: "b",
      }),
    );
    expect(host.textContent).toContain("Take another look");
    expect(host.textContent).toContain("B");
  });

  it("RetrievalPage handles a missing choice id gracefully", async () => {
    const { host } = await render(
      createElement(RetrievalPage, {
        page: makePage({ page_type: "retrieval" }),
        retrieval,
        answered: "not-a-choice",
      }),
    );
    expect(host.querySelector('[role="status"]')).toBeFalsy();
    expect(host.textContent).toContain("Pick the safest option");
  });
});
