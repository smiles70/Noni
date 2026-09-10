#!/usr/bin/env node
/**
 * Smoke gate — pa11y accessibility scan on critical pages.
 *
 * Expects `pa11y` to be available in the dev environment.
 * Install with: npm add -D pa11y
 *
 * Usage:
 *   npm run smoke:pa11y
 *   SMOKE_URL=https://www.mynaani.com npm run smoke:pa11y
 */
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const url = process.env.SMOKE_URL || "https://www.mynaani.com";
const standard = process.env.PA11Y_STANDARD || "WCAG2AA";

const child = spawn(
  "pa11y",
  [
    url,
    `--standard=${standard}`,
    "--reporter=json",
    `--config=${resolve(__dirname, "../pa11y.json")}`,
  ],
  { stdio: "inherit", shell: true, cwd: __dirname },
);

child.on("error", (err) => {
  if (err.code === "ENOENT") {
    console.error("pa11y is not installed. Run: npm add -D pa11y");
    process.exit(1);
  }
  throw err;
});

child.on("close", (code) => process.exit(code ?? 1));
