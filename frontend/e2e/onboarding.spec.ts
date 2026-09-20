import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";
import { setupAuth } from "./utils/auth";

test.describe("Onboarding journey (EPIC-002 Phase 2-3)", () => {
  test("/welcome requires an authenticated session", async ({ page }) => {
    await page.goto("/welcome");
    await expect(page).toHaveURL(/\/signin/);
  });

  test("/welcome redirects a new learner to /setup", async ({ page }) => {
    await setupAuth(page, { onboarding: { complete: false } });
    await page.goto("/welcome");
    await page.waitForURL("/setup");
    await expect(page).toHaveURL(/\/setup/);
  });

  test("/setup form can be completed and continues to /getting-started", async ({
    page,
  }) => {
    await setupAuth(page, { profileOk: true });
    await page.goto("/setup");

    await expect(
      page.getByRole("heading", { name: "Account setup" }),
    ).toBeVisible();

    await page.getByLabel("Display name").fill("Maya");
    await page.locator("#font-size").selectOption("large");
    await page.locator("#pace").selectOption("flexible");
    await page.getByRole("button", { name: "Complete setup" }).click();

    await expect(page.getByText("Account setup complete")).toBeVisible();
    await page.waitForURL("/getting-started", { timeout: 6000 });
    await expect(
      page.getByRole("heading", { name: "Getting started" }),
    ).toBeVisible();
  });

  test("/getting-started passes axe WCAG 2.1 AA", async ({ page }) => {
    await setupAuth(page);
    await page.goto("/getting-started");
    await expect(
      page.getByRole("heading", { name: "Getting started" }),
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
