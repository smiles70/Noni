import { test, expect } from "@playwright/test";

// Avoid the mock provider's useEffect call to the backend; we only want to
// test the post-purchase routing contract in the success surface.
const SUCCESS_BASE =
  "/purchase/success?purchase=test&product=modules_4_5&is_gift={is_gift}&provider=stripe";

test.describe("Post-purchase success routing", () => {
  test("self-purchase success routes to the paid track", async ({ page }) => {
    await page.goto(SUCCESS_BASE.replace("{is_gift}", "false"));
    await page
      .getByRole("button", { name: "Continue to the paid modules" })
      .click();
    await expect(page).toHaveURL(/\/paid-curriculum$/);
  });

  test("gift purchase success returns home", async ({ page }) => {
    await page.goto(SUCCESS_BASE.replace("{is_gift}", "true"));
    await page.getByRole("button", { name: "Return to home" }).click();
    await expect(page).toHaveURL(/\/$/);
  });
});
