/**
 * Marketing scroll-depth telemetry (WS-D).
 *
 * Emits `marketing.scroll_depth` milestone events at 25% / 50% / 90%
 * page depth — once per threshold per pageview — for /caregiver and
 * /for-communities so wayfinding changes can be judged against OUR
 * baseline rather than industry figures.
 *
 * Follows the E72-B1 contract: coarse milestones only, never
 * continuous motion; client-side dedup via shouldEmit; fire-and-
 * forget with silent failure — telemetry must never break a page.
 */

import { shouldEmit } from "./telemetryContract";
import { API_BASE_URL } from "./env";

export type MarketingPage = "caregiver" | "for-communities";

const DEPTHS = [25, 50, 90] as const;

/**
 * Attach scroll-depth tracking for a marketing page.
 * Returns a cleanup function that removes the listener.
 */
export function trackScrollDepth(page: MarketingPage): () => void {
  const fired = new Set<number>();

  const check = () => {
    const doc = document.documentElement;
    const scrollable = doc.scrollHeight - window.innerHeight;
    // If the page fits the viewport the visitor can see all of it —
    // report full depth honestly rather than nothing.
    const pct =
      scrollable <= 0 ? 100 : Math.round((window.scrollY / scrollable) * 100);

    for (const depth of DEPTHS) {
      if (pct >= depth && !fired.has(depth)) {
        fired.add(depth);
        emit(page, depth);
      }
    }
  };

  window.addEventListener("scroll", check, { passive: true });
  check();
  return () => window.removeEventListener("scroll", check);
}

function emit(page: MarketingPage, depth: number): void {
  // Dedup key covers StrictMode double-mounts and repeated fires.
  if (!shouldEmit("marketing.scroll_depth", `${page}:${depth}`)) return;

  fetch(`${API_BASE_URL}/api/v1/telemetry/marketing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event: "marketing.scroll_depth",
      timestamp: Date.now(),
      metadata: {
        page,
        depth,
        viewport: window.innerWidth < 768 ? "mobile" : "desktop",
      },
    }),
  }).catch(() => {
    // Silently fail — telemetry must never disrupt the user.
  });
}
