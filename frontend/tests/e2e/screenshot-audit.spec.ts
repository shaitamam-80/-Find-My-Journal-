import { test, expect } from '@playwright/test'

// Test credentials
const TEST_USER = {
  email: 'find_test_user@gmail.com',
  password: 'V$f92!B%jPpH@&G',
}

const SAMPLE_RESEARCH = {
  title: 'Exploring the Roots of Kindness: Validating the Social-Emotional Responding Task (SERT) for Infants and Toddlers',
  abstract: `A total of 179 caregivers in Leipzig, Germany completed the adapted SERT, as well as measures for the purpose of validating the adapted SERT, including social-emotional and behavioral problems (BITSEA; Briggs-Gowan & Carter 2007), temperament (IBQ/ECBQ; Putnam et al., 2013, 2006), and conscience development (Kochanska et al., 1994). Internal consistency was found across all empathy for others, empathy for the self, and emotion regulation precursor constructs.`,
  keywords: 'kindness, empathy, toddlerhood, infancy, social-emotional development',
}

test.describe('UI Audit Screenshots', () => {
  test('capture login page', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.screenshot({ path: 'screenshots/01-login-page.png', fullPage: true })
  })

  test('capture signup page', async ({ page }) => {
    await page.goto('/signup')
    await page.waitForLoadState('networkidle')
    await page.screenshot({ path: 'screenshots/02-signup-page.png', fullPage: true })
  })

  test('capture login with test user and search page', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')

    // Fill login form
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)

    await page.screenshot({ path: 'screenshots/03-login-filled.png', fullPage: true })

    // Click sign in
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for navigation to search page
    try {
      await expect(page).toHaveURL(/.*search/, { timeout: 15000 })
      await page.waitForLoadState('networkidle')
      await page.screenshot({ path: 'screenshots/04-search-page-empty.png', fullPage: true })
    } catch (e) {
      // If login fails, capture the error state
      await page.screenshot({ path: 'screenshots/04-login-error.png', fullPage: true })
      console.log('Login failed - captured error state')
    }
  })

  test('capture search with results', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    try {
      await expect(page).toHaveURL(/.*search/, { timeout: 15000 })
    } catch (e) {
      await page.screenshot({ path: 'screenshots/05-login-failed.png', fullPage: true })
      return
    }

    await page.waitForLoadState('networkidle')

    // Fill search form
    await page.getByLabel(/article title/i).fill(SAMPLE_RESEARCH.title)
    await page.getByLabel(/abstract/i).fill(SAMPLE_RESEARCH.abstract)
    await page.getByLabel(/keywords/i).fill(SAMPLE_RESEARCH.keywords)

    await page.screenshot({ path: 'screenshots/05-search-form-filled.png', fullPage: true })

    // Submit search
    await page.getByRole('button', { name: /find journals/i }).click()

    // Capture loading state
    await page.screenshot({ path: 'screenshots/06-search-loading.png', fullPage: true })

    // Wait for results
    try {
      await expect(page.getByText(/journals found/i)).toBeVisible({ timeout: 45000 })
      await page.waitForTimeout(1000) // Let animations complete
      await page.screenshot({ path: 'screenshots/07-search-results.png', fullPage: true })
    } catch (e) {
      await page.screenshot({ path: 'screenshots/07-search-timeout.png', fullPage: true })
      console.log('Search timed out')
    }
  })

  test('accessibility audit - color contrast and focus states', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')

    // Tab through elements to check focus states
    await page.keyboard.press('Tab')
    await page.screenshot({ path: 'screenshots/a11y-01-focus-email.png', fullPage: true })

    await page.keyboard.press('Tab')
    await page.screenshot({ path: 'screenshots/a11y-02-focus-password.png', fullPage: true })

    await page.keyboard.press('Tab')
    await page.screenshot({ path: 'screenshots/a11y-03-focus-button.png', fullPage: true })
  })

  test('mobile viewport - login', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.screenshot({ path: 'screenshots/mobile-01-login.png', fullPage: true })
  })

  test('mobile viewport - search', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/login')

    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    try {
      await expect(page).toHaveURL(/.*search/, { timeout: 15000 })
      await page.waitForLoadState('networkidle')
      await page.screenshot({ path: 'screenshots/mobile-02-search.png', fullPage: true })
    } catch (e) {
      await page.screenshot({ path: 'screenshots/mobile-02-login-failed.png', fullPage: true })
    }
  })
})
