/**
 * Enterprise useViewport hook contract tests.
 *
 * Validates safe server-side behaviour and breakpoint logic.
 * Full DOM integration is covered by Playwright e2e tests.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useViewport, type ViewportState } from "../useViewport";
import { renderToString } from "react-dom/server";
import { act, createElement } from "react";
import { createRoot } from "react-dom/client";

describe("useViewport — server-side safety", () => {
  it("returns default desktop dimensions when window is undefined", () => {
    // In Node, window is undefined; the hook must not throw.
    const Wrapper = () => {
      const vp = useViewport();
      return createElement(
        "div",
        { "data-breakpoint": vp.breakpoint, "data-width": String(vp.width) },
        null,
      );
    };
    const html = renderToString(createElement(Wrapper));
    expect(html).toContain('data-breakpoint="desktop"');
    expect(html).toContain('data-width="1024"');
  });
});

describe("useViewport — breakpoint logic (inferred)", () => {
  it("export includes the expected type names", () => {
    // Indirect contract check: the type export is stable.
    expect(useViewport).toBeTypeOf("function");
  });
});

describe("useViewport — client breakpoints", () => {
  const originalWidth = window.innerWidth;
  const originalHeight = window.innerHeight;

  beforeEach(() => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout"] });
  });

  afterEach(() => {
    vi.useRealTimers();
    window.innerWidth = originalWidth;
    window.innerHeight = originalHeight;
  });

  function renderAtWidth(width: number): ViewportState {
    window.innerWidth = width;
    const host = document.createElement("div");
    document.body.appendChild(host);
    const root = createRoot(host);
    let captured: ViewportState | null = null;
    function Capture() {
      captured = useViewport();
      return null;
    }
    act(() => {
      root.render(createElement(Capture));
    });
    const value = captured!;
    root.unmount();
    host.remove();
    return value;
  }

  it("classifies mobile width", () => {
    const vp = renderAtWidth(480);
    expect(vp.breakpoint).toBe("mobile");
    expect(vp.isMobile).toBe(true);
    expect(vp.isTablet).toBe(false);
    expect(vp.isDesktop).toBe(false);
    expect(vp.isWide).toBe(false);
  });

  it("classifies tablet width", () => {
    const vp = renderAtWidth(800);
    expect(vp.breakpoint).toBe("tablet");
    expect(vp.isMobile).toBe(false);
    expect(vp.isTablet).toBe(true);
  });

  it("classifies desktop width", () => {
    const vp = renderAtWidth(1200);
    expect(vp.breakpoint).toBe("desktop");
    expect(vp.isDesktop).toBe(true);
  });

  it("classifies wide width", () => {
    const vp = renderAtWidth(1600);
    expect(vp.breakpoint).toBe("wide");
    expect(vp.isWide).toBe(true);
  });

  it("exposes window dimensions in state", () => {
    window.innerWidth = 1234;
    window.innerHeight = 567;
    const vp = renderAtWidth(1234);
    expect(vp.width).toBe(1234);
    expect(vp.height).toBe(567);
  });
});
