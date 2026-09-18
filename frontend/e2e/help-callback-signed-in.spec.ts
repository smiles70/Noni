import { test, expect } from "@playwright/test";

// learner-help-channel signed-in e2e (Noni#71): a real session must carry
// the account identity to the callback so the CRM files one contact with
// email + phone. Unlike help-callback.spec.ts this spec does NOT stub the
// POST — it exercises the deployed backend. Run only against an
// environment whose callback path is safe to trigger (fictional 555
// numbers; rate-limit-aware, one phone per browser project).

const EMAIL = "help-e2e@test.dev";

const PHONE_BY_PROJECT: Record<string, string> = {
  chromium: "2025550411",
  firefox: "2025550422",
  "mobile-pixel": "2025550433",
  webkit: "2025550444",
  "mobile-iphone": "2025550455",
};

test.describe("Signed-in learner callback", () => {
  test("sends the Bearer token and reaches confirmation", async ({
    page,
  }, testInfo) => {
    const phone = PHONE_BY_PROJECT[testInfo.project.name] ?? "2025550499";

    await page.goto("/");
    await page.evaluate((email) => {
      localStorage.setItem("mynaani.mock_token", `mock:${email}`);
    }, EMAIL);

    await page.goto("/curriculum");
    await page.getByRole("button", { name: "Help" }).click();
    await page.getByRole("button", { name: "Call me" }).click();
    await page.locator("#help-phone").fill(phone);

    const callbackRequest = page.waitForRequest("**/api/v1/help/callback");
    await page.getByRole("button", { name: "Call me now" }).click();
    const request = await callbackRequest;

    expect(request.headers()["authorization"]).toBe(`Bearer mock:${EMAIL}`);

    await expect(
      page.getByRole("status").filter({ hasText: /call/i }),
    ).toBeVisible();
  });
});
