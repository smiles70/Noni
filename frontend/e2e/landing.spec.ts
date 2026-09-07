import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Landing page", () => {
  test("renders backend-served copy and primary CTA", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "How it works" }),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: /communities/i }),
    ).toBeVisible();
  });

  test("primary CTA advances to curriculum view", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "How it works" }).click();
    await page
      .getByRole("button", { name: "Continue to my account — free" })
      .click();
    // unauthenticated begin routes through the sign-in gate
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
  });

  test("larger-text toggle updates aria-pressed and html class", async ({
    page,
  }) => {
    await page.goto("/");
    const toggle = page.getByRole("button", { name: "Larger text" });
    await expect(toggle).toHaveAttribute("aria-pressed", "false");
    await toggle.click();
    const after = page.getByRole("button", { name: "Standard text" });
    await expect(after).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator("html")).toHaveClass(/large-text/);
  });

  test("passes WCAG 2.1 AA automated checks (axe-core)", async ({ page }) => {
    await page.goto("/");
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
