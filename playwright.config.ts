import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.E2E_BASE_URL || 'http://localhost:19006';

const cfg: any = {
  testDir: 'e2e',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  retries: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  // webServer is configured conditionally below to avoid Windows-specific Expo/Metro issues
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
};

if (process.env.E2E_START_COMMAND) {
  cfg.webServer = {
    command: process.env.E2E_START_COMMAND,
    url: baseURL,
    reuseExistingServer: true,
    timeout: 180_000,
    stderr: 'pipe',
    stdout: 'pipe',
  };
}

export default defineConfig(cfg);


