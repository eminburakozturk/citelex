import { existsSync } from "node:fs";
import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

const WIN_PYTHON = "C:\\Users\\Burak\\anaconda3\\envs\\citelex\\python.exe";
const pythonCmd = existsSync(WIN_PYTHON) ? `"${WIN_PYTHON}"` : "python3";
const outDir = path.join(__dirname, "out");
const PORT = 3123;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: `${pythonCmd} -m http.server ${PORT} --bind 127.0.0.1 --directory "${outDir}"`,
    url: `http://127.0.0.1:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
