import { expect, type Page } from "@playwright/test";

export const MOCK_TOKEN = "mock:test@example.com";

export const genericEnvelope = {
  state_id: "e2e.generic",
  authorized_components: [
    "Heading",
    "Body",
    "Button",
    "Card",
    "ConfirmDialog",
    "Divider",
    "Field",
    "Indicator",
    "List",
  ],
  interaction_limits: {
    max_primary_actions: 5,
    max_irreversible_actions: 1,
    max_highlighted_recommendations: 1,
    max_visible_text_levels: 3,
  },
  layout_constraints: {
    grid_base_px: 8,
    allowed_spacing_px: [4, 8, 16, 24, 32, 48],
    spatial_stability: true,
    reflow_permitted: false,
  },
  transition_permissions: [],
};

interface SetupAuthOptions {
  onboarding?: { complete: boolean };
  profileOk?: boolean;
  checkout?: { isGift: boolean; checkoutUrl: string; giftToken?: string };
  orgRedeem?: { productCode: string };
  deleteOk?: boolean;
}

export async function setupAuth(page: Page, opts: SetupAuthOptions = {}) {
  await page.addInitScript((token) => {
    localStorage.setItem("mynaani.mock_token", token);
  }, MOCK_TOKEN);

  await page.route("**/api/v1/auth/session", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        subject: "mock:test@example.com",
        materialized: true,
        account_id: "test-account-1",
        email: "test@example.com",
        display_name: null,
      }),
    });
  });

  await page.route("**/api/ui-envelope/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(genericEnvelope),
    });
  });

  if (opts.onboarding) {
    await page.route("**/account/onboarding-status", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          account_id: "test-account-1",
          onboarding_complete: opts.onboarding!.complete,
          display_name: null,
          preferences_set: false,
        }),
      });
    });
  }

  if (opts.profileOk) {
    await page.route("**/api/v1/account/profile", async (route) => {
      const postData = route.request().postDataJSON();
      if (postData) {
        expect(postData).toHaveProperty("displayName");
        expect(postData).toHaveProperty("preferences");
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ok: true }),
      });
    });
  }

  if (opts.checkout) {
    await page.route("**/api/v1/billing/checkout", async (route) => {
      const postData = route.request().postDataJSON();
      if (postData) {
        expect(postData).toHaveProperty("product_code");
        expect(postData).toHaveProperty("is_gift", opts.checkout!.isGift);
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          purchase_id: "paywall-purchase-123",
          checkout_url: opts.checkout!.checkoutUrl,
          provider_session_id: "sess_test",
          gift_token: opts.checkout!.giftToken ?? null,
        }),
      });
    });
  }

  if (opts.orgRedeem) {
    await page.route("**/api/v1/billing/org/redeem", async (route) => {
      const postData = route.request().postDataJSON();
      if (postData) {
        expect(postData).toHaveProperty("code");
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          granted: true,
          product_code: opts.orgRedeem!.productCode,
        }),
      });
    });
  }

  if (opts.deleteOk) {
    await page.route("**/api/v1/me/delete", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ scheduled: true }),
      });
    });
  }
}
