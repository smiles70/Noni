import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Partner / community journey (bid-17, B2B-LANDING-001)", () => {
  test("/for-communities renders the B2B marketing surface", async ({
    page,
  }) => {
    await page.goto("/for-communities");
    await expect(
      page.getByRole("heading", {
        name: /AI learning your residents actually finish/i,
      }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: /Budget you can defend/i }),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Start a conversation" }).first(),
    ).toBeVisible();
    await expect(page.getByText("Founding Partner rates")).toBeVisible();
  });

  test("/for-communities exposes contact CTAs", async ({ page }) => {
    await page.goto("/for-communities");

    // "Start a conversation" CTAs — nav scrolls to #contact, band routes
    // to the senior-care form — never a mailto picker.
    const bandCta = page.locator('#contact a[href="/partners"]');
    await expect(bandCta).toBeVisible();
    await expect(bandCta).toHaveAttribute("href", "/partners");

    // Toll-free line present.
    await expect(
      page.locator('a[href="tel:+18774094144"]').first(),
    ).toBeVisible();
  });

  test("/for-communities is a public, no-paywall surface", async ({ page }) => {
    await page.goto("/for-communities");
    await expect(page).toHaveURL("/for-communities");
    await expect(page.getByText("Buy", { exact: true })).not.toBeVisible();
    await expect(page.getByText("Purchase", { exact: true })).not.toBeVisible();
  });

  test("/for-communities passes axe WCAG 2.1 AA", async ({ page }) => {
    await page.goto("/for-communities");
    await expect(
      page.getByRole("heading", { name: /Budget you can defend/i }),
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
