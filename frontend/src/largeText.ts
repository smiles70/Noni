/**
 * Larger-text mode. Persists user preference in localStorage.
 * Reads on boot; toggle exposed for the LandingPage button.
 */
const KEY = "noni_large_text";

export function applyLargeTextOnBoot(): void {
  try {
    if (localStorage.getItem(KEY) === "1") {
      document.documentElement.classList.add("large-text");
    }
  } catch {
    /* localStorage unavailable; ignore */
  }
}

export function isLargeText(): boolean {
  return document.documentElement.classList.contains("large-text");
}

export function toggleLargeText(): boolean {
  const next = !isLargeText();
  document.documentElement.classList.toggle("large-text", next);
  try {
    localStorage.setItem(KEY, next ? "1" : "0");
  } catch {
    /* ignore */
  }
  return next;
}
