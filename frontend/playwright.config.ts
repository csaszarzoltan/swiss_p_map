/* eslint-disable @typescript-eslint/no-explicit-any */
import { defineConfig, devices } from "@playwright/test";

const FE_PORT = Number(process.env.FE_PORT ?? 3410);
const BE_PORT = Number(process.env.BE_PORT ?? 8310);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  timeout: 25_000,
  expect: { timeout: 8_000 },
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://localhost:${FE_PORT}`,
    trace: "off",
    screenshot: "off",
  },
  webServer: process.env.CI
    ? [
        {
          command: `python -m uvicorn src.main:app --port ${BE_PORT} --host 127.0.0.1`,
          url: `http://127.0.0.1:${BE_PORT}/health`,
          reuseExistingServer: true,
          cwd: "..",
          timeout: 20_000,
        },
        {
          command: `npm run dev -- -p ${FE_PORT}`,
          url: `http://127.0.0.1:${FE_PORT}/de`,
          reuseExistingServer: true,
          timeout: 40_000,
        },
      ]
    : undefined,
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
