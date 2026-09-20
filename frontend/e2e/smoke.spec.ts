import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

// Post-deploy smoke suite. Every test here MUST be read-only and
// unauthenticated: deployed environments never see a purchase,
// entitlement, or form mutation from Playwright. Assertions target
// rendered content, link integrity, asset headers, and accessibility —
// the classes of regression a local dev-server run cannot catch
// (CDN/_redirects issues, asset-hash mismatches, env misconfiguration).
const isDeployed = !!process.env.PLAYWRIGHT_TEST_BASE_URL;

const AXE_OPTIONS = {
  runOnly: {
    type: "tag" as const,
    values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
  },
};

test.describe("Deployed-environment smoke", { tag: "@smoke" }, () => {
  test("landing hero renders with primary CTAs", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "How it works" }),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: /Senior facilities/i }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: /Caregiver/i })).toBeVisible();
    // LEGAL-NAV-001: the mini-footer strip pins the legal links inside
    // the fixed viewport — the conspicuous privacy link CCPA requires.
    const footer = page.getByRole("contentinfo");
    await expect(footer).toBeVisible();
    await expect(footer.getByRole("link", { name: "Privacy" })).toBeVisible();
    await expect(footer.getByRole("link", { name: "Terms" })).toBeVisible();
  });

  test("legal pages render: terms and about", async ({ page }) => {
    await page.goto("/terms");
    await expect(
      page.getByRole("heading", { name: "Terms of Service" }),
    ).toBeVisible();
    await expect(page.getByText(/within 30 days of purchase/)).toBeVisible();

    await page.goto("/about");
    await expect(
      page.getByRole("heading", { name: "About mynaani" }),
    ).toBeVisible();
  });

  test("marketing pages carry the shared fat footer", async ({ page }) => {
    for (const path of ["/caregiver", "/for-communities"]) {
      await page.goto(path);
      const footer = page.getByRole("contentinfo");
      await expect(footer).toBeVisible();
      await expect(footer.getByRole("link", { name: "Privacy" })).toBeVisible();
      await expect(footer.getByRole("link", { name: "Terms" })).toBeVisible();
      await expect(
        footer.getByRole("link", { name: "Be our partner" }),
      ).toBeVisible();
      await expect(
        footer.getByRole("link", { name: "Instagram" }),
      ).toBeVisible();
      await expect(footer.getByRole("link", { name: "TikTok" })).toBeVisible();
      await expect(footer.getByRole("link", { name: "YouTube" })).toBeVisible();
      await expect(
        footer.getByRole("link", { name: "Facebook" }),
      ).toBeVisible();
      await expect(footer.getByText(/© \d{4} mynaani/)).toBeVisible();
    }
  });

  test("/partners renders the partner inquiry form", async ({ page }) => {
    await page.goto("/partners");
    await expect(
      page.getByRole("heading", { name: "Partner with mynaani" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Send inquiry" }),
    ).toBeVisible();
  });

  test("caregiver page renders and links to gift checkout", async ({
    page,
  }) => {
    await page.goto("/caregiver");
    await expect(
      page.getByText("They learn AI.", { exact: false }),
    ).toBeVisible();
    const gift = page.getByRole("link", { name: /Gift mynaani/i }).first();
    await expect(gift).toBeVisible();
    // Read-only navigation check: the CTA resolves to the gift surface.
    await gift.click();
    await expect(page).toHaveURL(/\/(gift|.*\/gift)$/);
    await expect(page.getByText("Buy mynaani as a gift")).toBeVisible();
  });

  test("whitepaper PDFs are served with the correct content type", async ({
    request,
  }) => {
    for (const path of [
      "/whitepapers/cognitive-engagement.pdf",
      "/whitepapers/geragogy-for-caregivers.pdf",
      "/whitepapers/the-ai-gap.pdf",
      "/whitepapers/geragogy-the-key-to-learning.pdf",
    ]) {
      const response = await request.get(path);
      expect(response.status(), path).toBe(200);
      expect(response.headers()["content-type"], path).toContain(
        "application/pdf",
      );
    }
  });

  // PW.8.2 regression test for the stale gifting-ai-learning.pdf incident:
  // the retired URL must redirect to the cognitive-engagement brief.
  // Cloudflare Pages serves _redirects; the Vite dev server does not, so
  // this test only runs in deployed mode.
  test("retired gifting whitepaper redirects to cognitive engagement", async ({
    request,
  }) => {
    test.skip(!isDeployed, "redirect rules only exist on deployed Pages");
    const response = await request.get("/whitepapers/gifting-ai-learning.pdf", {
      maxRedirects: 0,
    });
    expect(response.status()).toBe(301);
    expect(response.headers()["location"]).toContain(
      "/whitepapers/cognitive-engagement.pdf",
    );
  });

  test("landing and caregiver pass axe WCAG 2.1 AA", async ({ page }) => {
    for (const path of ["/", "/caregiver"]) {
      await page.goto(path);
      await injectAxe(page);
      await checkA11y(page, undefined, {
        detailedReport: true,
        detailedReportOptions: { html: false },
        axeOptions: AXE_OPTIONS,
      });
    }
  });
});
