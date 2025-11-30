import { useState, useEffect, createContext, useContext, useCallback, ReactNode } from 'react'
import { CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon, ExclamationTriangleIcon, XMarkIcon } from './Icons'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
}

interface ToastContextValue {
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  success: (title: string, message?: string) => void
  error: (title: string, message?: string) => void
  warning: (title: string, message?: string) => void
  info: (title: string, message?: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

const toastIcons: Record<ToastType, typeof CheckCircleIcon> = {
  success: CheckCircleIcon,
  error: ExclamationCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
}

const toastStyles: Record<ToastType, { container: string; icon: string }> = {
  success: {
    container: 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800',
    icon: 'text-success-500',
  },
  error: {
    container: 'bg-error-50 dark:bg-error-900/20 border-error-200 dark:border-error-800',
    icon: 'text-error-500',
  },
  warning: {
    container: 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800',
    icon: 'text-warning-500',
  },
  info: {
    container: 'bg-accent-50 dark:bg-accent-900/20 border-accent-200 dark:border-accent-800',
    icon: 'text-accent-500',
  },
}

interface ToastItemProps {
  toast: Toast
  onRemove: (id: string) => void
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  const [isExiting, setIsExiting] = useState(false)
  const Icon = toastIcons[toast.type]
  const styles = toastStyles[toast.type]

  useEffect(() => {
    const duration = toast.duration || 5000
    const timer = setTimeout(() => {
      setIsExiting(true)
      setTimeout(() => onRemove(toast.id), 300)
    }, duration)

    return () => clearTimeout(timer)
  }, [toast.id, toast.duration, onRemove])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => onRemove(toast.id), 300)
  }

  return (
    <div
      className={`
        flex items-start gap-3 p-4
        border rounded-lg shadow-lg
        ${styles.container}
        transition-all duration-300 ease-out
        ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
        animate-slide-in-right
      `}
      role="alert"
    >
      <Icon size={20} className={`flex-shrink-0 mt-0.5 ${styles.icon}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-surface-900 dark:text-surface-100">
          {toast.title}
        </p>
        {toast.message && (
          <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">
            {toast.message}
          </p>
        )}
      </div>
      <button
        onClick={handleClose}
        className="flex-shrink-0 p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
        aria-label="닫기"
      >
        <XMarkIcon size={16} className="text-surface-400" />
      </button>
    </div>
  )
}

interface ToastProviderProps {
  children: ReactNode
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { ...toast, id }])
  }, [])

  const success = useCallback((title: string, message?: string) => {
    addToast({ type: 'success', title, message })
  }, [addToast])

  const error = useCallback((title: string, message?: string) => {
    addToast({ type: 'error', title, message })
  }, [addToast])

  const warning = useCallback((title: string, message?: string) => {
    addToast({ type: 'warning', title, message })
  }, [addToast])

  const info = useCallback((title: string, message?: string) => {
    addToast({ type: 'info', title, message })
  }, [addToast])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, warning, info }}>
      {children}
      {/* Toast Container */}
      <div
        className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none"
        aria-live="polite"
        aria-atomic="true"
      >
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onRemove={removeToast} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

// 간단한 독립형 토스트 (Context 없이 사용)
export function SimpleToast({
  type,
  title,
  message,
  onClose,
}: {
  type: ToastType
  title: string
  message?: string
  onClose?: () => void
}) {
  const Icon = toastIcons[type]
  const styles = toastStyles[type]

  return (
    <div
      className={`
        flex items-start gap-3 p-4
        border rounded-lg shadow-lg
        ${styles.container}
      `}
      role="alert"
    >
      <Icon size={20} className={`flex-shrink-0 mt-0.5 ${styles.icon}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-surface-900 dark:text-surface-100">
          {title}
        </p>
        {message && (
          <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">
            {message}
          </p>
        )}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          aria-label="닫기"
        >
          <XMarkIcon size={16} className="text-surface-400" />
        </button>
      )}
    </div>
  )
}
