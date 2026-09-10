#!/usr/bin/env node
/**
 * Smoke gate — Lighthouse performance / best-practices / a11y.
 *
 * Expects `lighthouse` to be available in the dev environment.
 * Install with: npm add -D lighthouse
 *
 * Usage:
 *   npm run smoke:lighthouse
 *   SMOKE_URL=https://www.mynaani.com npm run smoke:lighthouse
 */
import { spawn } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const url = process.env.SMOKE_URL || "https://www.mynaani.com";
const budget = process.env.LIGHTHOUSE_BUDGET || "lighthouse-budget.json";

const outDir = resolve(__dirname, "../.ai/audit");
mkdirSync(outDir, { recursive: true });
const outPath = resolve(outDir, "lighthouse-smoke.json");

const args = [url, "--output=json", `--output-path=${outPath}`];
args.push(
  '--chrome-flags="--headless --no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --single-process"',
);
args.push("--only-categories=performance,accessibility,best-practices");
if (budget && existsSync(resolve(__dirname, budget))) {
  args.push(`--budget-path=${resolve(__dirname, budget)}`);
}

const child = spawn("lighthouse", args, { stdio: "inherit", shell: true });

child.on("error", (err) => {
  if (err.code === "ENOENT") {
    console.error("lighthouse is not installed. Run: npm add -D lighthouse");
    process.exit(1);
  }
  throw err;
});

child.on("close", (code) => process.exit(code ?? 1));
