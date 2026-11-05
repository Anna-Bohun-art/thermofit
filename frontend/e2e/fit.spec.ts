import { expect, test } from '@playwright/test'

test('DSC demo: fit shows Tm close to 45.3 °C and a simulated-data warning', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Load simulated demo' }).click()
  await expect(page.getByText('Simulated demo data – not a measurement.')).toBeVisible()
  const tmRow = page.getByRole('row', { name: /Melting temperature/ })
  await expect(tmRow).toBeVisible()
  const tm = Number((await tmRow.locator('td').nth(1).innerText()).trim())
  expect(tm).toBeGreaterThan(45.0)
  expect(tm).toBeLessThan(45.6)
  await expect(page.getByText(/R² = 0\.99/)).toBeVisible()
  await expect(page.getByTestId('summary')).toContainText('half unfolded')
  await page.screenshot({ path: 'e2e/screenshot-dsc.png', fullPage: true })
})

test('irreversible demo works', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Analysis').selectOption('dsc_irreversible')
  await page.getByRole('button', { name: 'Load simulated demo' }).click()
  await expect(page.getByRole('row', { name: /Energy barrier/ })).toBeVisible()
})

test('bad upload shows a readable error, not a crash', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('CSV file').setInputFiles({
    name: 'bad.csv', mimeType: 'text/csv', buffer: Buffer.from('a,b\n1,2\n3,4\n'),
  })
  await page.getByRole('button', { name: 'Fit', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('at least 15 data points')
})

test('thesis curve (Zn-AK, digitized Fig. 6) reproduces the published Tm and shows its source', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Load thesis curve: Zn-AK' }).click()
  await expect(page.getByTestId('banner')).toContainText('Digitized from Fig. 6')
  const tmRow = page.getByRole('row', { name: /Melting temperature/ })
  await expect(tmRow).toBeVisible()
  const tm = Number((await tmRow.locator('td').nth(1).innerText()).trim())
  expect(Math.abs(tm - 45.3)).toBeLessThan(0.15)
  await page.screenshot({ path: 'e2e/screenshot-thesis-zn.png', fullPage: true })
})

test('thesis curve (Fe-AK 1 K/min) sets the scan rate and reproduces the published T*', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Analysis').selectOption('dsc_irreversible')
  await page.getByRole('button', { name: 'Thesis curve: Fe-AK 1 K/min' }).click()
  await expect(page.getByTestId('banner')).toContainText('Fig. 7')
  const row = page.getByRole('row', { name: /Temperature of fast unfolding/ })
  await expect(row).toBeVisible()
  const tstar = Number((await row.locator('td').nth(1).innerText()).trim())
  expect(Math.abs(tstar - 43.1)).toBeLessThan(0.2)
  await page.screenshot({ path: 'e2e/screenshot-thesis-fe.png', fullPage: true })
})
