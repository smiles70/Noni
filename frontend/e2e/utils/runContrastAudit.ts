import { Page } from "@playwright/test";
import { injectAxe } from "axe-playwright";
import {
  AXE_CONTRAST_OPTIONS,
  AA_CONTRAST_RATIO,
  AAA_CONTRAST_RATIO,
  ContrastViolation,
} from "./axeConfig";

/**
 * Run a color-contrast-only axe audit on the current page.
 *
 * @param page Playwright Page instance (already navigated)
 * @returns Array of contrast violations (empty when all pass)
 */
export async function runContrastAudit(
  page: Page
): Promise<ContrastViolation[]> {
  await injectAxe(page);

  const results = await page.evaluate(async (opts) => {
    // axe is attached to window by injectAxe()
    return await (window as unknown as { axe: { run: (ctx: Document, o: unknown) => Promise<{ violations: unknown[] }> } }).axe.run(
      document,
      opts
    );
  }, AXE_CONTRAST_OPTIONS);

  return (results.violations || []) as ContrastViolation[];
}

/**
 * Format violations into a human-readable report for CI logs.
 */
export function formatViolations(violations: ContrastViolation[]): string {
  if (violations.length === 0) return "No contrast violations.";

  return violations
    .flatMap((v) =>
      v.nodes.map((node) => {
        const data = node.any[0]?.data;
        return [
          `  ❌ ${v.description}`,
          `     Element: ${node.target.join(" > ")}`,
          `     HTML: ${node.html.slice(0, 120)}`,
          data
            ? `     Colors: ${data.fgColor} on ${data.bgColor} (ratio ${data.contrastRatio})`
            : "",
          `     Required: >= ${AA_CONTRAST_RATIO} (AA) | aspiration >= ${AAA_CONTRAST_RATIO} (AAA)`,
        ]
          .filter(Boolean)
          .join("\n");
      })
    )
    .join("\n\n");
}
