import { Fragment, ReactNode, useEffect, useCallback, useRef } from 'react'
import { XIcon } from './Icons'
import { IconButton } from './Button'

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  description?: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
  closeOnOverlayClick?: boolean
  closeOnEscape?: boolean
  footer?: ReactNode
  /** Initial element to focus when modal opens. If not provided, focuses the first focusable element */
  initialFocus?: React.RefObject<HTMLElement>
}

const sizeStyles = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-4xl',
}

// Focusable element selector
const FOCUSABLE_SELECTOR = [
  'button:not([disabled])',
  '[href]',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ')

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  footer,
  initialFocus,
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const previouslyFocusedRef = useRef<HTMLElement | null>(null)

  // ESC 키 핸들링
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (closeOnEscape && e.key === 'Escape') {
        onClose()
      }
    },
    [closeOnEscape, onClose]
  )

  // Focus trap - Tab key handling
  const handleTabKey = useCallback((e: KeyboardEvent) => {
    if (e.key !== 'Tab' || !modalRef.current) return

    const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    if (!firstElement) return

    // Shift + Tab on first element -> go to last element
    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault()
      lastElement?.focus()
    }
    // Tab on last element -> go to first element
    else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault()
      firstElement?.focus()
    }
  }, [])

  // Store previously focused element and set initial focus
  useEffect(() => {
    if (isOpen) {
      // Store current focus
      previouslyFocusedRef.current = document.activeElement as HTMLElement

      // Set up event listeners
      document.addEventListener('keydown', handleEscape)
      document.addEventListener('keydown', handleTabKey)
      document.body.style.overflow = 'hidden'

      // Set initial focus
      const setInitialFocus = () => {
        if (initialFocus?.current) {
          initialFocus.current.focus()
        } else if (modalRef.current) {
          const firstFocusable = modalRef.current.querySelector<HTMLElement>(FOCUSABLE_SELECTOR)
          if (firstFocusable) {
            firstFocusable.focus()
          } else {
            // If no focusable elements, focus the modal itself
            modalRef.current.focus()
          }
        }
      }

      // Use requestAnimationFrame to ensure DOM is ready
      requestAnimationFrame(setInitialFocus)
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('keydown', handleTabKey)
      document.body.style.overflow = ''

      // Restore focus when modal closes
      if (previouslyFocusedRef.current && typeof previouslyFocusedRef.current.focus === 'function') {
        previouslyFocusedRef.current.focus()
      }
    }
  }, [isOpen, handleEscape, handleTabKey, initialFocus])

  if (!isOpen) return null

  return (
    <Fragment>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-fade-in"
        onClick={closeOnOverlayClick ? onClose : undefined}
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
        aria-describedby={description ? 'modal-description' : undefined}
      >
        {/* Modal Content */}
        <div
          ref={modalRef}
          tabIndex={-1}
          className={`
            ${sizeStyles[size]}
            w-full
            bg-white dark:bg-surface-800
            rounded-2xl shadow-2xl
            pointer-events-auto
            animate-scale-in
            max-h-[90vh] overflow-hidden
            flex flex-col
            outline-none
          `}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-start justify-between p-6 pb-0">
              <div>
                {title && (
                  <h2
                    id="modal-title"
                    className="text-xl font-semibold text-surface-900 dark:text-surface-100"
                  >
                    {title}
                  </h2>
                )}
                {description && (
                  <p
                    id="modal-description"
                    className="mt-1 text-sm text-surface-500 dark:text-surface-400"
                  >
                    {description}
                  </p>
                )}
              </div>
              {showCloseButton && (
                <IconButton
                  icon={<XIcon size={20} />}
                  label="닫기"
                  onClick={onClose}
                  className="ml-4 -mr-2 -mt-2"
                />
              )}
            </div>
          )}

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-6">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="p-6 pt-0 flex items-center justify-end gap-3">
              {footer}
            </div>
          )}
        </div>
      </div>
    </Fragment>
  )
}

// Confirm Modal - 확인 다이얼로그
export interface ConfirmModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title?: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'warning' | 'default'
  isLoading?: boolean
}

import { Button } from './Button'

export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = '확인',
  message,
  confirmLabel = '확인',
  cancelLabel = '취소',
  variant = 'default',
  isLoading = false,
}: ConfirmModalProps) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            {cancelLabel}
          </Button>
          <Button
            variant={variant === 'danger' ? 'danger' : 'primary'}
            onClick={onConfirm}
            isLoading={isLoading}
          >
            {confirmLabel}
          </Button>
        </>
      }
    >
      <p className="text-surface-600 dark:text-surface-300">{message}</p>
    </Modal>
  )
}

// Alert Modal - 알림 다이얼로그
export interface AlertModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  message: string
  buttonLabel?: string
}

export function AlertModal({
  isOpen,
  onClose,
  title = '알림',
  message,
  buttonLabel = '확인',
}: AlertModalProps) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <Button variant="primary" onClick={onClose}>
          {buttonLabel}
        </Button>
      }
    >
      <p className="text-surface-600 dark:text-surface-300">{message}</p>
    </Modal>
  )
}
