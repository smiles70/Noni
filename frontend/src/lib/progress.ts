/**
 * Last-visited curriculum position, persisted to localStorage so a learner
 * can close the tab and resume on next sign-in without a backend round-trip.
 *
 * Per-browser only (no cross-device sync). When per-account progress ships
 * server-side, this becomes the offline / pre-hydration fallback.
 *
 * All access is wrapped in try/catch because Safari Private mode, quota
 * exhaustion, and corrupted JSON would otherwise throw and brick the
 * curriculum view on mount.
 */

const KEY = "noni_progress_v1";

export interface Progress {
  module: 1 | 2 | 3 | 4 | 5;
  unitId: string;
}

export function readProgress(): Progress | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<Progress>;
    if (
      typeof parsed.unitId === "string" &&
      parsed.unitId.length > 0 &&
      typeof parsed.module === "number" &&
      parsed.module >= 1 &&
      parsed.module <= 5
    ) {
      return {
        module: parsed.module as Progress["module"],
        unitId: parsed.unitId,
      };
    }
    return null;
  } catch {
    return null;
  }
}

export function writeProgress(p: Progress): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(p));
  } catch {
    /* quota / disabled storage — intentionally swallowed */
  }
}
