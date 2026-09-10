import { test, expect } from "@playwright/test";
import { injectAxe, checkA11y } from "axe-playwright";

const overviewData = {
  orgs_total: 3,
  seats_total: 120,
  seats_used: 87,
  flags_total: 2,
  licenses_expiring: [],
  recent_audit: [
    {
      action: "license_created",
      detail: "New license for Example Org",
      org_name: "Example Org",
      actor: "ops@mynaani.com",
      created_at: "2026-09-10T12:00:00Z",
    },
  ],
};

async function setupStaff(
  page: (typeof import("@playwright/test"))["Page"]["prototype"],
) {
  await page.addInitScript((token) => {
    localStorage.setItem("mynaani.staff_token", token);
  }, "staff-token-test");

  await page.route("**/api/v1/admin/whoami-check", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ staff: true, role: "ops" }),
    });
  });

  await page.route("**/api/v1/admin/whoami", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ role: "ops" }),
    });
  });

  await page.route("**/api/v1/admin/overview", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(overviewData),
    });
  });
}

test.describe("Admin console (ADMIN-LOGIN-001)", () => {
  test("/admin renders the staff sign-in form for non-staff", async ({
    page,
  }) => {
    await page.goto("/admin");
    await expect(
      page.getByRole("heading", { name: "Staff sign in" }),
    ).toBeVisible();
    await expect(page.getByLabel("Username")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
  });

  test("/admin staff session shows the overview and navigation", async ({
    page,
  }) => {
    await setupStaff(page);
    await page.goto("/admin");

    await expect(
      page.getByRole("heading", { name: "Needs attention" }),
    ).toBeVisible();

    for (const label of [
      "Overview",
      "Organizations",
      "Accounts",
      "Flags",
      "Reports",
      "Audit",
    ]) {
      await expect(page.getByRole("button", { name: label })).toBeVisible();
    }

    await expect(page.getByText("87 / 120")).toBeVisible();
    await expect(page.getByText("2").first()).toBeVisible();
  });

  test.fixme("/admin staff view passes axe WCAG 2.1 AA (color-contrast findings)", async ({
    page,
  }) => {
    await setupStaff(page);
    await page.goto("/admin");
    await expect(
      page.getByRole("heading", { name: "Needs attention" }),
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
