import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";
import { setupAuth } from "./utils/auth";

const PAYWALL_PRODUCT = "modules_4_5";

test.describe("Paywall journey (account.paywall)", () => {
  test("/paywall requires an authenticated session", async ({ page }) => {
    await page.goto("/paywall");
    await expect(page).toHaveURL(/\/signin/);
  });

  test("/paywall is geragogy-calm and exposes all three exits", async ({
    page,
  }) => {
    await setupAuth(page);
    await page.goto("/paywall");

    await expect(
      page.getByRole("heading", { name: "Continue your learning" }),
    ).toBeVisible();

    const forbidden = [
      "hurry",
      "urgent",
      "limited time",
      "act now",
      "expires",
      "only today",
    ];
    const text = (await page.textContent("main"))?.toLowerCase() ?? "";
    for (const word of forbidden) {
      expect(text).not.toContain(word);
    }

    await expect(
      page.getByRole("button", { name: "Continue and purchase for myself" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Buy as a gift for someone else" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "I have a gift code to redeem" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Go back" })).toBeVisible();
  });

  test("self-purchase starts checkout and redirects to the provider", async ({
    page,
  }) => {
    await setupAuth(page, {
      checkout: { isGift: false, checkoutUrl: "about:blank" },
    });
    await page.goto("/paywall");
    await page
      .getByRole("button", { name: "Continue and purchase for myself" })
      .click();
    await page.waitForURL("about:blank");
  });

  test("gift purchase appends the token to the checkout url", async ({
    page,
  }) => {
    await setupAuth(page, {
      checkout: {
        isGift: true,
        checkoutUrl: "about:blank",
        giftToken: "gtok_abc123",
      },
    });
    await page.goto("/paywall");
    await page
      .getByRole("button", { name: "Buy as a gift for someone else" })
      .click();
    await page.waitForURL(/about:blank.*gift_token=gtok_abc123/);
  });

  test("gift-code redeem button routes to /gift-redeem", async ({ page }) => {
    await setupAuth(page);
    await page.goto("/paywall");
    await page
      .getByRole("button", { name: "I have a gift code to redeem" })
      .click();
    await page.waitForURL("/gift-redeem");
    await expect(page).toHaveURL(/\/gift-redeem/);
  });

  test("organization code can be redeemed for curriculum access", async ({
    page,
  }) => {
    await setupAuth(page, { orgRedeem: { productCode: PAYWALL_PRODUCT } });
    await page.goto("/paywall");

    await page
      .getByRole("textbox", { name: "Organization access code" })
      .fill("COMMUNITY-2026");
    await page
      .getByRole("button", { name: "Continue with organization code" })
      .click();

    await page.waitForURL("/curriculum");
    await expect(page).toHaveURL(/\/curriculum/);
  });

  test("/paywall passes axe WCAG 2.1 AA", async ({ page }) => {
    await setupAuth(page);
    await page.goto("/paywall");
    await expect(
      page.getByRole("heading", { name: "Continue your learning" }),
    ).toBeVisible();
    await injectAxe(page);
    await checkA11y(page, undefined, {
      detailedReport: true,
      detailedReportOptions: { html: false },
      axeOptions: {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
        },
      },
    });
  });
});
