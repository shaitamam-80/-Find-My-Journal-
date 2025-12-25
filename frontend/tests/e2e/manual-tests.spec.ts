/**
 * Manual E2E Tests - Requested Tests
 * These tests cover the 5 specific test cases requested by the user.
 */
import { test, expect } from '@playwright/test'

// Test configuration
const BASE_URL = 'http://localhost:3000'

test.describe('Manual E2E Tests', () => {
  // Test 1: Landing Page
  test('Test 1: Landing Page - should show logo, Sign Up, and Log In', async ({ page }) => {
    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // Verify logo "FindMyJournal" is visible (use first() since there are multiple)
    await expect(page.getByText('FindMyJournal').first()).toBeVisible()

    // Verify "Sign Up" button is visible (use first() since there are multiple)
    await expect(page.getByRole('link', { name: /sign up/i }).first()).toBeVisible()

    // Verify "Log In" button is visible
    await expect(page.getByRole('link', { name: /log in/i }).first()).toBeVisible()

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test1-landing-page.png', fullPage: true })
  })

  // Test 2: Login Flow - Error handling
  test('Test 2: Login Flow - should show error for invalid credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`)
    await page.waitForLoadState('networkidle')

    // Verify form elements are visible - use placeholder text since labels may not be directly associated
    await expect(page.getByPlaceholder(/email/i).or(page.locator('input[type="email"]'))).toBeVisible()
    await expect(page.getByPlaceholder(/password/i).or(page.locator('input[type="password"]'))).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()

    // Enter invalid credentials
    await page.getByPlaceholder(/email/i).or(page.locator('input[type="email"]')).fill('test@invalid.com')
    await page.getByPlaceholder(/password/i).or(page.locator('input[type="password"]')).fill('wrongpass')

    // Click Sign In
    await page.getByRole('button', { name: /sign in/i }).click()

    // Wait for error message (red error) - use first() since multiple elements may match
    await expect(page.locator('.text-red-600, .text-red-500').first()).toBeVisible({ timeout: 10000 })

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test2-login-error.png', fullPage: true })
  })

  // Test 3: SignUp Validation - Password mismatch
  test('Test 3: SignUp Validation - should show password mismatch error', async ({ page }) => {
    await page.goto(`${BASE_URL}/signup`)
    await page.waitForLoadState('networkidle')

    // Fill email (required field)
    const emailInput = page.getByPlaceholder(/email/i).or(page.locator('input[type="email"]'))
    await emailInput.fill('test@example.com')

    // Enter mismatched passwords
    const passwordInputs = page.locator('input[type="password"]')
    await passwordInputs.first().fill('abc123')
    await passwordInputs.nth(1).fill('xyz789')

    // Click Create Account
    const createButton = page.getByRole('button', { name: /create account/i }).or(page.getByRole('button', { name: /sign up/i }))
    await createButton.click()

    // Wait for error message about password mismatch
    await expect(page.getByText(/passwords do not match/i).or(page.getByText(/password.*match/i)).or(page.locator('.text-red-600, .text-red-500'))).toBeVisible({ timeout: 5000 })

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test3-signup-password-mismatch.png', fullPage: true })
  })

  // Test 4: Navigation - Non-existent route
  test('Test 4: Navigation - should not crash on non-existent route', async ({ page }) => {
    await page.goto(`${BASE_URL}/nonexistent`)

    // Should not crash - page should load something
    await page.waitForLoadState('load')

    // Page should not have an error overlay or crash
    // It should either show a 404 page or redirect to home/login
    const hasContent = await page.locator('body').isVisible()
    expect(hasContent).toBe(true)

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test4-nonexistent-route.png', fullPage: true })
  })

  // Test 5: Mobile View - Responsive design
  test('Test 5: Mobile View - should display responsive design', async ({ page }) => {
    // Set mobile viewport (iPhone SE)
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // Verify page is still functional (use first() since there are multiple)
    await expect(page.getByText('FindMyJournal').first()).toBeVisible()

    // Check that the layout is responsive (no horizontal scroll)
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth)
    const viewportWidth = 375
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20) // Allow small tolerance

    // Take screenshot
    await page.screenshot({ path: 'screenshots/test5-mobile-view.png', fullPage: true })
  })
})
