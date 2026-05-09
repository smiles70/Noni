import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Curriculum view", () => {
  test("reachable via primary CTA and shows a heading", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Begin calmly" }).click();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("exposes a Return-to-start affordance (reversibility)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Begin calmly" }).click();
    const back = page.getByRole("button", { name: "Return to start" });
    await expect(back).toBeVisible();
    await back.click();
    await expect(page.getByRole("button", { name: "Begin calmly" })).toBeVisible();
  });

  test("passes WCAG 2.1 AA automated checks (axe-core)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Begin calmly" }).click();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await injectAxe(page);
    await checkA11y(page, undefined, {
      detailedReport: true,
      detailedReportOptions: { html: false },
      axeOptions: {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
      },
    });
  });
});
