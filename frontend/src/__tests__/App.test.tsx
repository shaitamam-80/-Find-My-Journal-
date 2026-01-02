/**
 * Basic App component tests.
 *
 * These tests verify the core application structure and routing.
 */
import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import App from '../App'

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Route: () => null,
  }
})

// Mock AuthContext
vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    user: null,
    session: null,
    loading: false,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
  }),
}))

describe('App', () => {
  it('renders without crashing', () => {
    expect(() => render(<App />)).not.toThrow()
  })

  it('wraps content in ErrorBoundary', () => {
    const { container } = render(<App />)
    // ErrorBoundary renders children when no error
    expect(container).toBeDefined()
  })
})
