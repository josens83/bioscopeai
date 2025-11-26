import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ToastProvider, useToast, SimpleToast } from '../../components/ui/Toast'

// Test component to trigger toasts
function ToastTrigger() {
  const { success, error, warning, info } = useToast()

  return (
    <div>
      <button onClick={() => success('Success!', 'This is a success message')}>
        Show Success
      </button>
      <button onClick={() => error('Error!', 'This is an error message')}>
        Show Error
      </button>
      <button onClick={() => warning('Warning!', 'This is a warning message')}>
        Show Warning
      </button>
      <button onClick={() => info('Info!', 'This is an info message')}>
        Show Info
      </button>
    </div>
  )
}

describe('ToastProvider', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders children', () => {
    render(
      <ToastProvider>
        <div data-testid="child">Child content</div>
      </ToastProvider>
    )
    expect(screen.getByTestId('child')).toBeInTheDocument()
  })

  it('shows success toast', async () => {
    vi.useRealTimers()
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Show Success' }))
    expect(screen.getByText('Success!')).toBeInTheDocument()
    expect(screen.getByText('This is a success message')).toBeInTheDocument()
  })

  it('shows error toast', async () => {
    vi.useRealTimers()
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Show Error' }))
    expect(screen.getByText('Error!')).toBeInTheDocument()
  })

  it('shows warning toast', async () => {
    vi.useRealTimers()
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Show Warning' }))
    expect(screen.getByText('Warning!')).toBeInTheDocument()
  })

  it('shows info toast', async () => {
    vi.useRealTimers()
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Show Info' }))
    expect(screen.getByText('Info!')).toBeInTheDocument()
  })

  it('removes toast when close button is clicked', async () => {
    vi.useRealTimers()
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    await userEvent.click(screen.getByRole('button', { name: 'Show Success' }))
    expect(screen.getByText('Success!')).toBeInTheDocument()

    const closeButton = screen.getByLabelText('닫기')
    await userEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText('Success!')).not.toBeInTheDocument()
    }, { timeout: 500 })
  })

  it('auto-removes toast after duration', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    await act(async () => {
      const button = screen.getByRole('button', { name: 'Show Success' })
      button.click()
    })

    expect(screen.getByText('Success!')).toBeInTheDocument()

    // Fast-forward past the toast duration (5000ms) + exit animation (300ms)
    await act(async () => {
      vi.advanceTimersByTime(5500)
    })

    expect(screen.queryByText('Success!')).not.toBeInTheDocument()
  })

  it('throws error when useToast is used outside provider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    function InvalidComponent() {
      useToast()
      return null
    }

    expect(() => render(<InvalidComponent />)).toThrow(
      'useToast must be used within a ToastProvider'
    )

    consoleSpy.mockRestore()
  })
})

describe('SimpleToast', () => {
  it('renders success toast', () => {
    render(<SimpleToast type="success" title="Success" message="Success message" />)
    expect(screen.getByText('Success')).toBeInTheDocument()
    expect(screen.getByText('Success message')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveClass('bg-success-50')
  })

  it('renders error toast', () => {
    render(<SimpleToast type="error" title="Error" />)
    expect(screen.getByRole('alert')).toHaveClass('bg-error-50')
  })

  it('renders warning toast', () => {
    render(<SimpleToast type="warning" title="Warning" />)
    expect(screen.getByRole('alert')).toHaveClass('bg-warning-50')
  })

  it('renders info toast', () => {
    render(<SimpleToast type="info" title="Info" />)
    expect(screen.getByRole('alert')).toHaveClass('bg-accent-50')
  })

  it('shows close button when onClose provided', async () => {
    const handleClose = vi.fn()
    render(<SimpleToast type="success" title="Test" onClose={handleClose} />)

    const closeButton = screen.getByLabelText('닫기')
    await userEvent.click(closeButton)
    expect(handleClose).toHaveBeenCalled()
  })

  it('does not show close button when onClose not provided', () => {
    render(<SimpleToast type="success" title="Test" />)
    expect(screen.queryByLabelText('닫기')).not.toBeInTheDocument()
  })
})
