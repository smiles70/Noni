/**
 * Unit tests for `api/billing.ts`.
 *
 * The billing client is thin but its request bodies are part of the
 * billing contract (see backend A4 tests). If a field name drifts here
 * silently, the paywall will look like it works while charging the wrong
 * product. These tests pin the exact field names.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

const { mockGet, mockPost, mockUse } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockUse: vi.fn(),
}));

// client.ts (imported transitively via billing.ts) registers a Bearer
// interceptor at module load. The mocked axios.create must therefore
// include `interceptors.request.use` or the import would crash.
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

import { claimGift, previewGift, startCheckout } from "../billing";

afterEach(() => {
  mockGet.mockReset();
  mockPost.mockReset();
});

describe("startCheckout", () => {
  it("sends product_code + is_gift exactly as the backend expects", async () => {
    mockPost.mockResolvedValueOnce({
      data: {
        purchase_id: "p-1",
        checkout_url: "https://mock/checkout",
        provider_session_id: "cs_mock_1",
      },
    });

    const res = await startCheckout("modules_4_5", false);

    expect(mockPost).toHaveBeenCalledWith("/api/billing/checkout", {
      product_code: "modules_4_5",
      is_gift: false,
    });
    expect(res.purchase_id).toBe("p-1");
    expect(res.checkout_url).toMatch(/^https:\/\//);
  });

  it("flags is_gift=true for gift purchases", async () => {
    mockPost.mockResolvedValueOnce({
      data: { purchase_id: "p-2", checkout_url: "x", provider_session_id: "y" },
    });
    await startCheckout("modules_4_5", true);
    expect(mockPost).toHaveBeenLastCalledWith("/api/billing/checkout", {
      product_code: "modules_4_5",
      is_gift: true,
    });
  });
});

describe("gift redemption", () => {
  it("previewGift posts the token under the `token` key", async () => {
    mockPost.mockResolvedValueOnce({
      data: { valid: true, product_code: "modules_4_5", purchase_id: "p-1" },
    });
    const res = await previewGift("abc");
    expect(mockPost).toHaveBeenCalledWith("/api/gifts/preview", { token: "abc" });
    expect(res.valid).toBe(true);
  });

  it("claimGift posts the token under the `token` key", async () => {
    mockPost.mockResolvedValueOnce({
      data: {
        purchase_id: "p-1",
        product_code: "modules_4_5",
        granted_to_account_id: "acc-1",
      },
    });
    const res = await claimGift("abc");
    expect(mockPost).toHaveBeenCalledWith("/api/gifts/claim", { token: "abc" });
    expect(res.granted_to_account_id).toBe("acc-1");
  });
});
