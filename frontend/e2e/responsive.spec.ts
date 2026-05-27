import { test, expect } from "@playwright/test";

const VIEWPORTS = [
  { name: "iPhoneSE", width: 375, height: 667 },
  { name: "iPadMini", width: 768, height: 1024 },
  { name: "Desktop", width: 1440, height: 900 },
  { name: "LargeDesktop", width: 1920, height: 1080 },
];

for (const viewport of VIEWPORTS) {
  test.describe(`Responsive: ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    test("no horizontal scroll on landing", async ({ page }) => {
      await page.goto("/");
      const scrollWidth = await page.evaluate(
        () => document.documentElement.scrollWidth
      );
      const clientWidth = await page.evaluate(
        () => document.documentElement.clientWidth
      );
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
    });

    test("all buttons meet minimum touch target", async ({ page }) => {
      await page.goto("/");
      const buttons = await page.locator("button, a, [role='button']").all();

      for (const button of buttons) {
        const box = await button.boundingBox();
        expect(box?.width ?? 0).toBeGreaterThanOrEqual(44);
        expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
      }
    });

    test("text is readable without zoom", async ({ page }) => {
      await page.goto("/");
      const fontSizes = await page.evaluate(() => {
        const allText = Array.from(document.querySelectorAll("*"));
        return allText
          .filter((el) => el.children.length === 0 && el.textContent?.trim())
          .map((el) => {
            const style = window.getComputedStyle(el);
            return parseFloat(style.fontSize);
          });
      });

      const minFontSize = Math.min(...fontSizes);
      expect(minFontSize).toBeGreaterThanOrEqual(12);
    });
  });
}
