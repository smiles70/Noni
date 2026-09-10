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
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const url = process.env.SMOKE_URL || "https://www.mynaani.com";
const budget = process.env.LIGHTHOUSE_BUDGET || "lighthouse-budget.json";

const args = [url, "--output=json", `--output-path=${resolve(__dirname, "../.ai/audit/lighthouse-smoke.json")}`];
if (budget) args.push(`--budget-path=${resolve(__dirname, budget)}`);

const child = spawn("lighthouse", args, { stdio: "inherit", shell: true });

child.on("error", (err) => {
  if (err.code === "ENOENT") {
    console.error("lighthouse is not installed. Run: npm add -D lighthouse");
    process.exit(1);
  }
  throw err;
});

child.on("close", (code) => process.exit(code ?? 1));
