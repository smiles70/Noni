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

export interface CurriculumPage {
  id: string;
  title: string;
  content: string[];
  complexity: number;
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
  module: 1 | 2 | 3,
  unitId: string,
): Promise<ApprovedUnit> {
  const path =
    module === 1
      ? `/api/curriculum/units/${unitId}`
      : `/api/curriculum/module-${module}/units/${unitId}`;
  const res = await apiClient.get<Omit<ApprovedUnit, "module">>(path);
  return { ...res.data, module };
}
