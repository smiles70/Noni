import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

test.describe("Partner / community journey (B2B-LANDING-001)", () => {
  test("/for-communities renders the B2B marketing surface", async ({
    page,
  }) => {
    await page.goto("/for-communities");
    await expect(
      page.getByRole("heading", { name: "AI learning grounded in geragogy" }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", {
        name: "Why communities partner with mynaani",
      }),
    ).toBeVisible();
    await expect(page.getByText("Talk to us about a pilot")).toBeVisible();
    await expect(
      page.getByText("Pricing — founding partner rates"),
    ).toBeVisible();
  });

  test("/for-communities exposes mailto contact CTAs", async ({ page }) => {
    await page.goto("/for-communities");

    const primary = page.getByRole("link", {
      name: /Email hello@mynaani\.com/,
    });
    await expect(primary).toBeVisible();
    await expect(primary).toHaveAttribute("href", /^mailto:hello@mynaani\.com/);

    const headerCta = page.getByRole("link", { name: "Talk to us" }).first();
    await expect(headerCta).toBeVisible();
    await expect(headerCta).toHaveAttribute(
      "href",
      /^mailto:hello@mynaani\.com/,
    );
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
      page.getByRole("heading", {
        name: "Why communities partner with mynaani",
      }),
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
