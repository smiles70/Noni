/**
 * Vitest configuration.
 *
 * Scope: src/** unit tests only. The e2e/ directory belongs to Playwright
 * (a different runner with an incompatible test API) and must not be
 * picked up here.
 */
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
    environment: "jsdom",
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      thresholds: {
        // Rack 3.3 baseline; raise toward 85/75/80 as backfill continues.
        lines: 83,
        functions: 72,
        branches: 69,
        statements: 82,
      },
    },
  },
});
