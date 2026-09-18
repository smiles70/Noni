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
    await expect(page.getByRole("link", { name: "Talk to us" })).toBeVisible();
    await expect(
      page.getByText("Pricing — founding partner rates"),
    ).toBeVisible();
  });

  test("/for-communities exposes contact CTAs", async ({ page }) => {
    await page.goto("/for-communities");

    // "Let's talk" routes to the senior-care form — not a mailto picker.
    // Two instances: mid-page (WS-B) + bottom contact section.
    const primary = page.getByRole("link", { name: "Let's talk" });
    await expect(primary).toHaveCount(2);
    await expect(primary.first()).toBeVisible();
    await expect(primary.first()).toHaveAttribute("href", "/partners");
    await expect(primary.last()).toHaveAttribute("href", "/partners");

    // "Talk to us" routes to the /contact page — never a mailto picker.
    const headerCta = page.getByRole("link", { name: "Talk to us" }).first();
    await expect(headerCta).toBeVisible();
    await expect(headerCta).toHaveAttribute("href", "/contact");
  });

  test("On this page menu jumps to real sections (WS-A)", async ({ page }) => {
    await page.goto("/for-communities");
    const nav = page.getByRole("navigation", { name: "On this page" });
    await expect(nav).toBeVisible();
    // Jump to Pricing — heading should land in view.
    await nav.getByRole("link", { name: "Pricing" }).click();
    await expect(
      page.getByRole("heading", { name: "Pricing — founding partner rates" }),
    ).toBeInViewport();
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
