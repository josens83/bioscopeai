import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider, useTheme } from '../../components/ui/ThemeProvider'

// Test component to interact with theme
function ThemeConsumer() {
  const { theme, setTheme, isDark } = useTheme()

  return (
    <div>
      <span data-testid="current-theme">{theme}</span>
      <span data-testid="is-dark">{isDark ? 'dark' : 'light'}</span>
      <button onClick={() => setTheme('light')}>Set Light</button>
      <button onClick={() => setTheme('dark')}>Set Dark</button>
      <button onClick={() => setTheme('system')}>Set System</button>
    </div>
  )
}

describe('ThemeProvider', () => {
  const originalMatchMedia = window.matchMedia
  let mockMatchMedia: typeof window.matchMedia

  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('light', 'dark')

    // Mock matchMedia
    mockMatchMedia = vi.fn((query: string) => ({
      matches: query === '(prefers-color-scheme: dark)' ? false : false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia
    window.matchMedia = mockMatchMedia
  })

  afterEach(() => {
    window.matchMedia = originalMatchMedia
  })

  it('renders children', () => {
    render(
      <ThemeProvider>
        <div data-testid="child">Child content</div>
      </ThemeProvider>
    )
    expect(screen.getByTestId('child')).toBeInTheDocument()
  })

  it('uses default theme of system', () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )
    expect(screen.getByTestId('current-theme')).toHaveTextContent('system')
  })

  it('uses custom default theme', () => {
    render(
      <ThemeProvider defaultTheme="dark">
        <ThemeConsumer />
      </ThemeProvider>
    )
    expect(screen.getByTestId('current-theme')).toHaveTextContent('dark')
  })

  it('reads theme from localStorage', () => {
    localStorage.setItem('bioscopeai-theme', 'dark')
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )
    expect(screen.getByTestId('current-theme')).toHaveTextContent('dark')
  })

  it('uses custom storage key', () => {
    localStorage.setItem('custom-theme-key', 'light')
    render(
      <ThemeProvider storageKey="custom-theme-key">
        <ThemeConsumer />
      </ThemeProvider>
    )
    expect(screen.getByTestId('current-theme')).toHaveTextContent('light')
  })

  it('changes theme when setTheme is called', async () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Set Dark' }))
    expect(screen.getByTestId('current-theme')).toHaveTextContent('dark')

    await userEvent.click(screen.getByRole('button', { name: 'Set Light' }))
    expect(screen.getByTestId('current-theme')).toHaveTextContent('light')
  })

  it('saves theme to localStorage when changed', async () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Set Dark' }))
    expect(localStorage.getItem('bioscopeai-theme')).toBe('dark')
  })

  it('adds dark class to document when theme is dark', async () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Set Dark' }))
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(document.documentElement.classList.contains('light')).toBe(false)
  })

  it('adds light class to document when theme is light', async () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Set Light' }))
    expect(document.documentElement.classList.contains('light')).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('detects system dark mode preference', () => {
    // Override matchMedia for this specific test
    window.matchMedia = vi.fn((query: string) => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia

    render(
      <ThemeProvider defaultTheme="system">
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('is-dark')).toHaveTextContent('dark')
  })

  it('throws error when useTheme is used outside provider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    function InvalidComponent() {
      useTheme()
      return null
    }

    expect(() => render(<InvalidComponent />)).toThrow(
      'useTheme must be used within a ThemeProvider'
    )

    consoleSpy.mockRestore()
  })
})
