import { test, expect } from "@playwright/test";

const VIEWPORTS = [
  { name: "iPhoneSE", width: 375, height: 667 },
  { name: "iPadMini", width: 768, height: 1024 },
  { name: "Desktop", width: 1440, height: 900 },
  { name: "LargeDesktop", width: 1920, height: 1080 },
];

const ROUTES = ["/", "/lessons", "/paywall", "/account", "/redeem"];

for (const viewport of VIEWPORTS) {
  test.describe(`Responsive: ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    const minTarget =
      viewport.width < 768 ? 48 : viewport.width < 1024 ? 44 : 40;

    for (const route of ROUTES) {
      test(`no horizontal scroll on ${route || "root"}`, async ({ page }) => {
        await page.goto(route);
        const scrollWidth = await page.evaluate(
          () => document.documentElement.scrollWidth
        );
        const clientWidth = await page.evaluate(
          () => document.documentElement.clientWidth
        );
        expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
      });

      test(`all buttons meet minimum touch target on ${route || "root"}`, async ({ page }) => {
        await page.goto(route);
        const buttons = await page.locator("button, a, [role='button']").all();

        for (const button of buttons) {
          const box = await button.boundingBox();
          if (!box) continue;
          // Skip hidden or zero-area controls
          if (box.width === 0 || box.height === 0) continue;
          expect(box.width).toBeGreaterThanOrEqual(minTarget);
          expect(box.height).toBeGreaterThanOrEqual(minTarget);
        }
      });

      test(`text is readable without zoom on ${route || "root"}`, async ({ page }) => {
        await page.goto(route);
        const fontSizes = await page.evaluate(() => {
          const allText = Array.from(document.querySelectorAll("*"));
          return allText
            .filter((el) => el.children.length === 0 && el.textContent?.trim())
            .map((el) => {
              const style = window.getComputedStyle(el);
              return parseFloat(style.fontSize);
            })
            .filter((size) => size > 0);
        });

        expect(fontSizes.length).toBeGreaterThan(0);
        const minFontSize = Math.min(...fontSizes);
        expect(minFontSize).toBeGreaterThanOrEqual(12);
      });
    }

    test("landing hero serves mobile art-directed image on iPhoneSE", async ({ page }) => {
      // Only meaningful for the mobile viewport
      if (viewport.name !== "iPhoneSE") {
        test.skip();
      }

      await page.goto("/");
      const source = await page.locator("picture source").getAttribute("srcset");
      expect(source).toBe("/hero-mobile.jpg");
    });
  });
}
