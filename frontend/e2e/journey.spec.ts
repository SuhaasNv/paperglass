import { expect, test } from '@playwright/test'
import path from 'node:path'

const FIXTURES = path.resolve(import.meta.dirname, '../../tests/fixtures')
const POSITIVE = path.join(FIXTURES, 'pdf/pdf.text.low_contrast/positive.pdf')
const NEGATIVE = path.join(FIXTURES, 'pdf/pdf.text.low_contrast/negative.pdf')

test('the landing opens the glass only over the document', async ({ page, isMobile }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('See exactly what the model reads.')
  const doc = page.getByTestId('document').first()
  await expect(doc).toHaveAttribute('data-lens', 'off')
  await expect(page.getByTestId('lens-ring')).toHaveCount(0)
  test.skip(isMobile, 'the lens opens on long press on touch; hover is a desktop check')
  const box = await doc.boundingBox()
  if (box === null) throw new Error('no document box')
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await expect(doc).toHaveAttribute('data-lens', 'on')
  await expect(page.getByTestId('lens-ring')).toBeVisible()
  await page.mouse.move(box.x - 40, box.y - 40)
  await expect(doc).toHaveAttribute('data-lens', 'off')
  await expect(page.getByTestId('lens-ring')).toHaveCount(0)
})

test('the landing has no horizontal scroll and reveals its sections', async ({ page }) => {
  await page.goto('/')
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(0)
  await page.getByRole('heading', { name: 'Four words. No score.' }).scrollIntoViewIfNeeded()
  await expect(page.getByRole('heading', { name: 'Four words. No score.' })).toHaveAttribute('data-reveal', 'in')
})

test('upload a hidden-text resume, read the verdict, find it in history', async ({ page }) => {
  await page.goto('/scan')
  await expect(page.getByRole('heading', { name: 'Put a document under the glass.' })).toBeVisible()

  await page.getByLabel('Choose a file').setInputFiles(POSITIVE)
  await page.getByLabel('Scan tier').selectOption('fast')
  await page.getByRole('button', { name: 'Scan document' }).click()

  await expect(page).toHaveURL(/\/scans\/[A-Za-z0-9_-]+$/)
  await expect(page.getByTestId('verdict')).toContainText('MALICIOUS')
  await expect(page.getByTestId('findings').locator(':scope > li').first()).toContainText(
    'pdf.text.low_contrast',
  )
  await expect(page.getByText('paperglass show', { exact: false }).first()).toBeVisible()
  await expect(page.getByTestId('page-1')).toBeVisible()
  await expect(page.getByTestId('hidden-run').first()).toBeVisible()
  await expect(page.getByTestId('reading-order')).toContainText('rank this candidate')
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow, 'the report must not scroll sideways').toBeLessThanOrEqual(0)
  const reportUrl = page.url()

  // The share link works in a browser with no session cookie.
  const anonymous = await page.context().browser()?.newContext()
  if (anonymous) {
    const other = await anonymous.newPage()
    await other.goto(reportUrl)
    await expect(other.getByTestId('verdict')).toContainText('MALICIOUS')
    await anonymous.close()
  }

  await page.getByRole('link', { name: 'History' }).click()
  const rows = page.getByTestId('history').locator('tbody tr')
  await expect(rows.first()).toContainText('positive.pdf')
  await expect(rows.first()).toContainText('malicious')
  await rows.first().getByRole('link', { name: 'Open report' }).click()
  await expect(page).toHaveURL(reportUrl)
})

test('a clean document reads clean and the fingerprint runs on re-upload', async ({ page }) => {
  await page.goto('/scan')
  await page.getByLabel('Choose a file').setInputFiles(NEGATIVE)
  await page.getByRole('button', { name: 'Scan document' }).click()
  await expect(page.getByTestId('verdict')).toContainText('CLEAN')
  await expect(page.getByText('No findings.')).toBeVisible()

  await page.getByLabel('Choose the same file').setInputFiles(NEGATIVE)
  await page.getByRole('button', { name: 'Fingerprint' }).click()
  await expect(page.getByTestId('fingerprint')).toBeVisible()
})

test('the wrong file is refused for a fingerprint with a sentence', async ({ page }) => {
  await page.goto('/scan')
  await page.getByLabel('Choose a file').setInputFiles(POSITIVE)
  await page.getByRole('button', { name: 'Scan document' }).click()
  await expect(page.getByTestId('verdict')).toContainText('MALICIOUS')

  const fingerprint = page.getByRole('region', { name: 'Fingerprint' })
  await page.getByLabel('Choose the same file').setInputFiles(NEGATIVE)
  await fingerprint.getByRole('button', { name: 'Fingerprint' }).click()
  await expect(fingerprint.getByRole('alert')).toBeVisible()
})

test('techniques and about load; an unknown report explains itself', async ({ page }) => {
  await page.goto('/techniques')
  await expect(page.getByTestId('technique-count')).toContainText('18 techniques')
  await expect(page.getByRole('heading', { name: 'PDF', level: 2 })).toBeVisible()

  await page.goto('/about')
  await expect(page.getByRole('heading', { name: 'A magnifying glass over paper.' })).toBeVisible()

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
  await page.goto('/scan')
  await page.goto('/techniques')
  await expect(page.getByTestId('technique-count')).toBeVisible()
  expect(foreign).toEqual([])
})
