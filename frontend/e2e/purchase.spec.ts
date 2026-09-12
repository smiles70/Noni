import { test, expect } from "@playwright/test";

// Avoid the mock provider's useEffect call to the backend; we only want to
// test the post-purchase routing contract in the success surface.
const SUCCESS_BASE =
  "/purchase/success?purchase=test&product=modules_4_5&is_gift={is_gift}&provider=stripe";

test.describe("Post-purchase success routing", () => {
  // The self-purchase "Continue to the paid modules" CTA routes to
  // /paid-curriculum, which is behind RequireAuth. In an E2E context without
  // a signed-in session, the page correctly redirects to /signin. The exact
  // route to /paid-curriculum is covered by a journey-contract unit test.

  test("gift purchase success returns home", async ({ page }) => {
    await page.goto(SUCCESS_BASE.replace("{is_gift}", "true"));
    await page.getByRole("button", { name: "Return to home" }).click();
    await expect(page).toHaveURL(/\/$/);
  });

  test("chat widget marker is present in gift mode only", async ({
    page,
  }) => {
    await page.goto(SUCCESS_BASE.replace("{is_gift}", "true"));
    await expect(
      page.locator('[data-contract-exemption="chat-widget"]'),
    ).toHaveCount(1);

    await page.goto(SUCCESS_BASE.replace("{is_gift}", "false"));
    await expect(
      page.locator('[data-contract-exemption="chat-widget"]'),
    ).toHaveCount(0);
  });
});
