/**
 * Unit tests for `api/curriculum.ts`.
 *
 * `loadPaidUnit` is the bridge between the curriculum view and the
 * Sprint A10 paywall gate. It must distinguish:
 *   - 200 -> { kind: "ok", unit }
 *   - 402 with billing.signin_or_purchase_required -> paywall signal
 *   - 402 with billing.purchase_required           -> paywall signal
 *   - anything else                                -> { kind: "error" }
 *
 * Mis-classifying any of these would either leak paid content to anonymous
 * users or trap signed-in users behind a paywall they can't escape.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));

vi.mock("axios", () => ({
  default: {
    create: () => ({ get: mockGet }),
    isAxiosError: vi.fn(),
  },
}));

import { loadPaidUnit } from "../curriculum";

afterEach(() => {
  mockGet.mockReset();
});

describe("loadPaidUnit", () => {
  it("returns kind=ok with the unit body on 200", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        module: 4,
        unit_id: "module4-unit-1",
        unit_title: "Skills overview",
        ui_state: {
          id: "p1",
          title: "Hello",
          content: ["one"],
          complexity: 1,
        },
        stability: 0.1,
      },
    });

    const res = await loadPaidUnit(4, "module4-unit-1");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-4/units/module4-unit-1",
    );
    expect(res.kind).toBe("ok");
    if (res.kind === "ok") {
      expect(res.unit.module).toBe(4);
      expect(res.unit.ui_state.title).toBe("Hello");
    }
  });

  it("returns kind=paywall on 402 with signin_or_purchase_required envelope", async () => {
    mockGet.mockResolvedValueOnce({
      status: 402,
      data: {
        detail: {
          envelope_id: "billing.signin_or_purchase_required",
          product_code: "modules_4_5",
        },
      },
    });

    const res = await loadPaidUnit(4, "module4-unit-1");

    expect(res.kind).toBe("paywall");
    if (res.kind === "paywall") {
      expect(res.signal.envelope_id).toBe("billing.signin_or_purchase_required");
      expect(res.signal.product_code).toBe("modules_4_5");
    }
  });

  it("returns kind=paywall on 402 with purchase_required envelope", async () => {
    mockGet.mockResolvedValueOnce({
      status: 402,
      data: {
        detail: {
          envelope_id: "billing.purchase_required",
          product_code: "modules_4_5",
        },
      },
    });

    const res = await loadPaidUnit(5, "module5-unit-1");
    expect(res.kind).toBe("paywall");
  });

  it("returns kind=error when 402 lacks a recognized envelope_id (fail closed)", async () => {
    mockGet.mockResolvedValueOnce({
      status: 402,
      data: { detail: { envelope_id: "something.unknown" } },
    });

    const res = await loadPaidUnit(4, "module4-unit-1");
    expect(res.kind).toBe("error");
  });

  it("returns kind=error when the request rejects", async () => {
    mockGet.mockRejectedValueOnce(new Error("network down"));

    const res = await loadPaidUnit(4, "module4-unit-1");
    expect(res.kind).toBe("error");
    if (res.kind === "error") {
      expect(res.message).toMatch(/network down/);
    }
  });
});
