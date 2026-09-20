/**
 * Agentic CI — Ontology Crawler
 *
 * Crawls the local staging app, discovers internal routes, and records any
 * HTTP >= 400 responses or runtime console errors. It does not target
 * production.
 */
import { chromium } from "playwright";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const BASE_URL = process.env.STAGING_BASE_URL || "http://127.0.0.1:5173";
const BINARY_EXTENSIONS = new Set([".pdf", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".mp4", ".mp3"]);
const SEED_ROUTES = [
  "/",
  "/signin",
  "/welcome",
  "/setup",
  "/getting-started",
  "/curriculum",
  "/paid-curriculum",
  "/lessons",
  "/paywall",
  "/gift",
  "/gift-redeem",
  "/redeem",
  "/purchase-success",
  "/purchase-cancel",
  "/account",
  "/for-communities",
  "/admin",
  "/help",
  "/privacy",
  "/auth/callback",
];

function isBinaryPath(path) {
  const lower = path.toLowerCase();
  return Array.from(BINARY_EXTENSIONS).some((ext) => lower.endsWith(ext));
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const errors = [];
  const visited = new Set();
  const toVisit = new Set(SEED_ROUTES);

  page.on("response", (response) => {
    const status = response.status();
    if (status >= 400) {
      errors.push({
        type: "http_error",
        url: response.url(),
        status,
        route: page.url(),
      });
    }
  });

  page.on("pageerror", (error) => {
    errors.push({ type: "page_error", message: error.message, route: page.url() });
  });

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push({
        type: "console_error",
        text: msg.text(),
        route: page.url(),
      });
    }
  });

  for (const route of toVisit) {
    if (visited.has(route)) continue;
    if (isBinaryPath(route)) {
      visited.add(route);
      continue;
    }
    visited.add(route);

    const url = new URL(route, BASE_URL).toString();
    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    } catch (e) {
      errors.push({ type: "navigation_error", route, message: e.message });
      continue;
    }

    // Discover additional internal links on this route.
    const links = await page.evaluate(() =>
      Array.from(document.querySelectorAll("a[href]"))
        .map((a) => a.getAttribute("href"))
        .filter((href) => href && href.startsWith("/") && !href.startsWith("//")),
    );
    for (const href of links) {
      const clean = href.split("#")[0];
      if (!visited.has(clean) && !isBinaryPath(clean)) {
        toVisit.add(clean);
      }
    }
  }

  await browser.close();

  const report = {
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    visitedRoutes: Array.from(visited).sort(),
    errorCount: errors.length,
    errors,
    summary: errors.length === 0
      ? "No HTTP >= 400, navigation, page, or console errors detected."
      : `Detected ${errors.length} anomaly/ies during crawl.`,
  };

  const outPath = resolve(
    __dirname,
    "../../.ai/audit/2026-09-11-agentic-ontology-crawl.json",
  );
  writeFileSync(outPath, JSON.stringify(report, null, 2));
  console.log(report.summary);
  console.log(`Report written to ${outPath}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
