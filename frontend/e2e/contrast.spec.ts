import { test, expect } from "@playwright/test";
import { runContrastAudit, formatViolations } from "./utils/runContrastAudit";

/**
 * Contrast Audit
 *
 * Targets WCAG 2.1 AA on every reachable view. AAA (geragogy 7:1) is
 * tracked as a future step-release in `frontend/src/design/contrastRatios.ts`
 * and is NOT enforced at launch.
 *
 * Auth-gated views (paywall, gift_redeem, account_settings) redirect to
 * SignInPage when unauthenticated — so SignInPage IS the rendered surface
 * for those routes, and is covered by the "sign-in page" test here.
 * A follow-up spec with auth mocks will cover the gated views directly.
 */

test.describe("Contrast Audit (WCAG 2.1 AA)", () => {
  test("landing page", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    const violations = await runContrastAudit(page);
    expect(
      violations,
      `Landing page contrast failures:\n${formatViolations(violations)}`
    ).toHaveLength(0);
  });

  test("sign-in page", async ({ page }) => {
    await page.goto("/");
    const signIn = page.getByRole("button", { name: /sign in/i });
    if (await signIn.isVisible().catch(() => false)) {
      await signIn.click();
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    }

    const violations = await runContrastAudit(page);
    expect(
      violations,
      `Sign-in page contrast failures:\n${formatViolations(violations)}`
    ).toHaveLength(0);
  });

  test("curriculum view (free track)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Begin calmly" }).click();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    const violations = await runContrastAudit(page);
    expect(
      violations,
      `Curriculum view contrast failures:\n${formatViolations(violations)}`
    ).toHaveLength(0);
  });

  test("curriculum menu (lessons list)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Begin calmly" }).click();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    const lessons = page.getByRole("button", { name: /lessons/i });
    if (await lessons.isVisible().catch(() => false)) {
      await lessons.click();
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    }

    const violations = await runContrastAudit(page);
    expect(
      violations,
      `Curriculum menu contrast failures:\n${formatViolations(violations)}`
    ).toHaveLength(0);
  });

  test("larger-text mode preserves contrast", async ({ page }) => {
    await page.goto("/");
    const toggle = page.getByRole("button", { name: "Larger text" });
    await toggle.click();
    await expect(page.locator("html")).toHaveClass(/large-text/);

    const violations = await runContrastAudit(page);
    expect(
      violations,
      `Larger-text mode contrast failures:\n${formatViolations(violations)}`
    ).toHaveLength(0);
  });
});
