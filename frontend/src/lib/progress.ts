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
  /** Page index within the current unit's lesson (0-based).
   *
   *  Added in Curriculum-expansion Phase 1: lessons are now multi-page
   *  decks, so resume position must include the page offset within the
   *  unit. Older stored progress objects (v1 schema before this field)
   *  read as `pageIdx: 0`, which is the safe default — they re-start
   *  the unit from its first page on the next visit. */
  pageIdx?: number;
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
      const pageIdx =
        typeof parsed.pageIdx === "number" &&
        Number.isFinite(parsed.pageIdx) &&
        parsed.pageIdx >= 0
          ? Math.floor(parsed.pageIdx)
          : 0;
      return {
        module: parsed.module as Progress["module"],
        unitId: parsed.unitId,
        pageIdx,
      };
    }
    return null;
  } catch {
    return null;
  }
}

export function writeProgress(p: Progress): void {
  try {
    const payload: Progress = {
      module: p.module,
      unitId: p.unitId,
      pageIdx: typeof p.pageIdx === "number" ? p.pageIdx : 0,
    };
    localStorage.setItem(KEY, JSON.stringify(payload));
  } catch {
    /* quota / disabled storage — intentionally swallowed */
  }
}
