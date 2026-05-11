/**
 * Curriculum API client.
 *
 * `loadPaidUnit` knows about the paywall gate (Sprint A10): the backend
 * returns 402 with an envelope_id in the detail body when the caller has
 * no active entitlement. This client surfaces that as a typed result so
 * the renderer can decide between rendering the unit and switching to
 * the paywall view — without inspecting axios errors at the call site.
 */
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export interface CurriculumPage {
  id: string;
  title: string;
  content: string[];
  complexity: number;
}

export interface ApprovedUnit {
  module: number;
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

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  // Don't throw on 402; we want to inspect it.
  validateStatus: (status) => (status >= 200 && status < 300) || status === 402,
});

export async function loadPaidUnit(
  module: 4 | 5,
  unitId: string,
): Promise<LoadUnitResult> {
  try {
    const res = await client.get(`/api/curriculum/module-${module}/units/${unitId}`);
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
