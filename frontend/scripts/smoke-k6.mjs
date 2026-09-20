#!/usr/bin/env node
/**
 * Smoke gate — k6 load / latency gate on production.
 *
 * Expects `k6` binary to be installed locally:
 *   https://grafana.com/docs/k6/latest/set-up/install-k6/
 *
 * Usage:
 *   npm run smoke:k6
 *   SMOKE_URL=https://www.mynaani.com npm run smoke:k6
 */
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

const binary = process.env.K6_PATH || "k6";

const child = spawn(
  binary,
  ["run", resolve(__dirname, "smoke-k6.js")],
  { stdio: "inherit", shell: true, env: { ...process.env } },
);

child.on("error", (err) => {
  if (err.code === "ENOENT") {
    console.error(
      `k6 binary not found at ${binary}. Set K6_PATH or install from https://grafana.com/docs/k6/latest/set-up/install-k6/`,
    );
    process.exit(1);
  }
  throw err;
});

child.on("close", (code) => process.exit(code ?? 1));
