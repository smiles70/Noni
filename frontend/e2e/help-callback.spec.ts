import { test, expect } from "@playwright/test";

// learner-help-channel intake: the in-place help card on curriculum
// surfaces. Mock auth (VITE_AUTH_PROVIDER=mock) signs in via localStorage
// token — see AuthProvider tests. The callback POST is intercepted so the
// spec never places a real phone call.

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/help/callback", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "calling", calling: true }),
    }),
  );
  await page.goto("/");
  await page.evaluate(() =>
    localStorage.setItem("mynaani.mock_token", "mock:learner@example.com"),
  );
});

test.describe("Curriculum help card", () => {
  test("Help swaps the lesson body for the Call me card", async ({ page }) => {
    await page.goto("/curriculum");
    await page.waitForLoadState("networkidle");
    await page.getByRole("button", { name: "Help" }).click();
    await expect(
      page.getByRole("heading", { name: "Get help with this lesson" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Call me" })).toBeVisible();
  });

  test("Back to lesson restores the lesson view", async ({ page }) => {
    await page.goto("/curriculum");
    await page.getByRole("button", { name: "Help" }).click();
    await page.getByRole("button", { name: "Back to lesson" }).click();
    await expect(
      page.getByRole("heading", { name: "Get help with this lesson" }),
    ).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: /Continue|Try again/i }).first(),
    ).toBeVisible();
  });

  test("Call me → number field → confirmation", async ({ page }) => {
    await page.goto("/curriculum");
    await page.getByRole("button", { name: "Help" }).click();
    await page.getByRole("button", { name: "Call me" }).click();
    await page.getByLabel("Your phone number").fill("555-123-4567");
    await page.getByRole("button", { name: "Call me now" }).click();
    await expect(page.getByText(/we are calling you now/i)).toBeVisible();
  });

  test("never renders a floating widget or overlay", async ({ page }) => {
    await page.goto("/curriculum");
    await page.getByRole("button", { name: "Help" }).click();
    // Contract check: help lives inside the normal page flow — no
    // fixed-position element may appear.
    const fixed = await page.evaluate(() => {
      return Array.from(document.querySelectorAll("*")).some(
        (el) => getComputedStyle(el).position === "fixed",
      );
    });
    expect(fixed).toBe(false);
  });
});
