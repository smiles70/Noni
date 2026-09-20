import { defineConfig, devices } from "@playwright/test";

const isCI = !!process.env.CI;
// When set, the suite runs against a deployed environment instead of the
// local Vite dev server, and the webServer block is skipped entirely.
const deployedBaseURL = process.env.PLAYWRIGHT_TEST_BASE_URL;

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  reporter: isCI ? [["list"], ["html", { open: "never" }]] : [["list"]],
  use: {
    baseURL: deployedBaseURL ?? "http://127.0.0.1:5173",
    trace: isCI ? "retain-on-failure" : "off",
    screenshot: isCI ? "only-on-failure" : "off",
  },
  webServer: deployedBaseURL
    ? undefined
    : {
        command:
          "VITE_API_BASE_URL=https://noni-api-production.up.railway.app npm run dev",
        url: "http://127.0.0.1:5173",
        reuseExistingServer: !isCI,
        timeout: 60_000,
        env: {
          VITE_API_BASE_URL: "https://noni-api-production.up.railway.app",
        },
      },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile-pixel", use: { ...devices["Pixel 5"] } },
    { name: "mobile-iphone", use: { ...devices["iPhone 13"] } },
  ],
});
