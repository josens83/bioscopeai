import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Modal, ConfirmModal, AlertModal } from '../../components/ui/Modal'

describe('Modal', () => {
  it('does not render when closed', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        <div data-testid="content">Modal content</div>
      </Modal>
    )
    expect(screen.queryByTestId('content')).not.toBeInTheDocument()
  })

  it('renders when open', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <div data-testid="content">Modal content</div>
      </Modal>
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('renders with title', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Modal Title">
        <div>Content</div>
      </Modal>
    )
    expect(screen.getByText('Modal Title')).toBeInTheDocument()
  })

  it('calls onClose when clicking overlay', async () => {
    const handleClose = vi.fn()
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <div>Content</div>
      </Modal>
    )

    // Click on overlay (the backdrop element with aria-hidden)
    const overlay = document.querySelector('[aria-hidden="true"]')
    if (overlay) {
      await userEvent.click(overlay)
      expect(handleClose).toHaveBeenCalled()
    }
  })

  it('calls onClose when pressing Escape', () => {
    const handleClose = vi.fn()
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <div>Content</div>
      </Modal>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(handleClose).toHaveBeenCalled()
  })

  it('renders close button when showCloseButton is true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} showCloseButton={true}>
        <div>Content</div>
      </Modal>
    )
    expect(screen.getByLabelText('닫기')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={() => {}} size="sm">
        <div>Content</div>
      </Modal>
    )
    expect(document.querySelector('.max-w-sm')).toBeInTheDocument()

    rerender(
      <Modal isOpen={true} onClose={() => {}} size="lg">
        <div>Content</div>
      </Modal>
    )
    expect(document.querySelector('.max-w-lg')).toBeInTheDocument()
  })
})

describe('ConfirmModal', () => {
  it('renders title and message', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Confirm Delete"
        message="Are you sure you want to delete this item?"
      />
    )
    expect(screen.getByText('Confirm Delete')).toBeInTheDocument()
    expect(screen.getByText('Are you sure you want to delete this item?')).toBeInTheDocument()
  })

  it('calls onConfirm when clicking confirm button', async () => {
    const handleConfirm = vi.fn()
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={handleConfirm}
        title="Confirm"
        message="Confirm action?"
        confirmLabel="Yes"
      />
    )

    await userEvent.click(screen.getByText('Yes'))
    expect(handleConfirm).toHaveBeenCalled()
  })

  it('calls onClose when clicking cancel button', async () => {
    const handleClose = vi.fn()
    render(
      <ConfirmModal
        isOpen={true}
        onClose={handleClose}
        onConfirm={() => {}}
        title="Confirm"
        message="Confirm action?"
        cancelLabel="No"
      />
    )

    await userEvent.click(screen.getByText('No'))
    expect(handleClose).toHaveBeenCalled()
  })

  it('shows loading state', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Confirm"
        message="Confirm action?"
        isLoading={true}
      />
    )

    // When loading, the button text changes to "로딩 중..." and it's disabled
    const loadingButton = screen.getByText('로딩 중...').closest('button')
    expect(loadingButton).toBeDisabled()
  })

  it('renders with danger variant', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Delete"
        message="Delete item?"
        variant="danger"
      />
    )

    // Danger variant should have red styling
    const confirmButton = screen.getByText('확인').closest('button')
    expect(confirmButton).toHaveClass('bg-error-500')
  })
})

describe('AlertModal', () => {
  it('renders title and message', () => {
    render(
      <AlertModal
        isOpen={true}
        onClose={() => {}}
        title="Alert"
        message="This is an alert message"
      />
    )
    expect(screen.getByText('Alert')).toBeInTheDocument()
    expect(screen.getByText('This is an alert message')).toBeInTheDocument()
  })

  it('calls onClose when clicking close button', async () => {
    const handleClose = vi.fn()
    render(
      <AlertModal
        isOpen={true}
        onClose={handleClose}
        title="Alert"
        message="Alert message"
        buttonLabel="OK"
      />
    )

    await userEvent.click(screen.getByText('OK'))
    expect(handleClose).toHaveBeenCalled()
  })

  it('uses default button label', () => {
    render(
      <AlertModal
        isOpen={true}
        onClose={() => {}}
        title="Info"
        message="Info message"
      />
    )
    expect(screen.getByText('확인')).toBeInTheDocument()
  })
})
