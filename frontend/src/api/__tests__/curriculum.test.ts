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

const { mockGet, mockUse } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockUse: vi.fn(),
}));

// client.ts (imported transitively) registers a Bearer interceptor
// at module load. The mock must accept the registration call.
vi.mock("axios", () => ({
  default: {
    create: () => ({
      get: mockGet,
      interceptors: { request: { use: mockUse } },
    }),
    isAxiosError: vi.fn(),
  },
  AxiosHeaders: class {},
}));

import { loadFreeUnit, loadPaidUnit } from "../curriculum";

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

    // curriculum.ts passes a per-call validateStatus override so the
    // 402 paywall response doesn't throw. We assert the URL is correct
    // and that *some* config object was passed.
    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-4/units/module4-unit-1",
      expect.objectContaining({ validateStatus: expect.any(Function) }),
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

describe("loadFreeUnit", () => {
  it("hits /api/curriculum/units/{id} for module 1 and synthesizes module=1", async () => {
    // Module 1's endpoint does not include `module` in the payload.
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        unit_id: "unit-2",
        unit_title: "Why AI is different",
        ui_state: {
          id: "p1",
          title: "Hello",
          content: ["one"],
          complexity: 1,
        },
        stability: 0.1,
      },
    });

    const unit = await loadFreeUnit(1, "unit-2");

    expect(mockGet).toHaveBeenCalledWith("/api/curriculum/units/unit-2");
    expect(unit.module).toBe(1);
    expect(unit.unit_id).toBe("unit-2");
    expect(unit.ui_state.title).toBe("Hello");
  });

  it("hits /api/curriculum/module-2/units/{id} for module 2 and preserves module=2", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        module: 2,
        unit_id: "module2-unit-1",
        unit_title: "Patterns over time",
        ui_state: {
          id: "p1",
          title: "T",
          content: [],
          complexity: 1,
        },
        stability: 0.2,
      },
    });

    const unit = await loadFreeUnit(2, "module2-unit-1");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-2/units/module2-unit-1",
    );
    expect(unit.module).toBe(2);
    expect(unit.unit_id).toBe("module2-unit-1");
  });

  it("hits /api/curriculum/module-3/units/{id} for module 3", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        module: 3,
        unit_id: "module3-unit-1",
        unit_title: "Judgment",
        ui_state: { id: "p1", title: "T", content: [], complexity: 1 },
        stability: 0.3,
      },
    });

    const unit = await loadFreeUnit(3, "module3-unit-1");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-3/units/module3-unit-1",
    );
    expect(unit.module).toBe(3);
  });

  it("propagates a rejected request as a thrown error", async () => {
    mockGet.mockRejectedValueOnce(new Error("nope"));
    await expect(loadFreeUnit(1, "unit-2")).rejects.toThrow("nope");
  });
});
