import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Auth callback journey", () => {
  test("/auth/callback renders the pending sign-in message", async ({
    page,
  }) => {
    await page.goto("/auth/callback");
    await expect(page.getByRole("main")).toContainText(
      "One moment — finishing sign in",
    );
  });

  test("/auth/callback passes axe WCAG 2.1 AA", async ({ page }) => {
    await page.goto("/auth/callback");
    await expect(
      page.getByText("One moment — finishing sign in"),
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
