import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api'

// Mock the api module
vi.mock('@/lib/api', () => ({
  api: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock as any

// Test component that uses auth context
function TestComponent() {
  const { user, isAuthenticated, login, logout, loading } = useAuth()
  
  return (
    <div>
      <div data-testid="loading">{loading ? 'Loading' : 'Not Loading'}</div>
      <div data-testid="auth-status">{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>
      <div data-testid="username">{user?.username || 'No User'}</div>
      <button onClick={() => login('admin', 'admin123')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('provides authentication context', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
    expect(screen.getByTestId('username')).toHaveTextContent('No User')
  })

  it('handles successful login', async () => {
    const mockUser = {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      is_active: true,
      is_superuser: true
    }

    vi.mocked(api.login).mockResolvedValue({
      access_token: 'mock-token',
      token_type: 'bearer',
      user: mockUser
    })

    const user = userEvent.setup()

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await user.click(screen.getByText('Login'))

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated')
      expect(screen.getByTestId('username')).toHaveTextContent('admin')
    })

    expect(api.login).toHaveBeenCalledWith('admin', 'admin123')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'mock-token')
  })

  it('handles login failure', async () => {
    vi.mocked(api.login).mockRejectedValue(new Error('Invalid credentials'))

    const user = userEvent.setup()

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await user.click(screen.getByText('Login'))

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
      expect(screen.getByTestId('username')).toHaveTextContent('No User')
    })

    expect(localStorageMock.setItem).not.toHaveBeenCalled()
  })

  it('handles logout', async () => {
    // Setup authenticated state
    const mockUser = {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      is_active: true,
      is_superuser: true
    }

    localStorageMock.getItem.mockReturnValue('mock-token')
    vi.mocked(api.getCurrentUser).mockResolvedValue(mockUser)

    const user = userEvent.setup()

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    // Wait for initial auth check
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated')
    })

    // Logout
    await user.click(screen.getByText('Logout'))

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
      expect(screen.getByTestId('username')).toHaveTextContent('No User')
    })

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
  })

  it('loads user from token on mount', async () => {
    const mockUser = {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      is_active: true,
      is_superuser: true
    }

    localStorageMock.getItem.mockReturnValue('mock-token')
    vi.mocked(api.getCurrentUser).mockResolvedValue(mockUser)

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('loading')).toHaveTextContent('Loading')

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading')
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated')
      expect(screen.getByTestId('username')).toHaveTextContent('admin')
    })

    expect(api.getCurrentUser).toHaveBeenCalled()
  })

  it('handles invalid token on mount', async () => {
    localStorageMock.getItem.mockReturnValue('invalid-token')
    vi.mocked(api.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading')
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
    })

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
  })
})