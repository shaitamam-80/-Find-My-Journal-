/**
 * Vitest test setup file.
 *
 * This file is automatically loaded before each test file.
 * Configure global test utilities and mocks here.
 */

import { afterEach, vi } from 'vitest'

// Mock window.matchMedia for components using media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver for components using lazy loading
const mockIntersectionObserver = vi.fn()
mockIntersectionObserver.mockReturnValue({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})
window.IntersectionObserver = mockIntersectionObserver as unknown as typeof IntersectionObserver

// Mock ResizeObserver
const mockResizeObserver = vi.fn()
mockResizeObserver.mockReturnValue({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})
window.ResizeObserver = mockResizeObserver as unknown as typeof ResizeObserver

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks()
})

// Mock import.meta.env
vi.stubGlobal('import.meta', {
  env: {
    VITE_SUPABASE_URL: 'https://test.supabase.co',
    VITE_SUPABASE_ANON_KEY: 'test-anon-key',
    DEV: true,
    PROD: false,
    MODE: 'test',
  },
})
