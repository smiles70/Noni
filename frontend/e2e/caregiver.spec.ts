import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Caregiver marketing page (bid-17)", () => {
  test("renders the caregiver gift journey and CTA", async ({ page }) => {
    await page.goto("/caregiver");
    // Hero heading is the primary h1 on the page.
    await expect(
      page.getByText("They learn AI.", { exact: false }),
    ).toBeVisible();
    const gift = page.getByRole("link", { name: /Gift mynaani/i }).first();
    await expect(gift).toBeVisible();
    await gift.click();
    await expect(page).toHaveURL(/\/(gift|.*\/gift)$/);
    await expect(page.getByText("Buy mynaani as a gift")).toBeVisible();
  });

  test("links to whitepapers, sources, and the learner/facility surfaces", async ({
    page,
  }) => {
    await page.goto("/caregiver");
    await expect(
      page.locator('a[href="/whitepapers/cognitive-engagement.pdf"]'),
    ).toBeVisible();
    await expect(
      page.locator('a[href="/whitepapers/geragogy-for-caregivers.pdf"]'),
    ).toBeVisible();
    // Cross-persona way-back to the facility surface.
    await expect(
      page.getByRole("link", { name: /our community program/i }),
    ).toBeVisible();
    // Home is linked from the logo (aria-label) and the footer.
    await expect(
      page.getByRole("link", { name: /mynaani home/i }),
    ).toBeVisible();
    // Toll-free line present.
    await expect(
      page.locator('a[href="tel:+18774094144"]').first(),
    ).toBeVisible();
  });

  test("passes WCAG 2.1 AA automated checks (axe-core)", async ({ page }) => {
    await page.goto("/caregiver");
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
