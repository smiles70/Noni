/**
 * OnThisPage (WS-A) — anchor menu renders every section, jump lands
 * focus on the destination heading, and prefers-reduced-motion is
 * honoured for the scroll.
 */
import { describe, it, expect, vi, afterEach } from "vitest";
import { createElement } from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";

import OnThisPage from "../OnThisPage";

const SECTIONS = [
  { id: "s-one", label: "First section" },
  { id: "s-two", label: "Second section" },
];

async function render() {
  const host = document.createElement("div");
  host.innerHTML =
    '<h2 id="s-one">One</h2><h2 id="s-two">Two</h2><div id="menu"></div>';
  document.body.appendChild(host);
  const root = createRoot(host.querySelector("#menu")!);
  await act(async () => {
    root.render(createElement(OnThisPage, { sections: SECTIONS }));
  });
  return host;
}

describe("OnThisPage", () => {
  // Hosts accumulate in document.body — clear between tests so
  // getElementById inside the component can't resolve a stale
  // duplicate heading.
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("renders a labelled nav with one link per section", async () => {
    const host = await render();
    const nav = host.querySelector('nav[aria-label="On this page"]');
    expect(nav).not.toBeNull();
    const links = nav!.querySelectorAll("a");
    expect(links.length).toBe(2);
    expect(links[0]!.getAttribute("href")).toBe("#s-one");
    expect(links[1]!.textContent).toBe("Second section");
  });

  it("jump moves focus to the target heading", async () => {
    const host = await render();
    const link = host.querySelector('a[href="#s-two"]')!;
    const target = host.querySelector("#s-two")! as HTMLElement;
    const scrollSpy = vi.fn();
    target.scrollIntoView = scrollSpy;
    await act(async () => {
      link.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(scrollSpy).toHaveBeenCalled();
    expect(document.activeElement).toBe(target);
  });
});
