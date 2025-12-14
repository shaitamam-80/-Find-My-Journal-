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
  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/')

    // Should be redirected to login page
    await expect(page).toHaveURL(/.*login/)
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible()
  })

  test('should show login form elements', async ({ page }) => {
    await page.goto('/login')

    await expect(page.getByLabel(/email/i)).toBeVisible()
    await expect(page.getByLabel(/password/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /sign up/i })).toBeVisible()
  })

  test('should login successfully and show search page', async ({ page }) => {
    await page.goto('/login')

    // Fill login form
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)

    // Click sign in
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for navigation to search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Verify search page elements
    await expect(page.getByText('Find My Journal')).toBeVisible()
    await expect(page.getByLabel(/article title/i)).toBeVisible()
    await expect(page.getByLabel(/abstract/i)).toBeVisible()
    await expect(page.getByText(TEST_USER.email)).toBeVisible()
  })

  test('should show validation errors for empty form', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)
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

  test('should perform search and show results', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)
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
    await expect(page.getByRole('button', { name: /searching/i })).toBeVisible()

    // Wait for results (timeout 30s for API call)
    await expect(page.getByRole('heading', { name: /found \d+ journals/i })).toBeVisible({ timeout: 30000 })
  })

  test('should show search limit indicator', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Should show search limit indicator in header (either "Searches today: X/Y" for free users or "Unlimited searches" for paid/admin)
    // Use .first() to avoid strict mode violation when multiple elements match
    const searchesToday = page.getByText(/searches today:/i).first()
    const unlimitedSearches = page.getByText(/unlimited searches/i).first()

    // Wait for either indicator to appear
    await expect(searchesToday.or(unlimitedSearches)).toBeVisible({ timeout: 5000 })
  })

  test('should sign out successfully', async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.getByLabel(/email/i).fill(TEST_USER.email)
    await page.getByLabel(/password/i).fill(TEST_USER.password)
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for search page
    await expect(page).toHaveURL(/.*search/, { timeout: 10000 })

    // Click sign out
    await page.getByRole('button', { name: /sign out/i }).click()

    // Should redirect to login
    await expect(page).toHaveURL(/.*login/)
  })
})
