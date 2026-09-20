import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";
import { setupAuth } from "./utils/auth";

test.describe("Account settings journey (account.settings)", () => {
  test("/account requires an authenticated session", async ({ page }) => {
    await page.goto("/account");
    await expect(page).toHaveURL(/\/signin/);
  });

  test("/account renders identity and reversible actions", async ({ page }) => {
    await setupAuth(page);
    await page.goto("/account");

    await expect(
      page.getByRole("heading", { name: "Your account" }),
    ).toBeVisible();
    await expect(page.getByText("test@example.com")).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Delete my account" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Go back" })).toBeVisible();
  });

  test("signing out returns the learner to the landing page", async ({
    page,
  }) => {
    await setupAuth(page);
    await page.goto("/account");
    await page.getByRole("button", { name: "Sign out" }).click();
    await page.waitForURL("/");
    await expect(page).toHaveURL("/");
  });

  test("account deletion is confirmed before it is scheduled", async ({
    page,
  }) => {
    await setupAuth(page, { deleteOk: true });
    await page.goto("/account");

    await page.getByRole("button", { name: "Delete my account" }).click();
    await expect(
      page.getByText("This will change your account access"),
    ).toBeVisible();
    await page.getByRole("button", { name: "Continue and delete" }).click();

    await expect(
      page.getByText("Your account has been scheduled for deletion"),
    ).toBeVisible();
    await page.waitForURL("/", { timeout: 5000 });
    await expect(page).toHaveURL("/");
  });

  test("/account passes axe WCAG 2.1 AA", async ({ page }) => {
    await setupAuth(page);
    await page.goto("/account");
    await expect(
      page.getByRole("heading", { name: "Your account" }),
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
