/**
 * AuthPendingBanner unit tests.
 *
 * Validates countdown, auto-retry, max-retry exhaustion, and
 * sessionStorage persistence across remounts.
 *
 * Uses createRoot + container.textContent (project pattern) instead
 * of @testing-library/react.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { act } from "react";
import AuthPendingBanner from "../AuthPendingBanner";

const RETRY_STORAGE_KEY = "noni.auth_banner_retries";

describe("AuthPendingBanner", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    vi.useFakeTimers();
    sessionStorage.clear();
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    vi.useRealTimers();
    act(() => root.unmount());
    container.remove();
    sessionStorage.clear();
  });

  function renderBanner(props: { onRetry?: () => void }) {
    act(() => {
      root.render(createElement(AuthPendingBanner, props));
    });
  }

  function getText() {
    return container.textContent ?? "";
  }

  it("shows countdown with Try now button", () => {
    renderBanner({ onRetry: () => {} });
    expect(getText()).toMatch(/retrying in 15s/);
    expect(getText()).toMatch(/Try now/);
  });

  it("calls onRetry after countdown reaches zero", () => {
    const onRetry = vi.fn();
    renderBanner({ onRetry });

    act(() => {
      vi.advanceTimersByTime(15000);
    });

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("increments retry count in sessionStorage on auto-retry", () => {
    const onRetry = vi.fn();
    renderBanner({ onRetry });

    act(() => {
      vi.advanceTimersByTime(15000);
    });

    expect(sessionStorage.getItem(RETRY_STORAGE_KEY)).toBe("1");
  });

  it("shows 'Please refresh' after 3 auto-retries", () => {
    const onRetry = vi.fn();
    sessionStorage.setItem(RETRY_STORAGE_KEY, "3");

    renderBanner({ onRetry });

    expect(getText()).toMatch(/Still having trouble connecting/);
    expect(getText()).not.toMatch(/Try now/);
  });

  it("does not auto-retry when exhausted", () => {
    const onRetry = vi.fn();
    sessionStorage.setItem(RETRY_STORAGE_KEY, "3");

    renderBanner({ onRetry });

    act(() => {
      vi.advanceTimersByTime(30000);
    });

    expect(onRetry).not.toHaveBeenCalled();
  });

  it("counts down from 15 to 0 in 1-second steps", () => {
    renderBanner({ onRetry: () => {} });

    expect(getText()).toMatch(/retrying in 15s/);

    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(getText()).toMatch(/retrying in 10s/);

    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(getText()).toMatch(/retrying in 5s/);
  });

  it("clears interval on unmount to prevent leaks", () => {
    const onRetry = vi.fn();
    renderBanner({ onRetry });

    act(() => root.unmount());

    act(() => {
      vi.advanceTimersByTime(30000);
    });

    expect(onRetry).not.toHaveBeenCalled();
  });
});
