import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 180_000,
  use: { baseURL: 'http://127.0.0.1:8778' },
  webServer: {
    command:
      'python3 -m http.server 8778 --bind 127.0.0.1 --directory ../docs/_build/html',
    url: 'http://127.0.0.1:8778',
    reuseExistingServer: false,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
