import { defineConfig, devices } from '@playwright/test'

/**
 * The journey runs against the real backend (SQLite, in-memory scans) and the Vite dev server.
 * Three widths: phone, tablet, desktop. CI sets PAPERGLASS_E2E_BASE_URL to reuse a running stack.
 */
const baseURL = process.env.PAPERGLASS_E2E_BASE_URL ?? 'http://localhost:5173'
const external = process.env.PAPERGLASS_E2E_BASE_URL !== undefined

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: process.env.CI !== undefined,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  timeout: 60_000,
  use: {
    baseURL,
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'phone', use: { ...devices['Desktop Chrome'], viewport: { width: 375, height: 812 } } },
    { name: 'tablet', use: { ...devices['Desktop Chrome'], viewport: { width: 768, height: 1024 } } },
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } } },
  ],
  webServer: external
    ? undefined
    : [
        {
          command:
            'uv run --directory ../backend uvicorn app.main:app --host 127.0.0.1 --port 8000',
          url: 'http://127.0.0.1:8000/healthz',
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: {
            PAPERGLASS_DATABASE_URL: 'sqlite+pysqlite:///./.e2e.sqlite3',
            PAPERGLASS_SANDBOX_POOL: '1',
          },
        },
        {
          command: 'npm run dev',
          url: 'http://localhost:5173',
          reuseExistingServer: !process.env.CI,
          timeout: 60_000,
        },
      ],
})
