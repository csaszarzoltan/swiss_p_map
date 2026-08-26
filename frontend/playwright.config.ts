/* eslint-disable @typescript-eslint/no-explicit-any */
import { defineConfig, devices } from "@playwright/test";

const FE_PORT = Number(process.env.FE_PORT ?? 3310);
const BE_PORT = Number(process.env.BE_PORT ?? 8310);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  timeout: 25_000,
  expect: { timeout: 8_000 },
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${FE_PORT}`,
    trace: "off",
    screenshot: "off",
  },
  webServer: [
    {
      command: `bash -c 'SWISSPM_CORS_ORIGINS=http://localhost:${FE_PORT},http://127.0.0.1:${FE_PORT} ../.venv/bin/python -m uvicorn src.main:app --port ${BE_PORT} --host 127.0.0.1'`,
      url: `http://127.0.0.1:${BE_PORT}/health`,
      reuseExistingServer: true,
      cwd: "..",
      timeout: 20_000,
    },
    {
      command: `bash -c 'NEXT_PUBLIC_API_URL=http://127.0.0.1:${BE_PORT} npm run dev -- -p ${FE_PORT}'`,
      url: `http://127.0.0.1:${FE_PORT}/`,
      reuseExistingServer: true,
      timeout: 40_000,
    },
  ],
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
