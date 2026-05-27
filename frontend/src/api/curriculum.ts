/**
 * Curriculum API client.
 *
 * `loadPaidUnit` knows about the paywall gate (Sprint A10): the backend
 * returns 402 with an envelope_id in the detail body when the caller has
 * no active entitlement. This client surfaces that as a typed result so
 * the renderer can decide between rendering the unit and switching to
 * the paywall view — without inspecting axios errors at the call site.
 *
 * Auth (ADR 0024): uses the centralized `apiClient` so the Bearer token
 * is attached automatically. The per-call `validateStatus` override is
 * passed to apiClient.get so the 402 paywall response doesn't throw.
 */
import { apiClient } from "./client";

// ---- Page-type extension (Curriculum-expansion Phase 1) --------------------
//
// The backend's `CurriculumPage` (backend/models/curriculum.py) now carries
// an optional `page_type` plus one of three optional structured blocks
// (principle / example / retrieval). These types mirror that shape; all
// new fields are optional so legacy pages (older units that only set
// id/title/content/complexity) keep deserializing without ceremony.

export type PageType =
  | "recap"
  | "context"
  | "principle"
  | "example"
  | "retrieval";

export interface RetrievalChoice {
  id: string;
  text: string;
}

export interface RetrievalBlock {
  prompt: string;
  choices: RetrievalChoice[];
  correct_id: string;
  explanation: string;
}

export interface ExampleBlock {
  situation: string;
  claude_says: string;
  takeaway: string;
}

export interface CurriculumPage {
  id: string;
  title: string;
  content: string[];
  complexity: number;
  // Optional Phase-1 fields. Legacy responses (which the backend
  // serializes with `exclude_none=True`) simply omit these.
  page_type?: PageType;
  principle?: string;
  example?: ExampleBlock;
  retrieval?: RetrievalBlock;
}

export interface ApprovedUnit {
  /** Module 1's `/units/{id}` endpoint omits this field; loaders
   *  synthesize it from the call's `module` argument so consumers
   *  never have to branch on whether the wire payload included it. */
  module?: number;
  unit_id: string;
  unit_title: string;
  ui_state: CurriculumPage;
  stability: number;
}

export interface PaywallSignal {
  envelope_id: "billing.signin_or_purchase_required" | "billing.purchase_required";
  product_code: string;
}

/** Thrown by paid loaders when the backend returns 402. The renderer
 *  core catches this and routes to the paywall view instead of the
 *  generic error banner. */
export class PaywallError extends Error {
  constructor(public readonly signal: PaywallSignal) {
    super("Payment required.");
    this.name = "PaywallError";
  }
}

export type LoadUnitResult =
  | { kind: "ok"; unit: ApprovedUnit }
  | { kind: "paywall"; signal: PaywallSignal }
  | { kind: "error"; message: string };

export async function loadPaidUnit(
  module: 4 | 5,
  unitId: string,
): Promise<LoadUnitResult> {
  try {
    const res = await apiClient.get(
      `/api/curriculum/module-${module}/units/${unitId}`,
      {
        // Don't throw on 402 — the paywall signal is a successful
        // negotiation, not an error. The interceptor still attaches
        // the Bearer header.
        validateStatus: (s) => (s >= 200 && s < 300) || s === 402,
      },
    );
    if (res.status === 402) {
      const detail = (res.data as { detail?: PaywallSignal })?.detail;
      if (
        detail &&
        (detail.envelope_id === "billing.signin_or_purchase_required" ||
          detail.envelope_id === "billing.purchase_required") &&
        typeof detail.product_code === "string"
      ) {
        return { kind: "paywall", signal: detail };
      }
      return { kind: "error", message: "Payment required." };
    }
    return { kind: "ok", unit: res.data as ApprovedUnit };
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "Failed to load unit.";
    return { kind: "error", message };
  }
}

/**
 * Load a free-track curriculum unit (modules 1-3). Returns the
 * ApprovedUnit directly; free endpoints never 402.
 *
 * Module 1 uses `/api/curriculum/units/{id}` (the original endpoint).
 * Modules 2-3 use `/api/curriculum/module-{n}/units/{id}`.
 * We synthesize `module` on the way out so callers always see it.
 */
export async function loadFreeUnit(
  module: 0 | 1 | 2 | 3,
  unitId: string,
): Promise<ApprovedUnit> {
  const path =
    module === 1
      ? `/api/curriculum/units/${unitId}`
      : `/api/curriculum/module-${module}/units/${unitId}`;
  const res = await apiClient.get<Omit<ApprovedUnit, "module">>(path);
  return { ...res.data, module };
}

// ---- /lesson loader (Curriculum-expansion Phase 1; extended P3) -----------
//
// `loadFreeLesson` fetches the full ordered page list for a unit. The
// renderer walks these pages locally; ISCS already gated which pages are
// in the response (by complexity ≤ unit.max_complexity), so the frontend
// does no selection — only sequencing.
//
// Sprint "paid modules" P3 widens `LessonResponse.module` from `1|2|3`
// to `1|2|3|4|5` so the same shape can carry paid lessons. The free
// loader keeps a narrowed return type (`LessonResponse & {module:1|2|3}`)
// so existing callers do not see a widened module they cannot handle.
// Paid lessons use `loadPaidLesson` which mirrors `loadPaidUnit`'s
// discriminated 200/402/error result.

export interface LessonResponse {
  module: 0 | 1 | 2 | 3 | 4 | 5;
  unit_id: string;
  unit_title: string;
  pages: CurriculumPage[];
  stability: number;
}

/** Result discriminator for paid lesson loads. Mirrors `LoadUnitResult`. */
export type LoadLessonResult =
  | { kind: "ok"; lesson: LessonResponse & { module: 4 | 5 } }
  | { kind: "paywall"; signal: PaywallSignal }
  | { kind: "error"; message: string };

export async function loadFreeLesson(
  module: 0 | 1 | 2 | 3,
  unitId: string,
): Promise<LessonResponse & { module: 0 | 1 | 2 | 3 }> {
  const path =
    module === 1
      ? `/api/curriculum/units/${unitId}/lesson`
      : `/api/curriculum/module-${module}/units/${unitId}/lesson`;
  // The backend response includes `module`, but for module 1 it always
  // emits 1; we cast through `unknown` so the call site sees the narrow
  // 1|2|3 type even when the JSON `module` is widened to `number`.
  const res = await apiClient.get<{
    module: number;
    unit_id: string;
    unit_title: string;
    pages: CurriculumPage[];
    stability: number;
  }>(path);
  return { ...res.data, module };
}

/**
 * Load a paid-track lesson (modules 4 or 5; Sprint "paid modules" P3).
 *
 * Like `loadPaidUnit`, this returns a discriminated result so the
 * renderer can route a 402 to the paywall view without throwing. The
 * 402 detail envelope is the same one `loadPaidUnit` already handles.
 */
export async function loadPaidLesson(
  module: 4 | 5,
  unitId: string,
): Promise<LoadLessonResult> {
  try {
    const res = await apiClient.get(
      `/api/curriculum/module-${module}/units/${unitId}/lesson`,
      {
        // Don't throw on 402 — paywall is a successful negotiation,
        // not an error.
        validateStatus: (s) => (s >= 200 && s < 300) || s === 402,
      },
    );
    if (res.status === 402) {
      const detail = (res.data as { detail?: PaywallSignal })?.detail;
      if (
        detail &&
        (detail.envelope_id === "billing.signin_or_purchase_required" ||
          detail.envelope_id === "billing.purchase_required") &&
        typeof detail.product_code === "string"
      ) {
        return { kind: "paywall", signal: detail };
      }
      return { kind: "error", message: "Payment required." };
    }
    const body = res.data as {
      module: number;
      unit_id: string;
      unit_title: string;
      pages: CurriculumPage[];
      stability: number;
    };
    // Narrow `module` to the called value; backend echoes it but the
    // caller is the source of truth on which track this is.
    return {
      kind: "ok",
      lesson: { ...body, module },
    };
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "Failed to load lesson.";
    return { kind: "error", message };
  }
}

// ---- Retrieval-choice telemetry --------------------------------------------

export interface RetrievalChoiceRecord {
  // Widened in Sprint "paid modules" P3 alongside the backend's
  // `RetrievalChoiceBody.module: int = Field(ge=1, le=5)`.
  // Further widened to include 0 when Module 0 (primer) shipped.
  module: 0 | 1 | 2 | 3 | 4 | 5;
  unit_id: string;
  page_id: string;
  chosen_id: string;
  correct: boolean;
}

/**
 * Record a learner's retrieval-page selection. Fire-and-forget: callers
 * should not block UI on this. Network failure is silently swallowed
 * because losing one audit row must not break the learning flow.
 */
export async function recordRetrievalChoice(
  body: RetrievalChoiceRecord,
): Promise<void> {
  try {
    await apiClient.post("/api/curriculum/retrieval-choice", body);
  } catch {
    /* fire-and-forget — telemetry loss is acceptable, blocking the
     *  learner is not. */
  }
}

// ---- Lesson menu (S25.1) ---------------------------------------------------
//
// Single-roundtrip table of contents for the free track. Modules 4+ are
// paid and intentionally absent from the payload; do not infer their
// presence from the menu UI.

export interface MenuUnit {
  id: string;
  title: string;
  description: string;
}

export interface MenuModule {
  id: 0 | 1 | 2 | 3;
  title: string;
  units: MenuUnit[];
}

export interface CurriculumMenu {
  modules: MenuModule[];
  bridge_units: MenuUnit[];
}

export async function loadCurriculumMenu(): Promise<CurriculumMenu> {
  const res = await apiClient.get<CurriculumMenu>("/api/curriculum/menu");
  return res.data;
}
