/**
 * Authenticated E2E Tests
 * Tests that require a real logged-in user.
 * Credentials loaded from .env.test file.
 */
import { test, expect } from '@playwright/test'
import * as dotenv from 'dotenv'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

// ESM-compatible __dirname
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Load test credentials
dotenv.config({ path: resolve(__dirname, '../../.env.test') })

const BASE_URL = 'http://localhost:3000'
const TEST_EMAIL = process.env.TEST_USER_EMAIL || ''
const TEST_PASSWORD = process.env.TEST_USER_PASSWORD || ''

// Helper function to login
async function login(page: import('@playwright/test').Page) {
  await page.goto(`${BASE_URL}/login`)
  await page.waitForLoadState('networkidle')

  // Fill login form
  await page.locator('input[type="email"]').fill(TEST_EMAIL)
  await page.locator('input[type="password"]').fill(TEST_PASSWORD)

  // Click Sign In
  await page.getByRole('button', { name: /sign in/i }).click()

  // Wait for redirect to search page
  await page.waitForURL(/\/(search|dashboard)/, { timeout: 15000 })
}

test.describe('Authenticated User Tests', () => {
  // Skip all tests if credentials are not configured
  test.beforeAll(() => {
    if (!TEST_EMAIL || !TEST_PASSWORD) {
      test.skip()
    }
  })

  test('Test 6: Successful Login - should login and redirect to search', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`)
    await page.waitForLoadState('networkidle')

    // Fill login form
    await page.locator('input[type="email"]').fill(TEST_EMAIL)
    await page.locator('input[type="password"]').fill(TEST_PASSWORD)

    // Take screenshot before login
    await page.screenshot({ path: 'screenshots/test6-login-form-filled.png' })

    // Click Sign In
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for successful redirect
    await page.waitForURL(/\/(search|dashboard)/, { timeout: 15000 })

    // Verify user is logged in - should see sign out button
    await expect(page.getByRole('button', { name: /sign out/i }).first()).toBeVisible({ timeout: 5000 })

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test6-login-success.png', fullPage: true })
  })

  test('Test 7: Dashboard Page - should display user stats', async ({ page }) => {
    await login(page)

    // Navigate to dashboard
    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // Wait for dashboard to load
    await expect(page.getByText(/dashboard/i).first()).toBeVisible({ timeout: 10000 })

    // Check for stats elements
    await expect(page.getByText(/searches/i).first()).toBeVisible()

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test7-dashboard.png', fullPage: true })
  })

  test('Test 8: Search Page - should display search form', async ({ page }) => {
    await login(page)

    // Navigate to search
    await page.goto(`${BASE_URL}/search`)
    await page.waitForLoadState('networkidle')

    // Verify search form elements
    await expect(page.getByRole('heading', { name: /find the right journal/i })).toBeVisible()

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test8-search-page.png', fullPage: true })
  })

  test('Test 9: Search Flow - should perform search and show results', async ({ page }) => {
    test.setTimeout(180000) // 3 minutes for slow API

    await login(page)
    await page.goto(`${BASE_URL}/search`)
    await page.waitForLoadState('networkidle')

    // Fill search form
    const titleInput = page.getByPlaceholder(/title/i).or(page.locator('input').first())
    const abstractInput = page.getByPlaceholder(/abstract/i).or(page.locator('textarea').first())

    if (await titleInput.isVisible()) {
      await titleInput.fill('Machine Learning in Healthcare')
    }

    if (await abstractInput.isVisible()) {
      await abstractInput.fill(
        'This study explores the application of machine learning algorithms in predicting patient outcomes. ' +
          'We analyze electronic health records using deep learning models to identify patterns in disease progression. ' +
          'Our results demonstrate significant improvements in early diagnosis accuracy compared to traditional methods.'
      )
    }

    // Take screenshot before search
    await page.screenshot({ path: 'screenshots/test9-search-form-filled.png', fullPage: true })

    // Click search button
    const searchButton = page.getByRole('button', { name: /search|find/i })
    await searchButton.click()

    // Wait for results (this can take a while due to OpenAlex API)
    // Look for Top-Tier Journals heading which indicates results loaded
    await expect(
      page.getByRole('heading', { name: /top-tier journals/i })
    ).toBeVisible({ timeout: 120000 })

    // Take screenshot of results
    await page.screenshot({ path: 'screenshots/test9-search-results.png', fullPage: true })
  })

  test('Test 10: Sign Out - should sign out and redirect to landing', async ({ page }) => {
    await login(page)

    // Find and click sign out button (use first() since there are multiple)
    await page.getByRole('button', { name: /sign out/i }).first().click()

    // Should redirect to landing or login page
    await page.waitForURL(/\/(login)?$/, { timeout: 10000 })

    // Wait for page to load
    await page.waitForLoadState('networkidle')

    // Verify logged out - should see login/signup links on landing page
    await expect(
      page.getByRole('link', { name: /log in/i }).first().or(page.getByRole('link', { name: /sign up/i }).first())
    ).toBeVisible({ timeout: 10000 })

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test10-signed-out.png', fullPage: true })
  })
})
