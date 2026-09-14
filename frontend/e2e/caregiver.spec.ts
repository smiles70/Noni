import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Caregiver marketing page", () => {
  test("renders the caregiver gift journey and CTA", async ({ page }) => {
    await page.goto("/caregiver");
    await expect(
      page.getByRole("heading", { name: /Give calm, self-paced AI learning/i }),
    ).toBeVisible();
    const gift = page.getByRole("link", { name: /Gift mynaani/i }).first();
    await expect(gift).toBeVisible();
    await gift.click();
    await expect(page).toHaveURL(/\/(gift|.*\/gift)$/);
    await expect(
      page.getByRole("heading", { name: /Buy mynaani as a gift/i }),
    ).toBeVisible();
  });

  test("links to whitepapers, sources, and the learner/facility surfaces", async ({
    page,
  }) => {
    await page.goto("/caregiver");
    await expect(
      page.locator('a[href="/whitepapers/the-ai-gap.pdf"]'),
    ).toBeVisible();
    await expect(
      page.locator('a[href="/whitepapers/geragogy-the-key-to-learning.pdf"]'),
    ).toBeVisible();
    await expect(page.locator('a[href="/for-communities"]')).toBeVisible();
    await expect(page.locator('a[href="/"]')).toBeVisible();
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
