import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

// The learner journey entry point: landing → "How it works" dialog →
// "Continue to my account — free" → /signin (auth gate for curriculum).
async function beginJourney(page) {
  await page.getByRole("button", { name: "How it works" }).click();
  await page
    .getByRole("button", { name: "Continue to my account — free" })
    .click();
}

test.describe("Curriculum view", () => {
  test("reachable via primary CTA and shows a heading", async ({ page }) => {
    await page.goto("/");
    await beginJourney(page);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("exposes a reversible exit from the How-it-works dialog", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "How it works" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(dialog).not.toBeVisible();
    await expect(
      page.getByRole("button", { name: "How it works" }),
    ).toBeVisible();
  });

  test("passes WCAG 2.1 AA automated checks (axe-core)", async ({ page }) => {
    await page.goto("/");
    await beginJourney(page);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
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
