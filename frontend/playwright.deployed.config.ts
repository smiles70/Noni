import { defineConfig, devices } from "@playwright/test";

// Post-deploy smoke runs against a live environment. This config refuses
// to run without an explicit target so a bare `playwright test` can never
// accidentally aim at production. It also restricts the suite to
// `@smoke`-tagged tests, which are required to be read-only and
// unauthenticated — deployed environments must never see a purchase,
// entitlement, or form mutation from the test suite.
const baseURL = process.env.PLAYWRIGHT_TEST_BASE_URL;
if (!baseURL) {
  throw new Error(
    "PLAYWRIGHT_TEST_BASE_URL is required (e.g. https://staging.noni-web.pages.dev)",
  );
}
if (!/^https:\/\//.test(baseURL)) {
  throw new Error(
    `PLAYWRIGHT_TEST_BASE_URL must be https for deployed runs, got: ${baseURL}`,
  );
}

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: false,
  forbidOnly: true,
  retries: 2,
  reporter: [["list"], ["html", { open: "never" }]],
  grep: /@smoke/,
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile-pixel", use: { ...devices["Pixel 5"] } },
    { name: "mobile-iphone", use: { ...devices["iPhone 13"] } },
  ],
});
