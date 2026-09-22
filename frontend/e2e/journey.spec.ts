import { expect, test } from '@playwright/test'
import path from 'node:path'

const FIXTURES = path.resolve(import.meta.dirname, '../../tests/fixtures')
const POSITIVE = path.join(FIXTURES, 'pdf/pdf.text.low_contrast/positive.pdf')
const NEGATIVE = path.join(FIXTURES, 'pdf/pdf.text.low_contrast/negative.pdf')

test('upload a hidden-text resume, read the verdict, find it in history', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Scan a document' })).toBeVisible()

  await page.getByLabel('File', { exact: true }).setInputFiles(POSITIVE)
  await page.getByLabel('Tier').selectOption('fast')
  await page.getByRole('button', { name: 'Scan' }).click()

  await expect(page).toHaveURL(/\/scans\/[A-Za-z0-9_-]+$/)
  await expect(page.getByTestId('verdict')).toContainText('malicious')
  await expect(page.getByTestId('findings').locator('li').first()).toContainText(
    'pdf.text.low_contrast',
  )
  await expect(page.getByText('paperglass show', { exact: false }).first()).toBeVisible()
  const reportUrl = page.url()

  // The share link works in a browser with no session cookie.
  const anonymous = await page.context().browser()?.newContext()
  if (anonymous) {
    const other = await anonymous.newPage()
    await other.goto(reportUrl)
    await expect(other.getByTestId('verdict')).toContainText('malicious')
    await anonymous.close()
  }

  await page.getByRole('link', { name: 'History' }).click()
  const rows = page.getByTestId('history').locator('tbody tr')
  await expect(rows.first()).toContainText('positive.pdf')
  await expect(rows.first()).toContainText('malicious')
  await rows.first().getByRole('link').click()
  await expect(page).toHaveURL(reportUrl)
})

test('a clean document reads clean and the fingerprint runs on re-upload', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('File', { exact: true }).setInputFiles(NEGATIVE)
  await page.getByRole('button', { name: 'Scan' }).click()
  await expect(page.getByTestId('verdict')).toContainText('clean')
  await expect(page.getByText('No findings.')).toBeVisible()

  const fingerprint = page.getByRole('region', { name: 'Fingerprint' })
  await fingerprint.getByLabel('File', { exact: true }).setInputFiles(NEGATIVE)
  await fingerprint.getByRole('button', { name: 'Fingerprint' }).click()
  await expect(page.getByTestId('fingerprint')).toBeVisible()
})

test('the wrong file is refused for a fingerprint with a sentence', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('File', { exact: true }).setInputFiles(POSITIVE)
  await page.getByRole('button', { name: 'Scan' }).click()
  await expect(page.getByTestId('verdict')).toContainText('malicious')

  const fingerprint = page.getByRole('region', { name: 'Fingerprint' })
  await fingerprint.getByLabel('File', { exact: true }).setInputFiles(NEGATIVE)
  await fingerprint.getByRole('button', { name: 'Fingerprint' }).click()
  await expect(fingerprint.getByRole('alert')).toBeVisible()
})

test('techniques and about load; an unknown report explains itself', async ({ page }) => {
  await page.goto('/techniques')
  await expect(page.getByTestId('technique-count')).toContainText('18 techniques')
  await expect(page.getByRole('heading', { name: 'pdf', level: 2 })).toBeVisible()

  await page.goto('/about')
  await expect(page.getByRole('heading', { name: 'About Paperglass' })).toBeVisible()

  await page.goto('/scans/does-not-exist')
  await expect(page.getByRole('alert')).toContainText('does not exist or has expired')
})

test('no page makes a request outside its own origin', async ({ page }) => {
  const foreign: string[] = []
  page.on('request', (request) => {
    const url = new URL(request.url())
    if (url.hostname !== 'localhost' && url.hostname !== '127.0.0.1') foreign.push(request.url())
  })
  await page.goto('/')
  await page.goto('/techniques')
  await expect(page.getByTestId('technique-count')).toBeVisible()
  expect(foreign).toEqual([])
})
