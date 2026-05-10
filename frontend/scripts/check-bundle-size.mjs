#!/usr/bin/env node
/**
 * Bundle-size budget check (Sprint 15, ADR 0013).
 */
import { readdir, readFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ASSETS_DIR = join(__dirname, "..", "dist", "assets");
const BUDGET_KB = 100;

let failed = false;
let entries;
try {
  entries = await readdir(ASSETS_DIR);
} catch {
  console.error("[bundle-size] dist/assets/ not found. Run 'npm run build' first.");
  process.exit(2);
}
const jsChunks = entries.filter((f) => f.endsWith(".js"));
if (jsChunks.length === 0) {
  console.error("[bundle-size] no JS chunks found");
  process.exit(2);
}
console.log(`[bundle-size] budget: ${BUDGET_KB} kB gzipped per chunk`);
for (const file of jsChunks) {
  const buf = await readFile(join(ASSETS_DIR, file));
  const gz = gzipSync(buf, { level: 9 });
  const kb = gz.length / 1024;
  const status = kb <= BUDGET_KB ? "OK " : "FAIL";
  console.log(`  ${status}  ${file}  ${kb.toFixed(2)} kB gz  (raw ${(buf.length / 1024).toFixed(2)} kB)`);
  if (kb > BUDGET_KB) failed = true;
}
if (failed) {
  console.error("[bundle-size] FAIL: at least one chunk exceeded the budget.");
  process.exit(1);
}
console.log("[bundle-size] all chunks within budget");
