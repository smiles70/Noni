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

const { mockGet, mockPost, mockUse } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockUse: vi.fn(),
}));

// client.ts (imported transitively) registers a Bearer interceptor
// at module load. The mock must accept the registration call.
vi.mock("axios", () => ({
  default: {
    create: () => ({
      get: mockGet,
      post: mockPost,
      interceptors: { request: { use: mockUse } },
    }),
    isAxiosError: vi.fn(),
  },
  AxiosHeaders: class {},
}));

import {
  loadCurriculumMenu,
  loadFreeLesson,
  loadFreeUnit,
  loadPaidLesson,
  loadPaidUnit,
  recordRetrievalChoice,
} from "../curriculum";

afterEach(() => {
  mockGet.mockReset();
  mockPost.mockReset();
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

// ---- /lesson loader (Curriculum-expansion Phase 1) -------------------------

describe("loadFreeLesson", () => {
  it("hits /api/curriculum/units/{id}/lesson for module 1 and synthesizes module=1", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        module: 1,
        unit_id: "unit-2",
        unit_title: "What Is Claude",
        pages: [
          {
            id: "u2-context",
            title: "Context",
            content: ["a"],
            complexity: 1,
            page_type: "context",
          },
          {
            id: "u2-principle",
            title: "Principle",
            content: [],
            complexity: 1,
            page_type: "principle",
            principle: "x",
          },
        ],
        stability: 0.1,
      },
    });

    const lesson = await loadFreeLesson(1, "unit-2");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/units/unit-2/lesson",
    );
    expect(lesson.module).toBe(1);
    expect(lesson.unit_id).toBe("unit-2");
    expect(lesson.pages).toHaveLength(2);
    expect(lesson.pages[0].page_type).toBe("context");
  });

  it("hits the module-2 path for module 2", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        module: 2,
        unit_id: "module2-unit-1",
        unit_title: "T",
        pages: [
          { id: "p", title: "T", content: [], complexity: 1 },
        ],
        stability: 0.2,
      },
    });

    const lesson = await loadFreeLesson(2, "module2-unit-1");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-2/units/module2-unit-1/lesson",
    );
    expect(lesson.module).toBe(2);
  });

  it("preserves pages with retrieval/example structured blocks", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        module: 1,
        unit_id: "unit-2",
        unit_title: "U2",
        pages: [
          {
            id: "u2-retrieval",
            title: "Pick one",
            content: ["read both"],
            complexity: 1,
            page_type: "retrieval",
            retrieval: {
              prompt: "Which?",
              choices: [
                { id: "a", text: "A" },
                { id: "b", text: "B" },
              ],
              correct_id: "a",
              explanation: "because",
            },
          },
        ],
        stability: 0,
      },
    });

    const lesson = await loadFreeLesson(1, "unit-2");
    expect(lesson.pages[0].retrieval?.choices).toHaveLength(2);
    expect(lesson.pages[0].retrieval?.correct_id).toBe("a");
  });
});

// ---- recordRetrievalChoice -------------------------------------------------

describe("recordRetrievalChoice", () => {
  it("POSTs the body to /api/curriculum/retrieval-choice", async () => {
    mockPost.mockResolvedValueOnce({ status: 200, data: { recorded: true } });

    await recordRetrievalChoice({
      module: 1,
      unit_id: "unit-2",
      page_id: "u2-retrieval",
      chosen_id: "a",
      correct: true,
    });

    expect(mockPost).toHaveBeenCalledWith(
      "/api/curriculum/retrieval-choice",
      {
        module: 1,
        unit_id: "unit-2",
        page_id: "u2-retrieval",
        chosen_id: "a",
        correct: true,
      },
    );
  });

  it("swallows network failures (fire-and-forget)", async () => {
    mockPost.mockRejectedValueOnce(new Error("offline"));

    // Must not throw — losing telemetry must never block the learner.
    await expect(
      recordRetrievalChoice({
        module: 1,
        unit_id: "unit-2",
        page_id: "u2-retrieval",
        chosen_id: "b",
        correct: false,
      }),
    ).resolves.toBeUndefined();
  });
});

// ---- loadPaidLesson (Sprint "paid modules" P3) -----------------------------
//
// Same discriminated-result contract as loadPaidUnit, applied to the new
// /module-{4,5}/units/{id}/lesson endpoints. Mis-classifying any of the
// four cases (200 / 402 signin-or-purchase / 402 purchase / other) would
// either leak paid lesson pages or trap signed-in buyers behind a wall
// they can't escape.

describe("loadPaidLesson", () => {
  const okBody = {
    module: 4,
    unit_id: "module4-unit-1",
    unit_title: "Skills overview",
    pages: [
      { id: "p1", title: "Intro", content: ["hi"], complexity: 1 },
      { id: "p2", title: "More", content: ["next"], complexity: 1 },
    ],
    stability: 0.1,
  };

  it("hits the paid /lesson path and returns kind=ok with the lesson on 200", async () => {
    mockGet.mockResolvedValueOnce({ status: 200, data: okBody });

    const res = await loadPaidLesson(4, "module4-unit-1");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-4/units/module4-unit-1/lesson",
      expect.objectContaining({ validateStatus: expect.any(Function) }),
    );
    expect(res.kind).toBe("ok");
    if (res.kind === "ok") {
      expect(res.lesson.module).toBe(4);
      expect(res.lesson.pages).toHaveLength(2);
      expect(res.lesson.unit_title).toBe("Skills overview");
    }
  });

  it("uses the module-5 path when module=5", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: { ...okBody, module: 5, unit_id: "module5-unit-1" },
    });

    await loadPaidLesson(5, "module5-unit-1");

    expect(mockGet).toHaveBeenCalledWith(
      "/api/curriculum/module-5/units/module5-unit-1/lesson",
      expect.objectContaining({ validateStatus: expect.any(Function) }),
    );
  });

  it("returns kind=paywall on 402 signin_or_purchase_required", async () => {
    mockGet.mockResolvedValueOnce({
      status: 402,
      data: {
        detail: {
          envelope_id: "billing.signin_or_purchase_required",
          product_code: "modules_4_5",
        },
      },
    });

    const res = await loadPaidLesson(4, "module4-unit-1");
    expect(res.kind).toBe("paywall");
    if (res.kind === "paywall") {
      expect(res.signal.envelope_id).toBe("billing.signin_or_purchase_required");
      expect(res.signal.product_code).toBe("modules_4_5");
    }
  });

  it("returns kind=paywall on 402 purchase_required", async () => {
    mockGet.mockResolvedValueOnce({
      status: 402,
      data: {
        detail: {
          envelope_id: "billing.purchase_required",
          product_code: "modules_4_5",
        },
      },
    });

    const res = await loadPaidLesson(5, "module5-unit-1");
    expect(res.kind).toBe("paywall");
  });

  it("returns kind=error when 402 lacks a recognized envelope_id (fail closed)", async () => {
    mockGet.mockResolvedValueOnce({
      status: 402,
      data: { detail: { envelope_id: "something.unknown" } },
    });

    const res = await loadPaidLesson(4, "module4-unit-1");
    expect(res.kind).toBe("error");
  });

  it("returns kind=error when the request rejects", async () => {
    mockGet.mockRejectedValueOnce(new Error("network down"));

    const res = await loadPaidLesson(4, "module4-unit-1");
    expect(res.kind).toBe("error");
    if (res.kind === "error") {
      expect(res.message).toMatch(/network down/);
    }
  });
});

describe("loadCurriculumMenu (S25.1)", () => {
  it("GETs /api/curriculum/menu and returns the typed tree", async () => {
    mockGet.mockResolvedValueOnce({
      status: 200,
      data: {
        modules: [
          {
            id: 1,
            title: "Module 1 — Meeting Claude",
            units: [
              { id: "unit-1", title: "Meet Claude", description: "..." },
            ],
          },
          {
            id: 2,
            title: "Module 2 — Sustained use over time",
            units: [],
          },
          { id: 3, title: "Module 3 — Long-term judgment", units: [] },
        ],
        bridge_units: [
          {
            id: "bridge-compare",
            title: "How Claude compares",
            description: "...",
          },
        ],
      },
    });

    const menu = await loadCurriculumMenu();

    expect(mockGet).toHaveBeenCalledWith("/api/curriculum/menu");
    expect(menu.modules.map((m) => m.id)).toEqual([1, 2, 3]);
    expect(menu.bridge_units).toHaveLength(1);
    expect(menu.bridge_units[0].id).toBe("bridge-compare");
  });
});
