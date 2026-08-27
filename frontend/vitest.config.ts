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
        lines: 1,
        functions: 1,
        branches: 1,
        statements: 1,
      },
    },
  },
});
