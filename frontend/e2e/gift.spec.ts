import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

const VALID_EMAIL = "caregiver@example.com";
const INVALID_EMAIL = "not-an-email";

test.describe("Gift checkout journey (P1 guest gift checkout)", () => {
  test("/gift renders the public gift checkout form", async ({ page }) => {
    await page.goto("/gift");
    await expect(
      page.getByRole("heading", { name: "Buy mynaani as a gift" }),
    ).toBeVisible();
    await expect(page.getByLabel("Your email")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Continue to payment" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Go back" })).toBeVisible();
  });

  test("invalid email shows a calm, reversible error", async ({ page }) => {
    await page.goto("/gift");
    await page.getByLabel("Your email").fill(INVALID_EMAIL);
    await page.getByRole("button", { name: "Continue to payment" }).click();
    await expect(page.getByRole("alert")).toContainText(
      "Please enter a valid email address",
    );
  });

  test("valid email submits a guest gift checkout and redirects", async ({
    page,
  }) => {
    await page.goto("/gift");

    await page.route("**/api/v1/billing/checkout", async (route) => {
      const postData = route.request().postDataJSON();
      expect(postData).toMatchObject({
        product_code: "modules_4_5",
        is_gift: true,
        buyer_email: VALID_EMAIL,
      });
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          purchase_id: "gift-purchase-123",
          checkout_url: "about:blank",
          provider_session_id: "sess_test",
          gift_token: null,
        }),
      });
    });

    await page.getByLabel("Your email").fill(VALID_EMAIL);
    await page.getByRole("button", { name: "Continue to payment" }).click();
    await page.waitForURL("about:blank");
  });

  test("/gift-redeem requires an authenticated session", async ({ page }) => {
    await page.goto("/gift-redeem");
    await expect(page).toHaveURL(/\/signin/);
  });

  test("gift checkout page passes axe WCAG 2.1 AA", async ({ page }) => {
    await page.goto("/gift");
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
