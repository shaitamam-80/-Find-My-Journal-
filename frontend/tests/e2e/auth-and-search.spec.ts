import { test, expect } from '@playwright/test'

// Test credentials - User is set to 'paid' tier with unlimited searches
const TEST_USER = {
  email: 'find_test_user@gmail.com',
  password: 'V$f92!B%jPpH@&G',
}

// Sample research data for testing
const SAMPLE_RESEARCH = {
  title: 'Machine Learning Applications in Medical Diagnosis',
  abstract: `This study investigates the application of deep learning algorithms for early detection
of cancer in medical imaging. We developed a convolutional neural network model trained on
over 50,000 CT scan images. The model achieved 94% accuracy in identifying early-stage tumors,
significantly outperforming traditional diagnostic methods. Our findings suggest that AI-assisted
diagnosis can improve patient outcomes by enabling earlier intervention. The implications for
healthcare systems are substantial, potentially reducing diagnostic costs while improving accuracy.`,
  keywords: 'machine learning, medical imaging, cancer detection',
}

test.describe('Find My Journal E2E Tests', () => {
  // Note: Test user (find_test_user@gmail.com) is set to 'paid' tier with unlimited searches
  // No need to reset credits before tests
  test('should show landing page when not authenticated', async ({ page }) => {
    await page.goto('/')

    // Landing page should be visible (not redirected to login)
    // The landing page has "FindMyJournal" logo and Sign Up/Log In links
    await expect(page.getByText('FindMyJournal').first()).toBeVisible()
    await expect(page.getByRole('link', { name: /sign up/i }).first()).toBeVisible()
  })

  test('should show login form elements', async ({ page }) => {
    await page.goto('/login')

    await expect(page.getByPlaceholder('you@example.com')).toBeVisible()
    await expect(page.getByPlaceholder('Enter your password')).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /sign up now/i })).toBeVisible()
  })

  test('should login successfully and show search page', async ({ page }) => {
    await page.goto('/login')

    // Fill login form
    await page.getByPlaceholder('you@example.com').fill(TEST_USER.email)
    await page.getByPlaceholder('Enter your password').fill(TEST_USER.password)

    // Click sign in
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for navigation to search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Verify search page elements
    await expect(page.getByText('FindMyJournal')).toBeVisible()
    await expect(page.getByLabel(/article title/i)).toBeVisible()
    await expect(page.getByLabel(/abstract/i)).toBeVisible()
    await expect(page.getByText(TEST_USER.email)).toBeVisible()
  })

  test('should show validation errors for empty form', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.getByPlaceholder('you@example.com').fill(TEST_USER.email)
    await page.getByPlaceholder('Enter your password').fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Try to submit with short title
    await page.getByLabel(/article title/i).fill('abc')
    await page.getByLabel(/abstract/i).fill('Short abstract')
    await page.getByRole('button', { name: /find journals/i }).click()

    // Should show validation error
    await expect(page.getByText(/title must be at least 5 characters/i)).toBeVisible()
  })

  test('should perform search and show results', async ({ page }, testInfo) => {
    testInfo.setTimeout(90000) // 90 second timeout for slow API calls
    // Login first
    await page.goto('/login')
    await page.getByPlaceholder('you@example.com').fill(TEST_USER.email)
    await page.getByPlaceholder('Enter your password').fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Fill search form
    await page.getByLabel(/article title/i).fill(SAMPLE_RESEARCH.title)
    await page.getByLabel(/abstract/i).fill(SAMPLE_RESEARCH.abstract)
    await page.getByLabel(/keywords/i).fill(SAMPLE_RESEARCH.keywords)

    // Submit search
    await page.getByRole('button', { name: /find journals/i }).click()

    // Wait for loading to complete (button shows "Searching...")
    await expect(page.getByText(/Searching\.\.\./i)).toBeVisible()

    // Wait for results - look for "Top-Tier Journals" heading which indicates results loaded
    await expect(page.getByRole('heading', { name: /top-tier journals/i })).toBeVisible({ timeout: 60000 })
  })

  test('should show search limit indicator', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.getByPlaceholder('you@example.com').fill(TEST_USER.email)
    await page.getByPlaceholder('Enter your password').fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Wait for page to fully load (limits are fetched asynchronously)
    await page.waitForLoadState('networkidle')

    // Should show search limit indicator in header (either "Searches today: X/Y" for free users or "Unlimited" for paid/admin)
    // Use .first() to avoid strict mode violation when multiple elements match
    const searchesToday = page.getByText(/searches today:/i).first()
    const unlimitedSearches = page.getByText(/unlimited/i).first()

    // Wait for either indicator to appear (increased timeout for async limit fetch)
    await expect(searchesToday.or(unlimitedSearches)).toBeVisible({ timeout: 10000 })
  })

  test('should sign out successfully', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.getByPlaceholder('you@example.com').fill(TEST_USER.email)
    await page.getByPlaceholder('Enter your password').fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Click sign out
    await page.getByRole('button', { name: /sign out/i }).click()

    // Should redirect to login
    await expect(page).toHaveURL(/.*login/)
  })
})
