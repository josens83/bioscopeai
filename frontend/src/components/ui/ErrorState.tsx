import { ReactNode } from 'react'
import { ErrorIcon, RefreshIcon, WarningIcon } from './Icons'
import { Button } from './Button'

export interface ErrorStateProps {
  icon?: ReactNode
  title?: string
  description?: string
  error?: Error | string
  onRetry?: () => void
  retryLabel?: string
  fullPage?: boolean
}

export function ErrorState({
  icon,
  title = '문제가 발생했습니다',
  description,
  error,
  onRetry,
  retryLabel = '다시 시도',
  fullPage = false,
}: ErrorStateProps) {
  const errorMessage = error instanceof Error ? error.message : error

  return (
    <div
      className={`
        flex flex-col items-center justify-center text-center
        ${fullPage ? 'min-h-[60vh]' : 'py-12'}
      `}
      role="alert"
    >
      {/* Icon */}
      <div className="w-20 h-20 flex items-center justify-center bg-error-100 dark:bg-error-900/30 rounded-full mb-4">
        {icon || <ErrorIcon size={48} className="text-error-500" />}
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100 mb-2">
        {title}
      </h3>

      {/* Description */}
      <p className="text-sm text-surface-500 dark:text-surface-400 max-w-md mb-2">
        {description || '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'}
      </p>

      {/* Error details (개발 모드에서만 표시하거나 축소 가능) */}
      {errorMessage && (
        <details className="text-xs text-surface-400 mb-6 max-w-md">
          <summary className="cursor-pointer hover:text-surface-600 dark:hover:text-surface-300">
            오류 상세 정보
          </summary>
          <pre className="mt-2 p-3 bg-surface-100 dark:bg-surface-800 rounded-lg text-left overflow-x-auto">
            {errorMessage}
          </pre>
        </details>
      )}

      {/* Retry Button */}
      {onRetry && (
        <Button
          variant="secondary"
          onClick={onRetry}
          leftIcon={<RefreshIcon size={16} />}
        >
          {retryLabel}
        </Button>
      )}
    </div>
  )
}

// Network Error - 네트워크 오류
export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorState
      title="네트워크 연결 오류"
      description="인터넷 연결을 확인하고 다시 시도해주세요."
      onRetry={onRetry}
    />
  )
}

// Server Error - 서버 오류
export function ServerError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorState
      title="서버 오류가 발생했습니다"
      description="서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
      onRetry={onRetry}
    />
  )
}

// Not Found - 404
export function NotFoundError({
  resource = '페이지',
  onGoBack,
}: {
  resource?: string
  onGoBack?: () => void
}) {
  return (
    <ErrorState
      title={`${resource}를 찾을 수 없습니다`}
      description="요청하신 내용이 존재하지 않거나 삭제되었을 수 있습니다."
      onRetry={onGoBack}
      retryLabel="돌아가기"
    />
  )
}

// Permission Denied - 403
export function PermissionDenied({ onGoBack }: { onGoBack?: () => void }) {
  return (
    <ErrorState
      icon={<WarningIcon size={48} className="text-warning-500" />}
      title="접근 권한이 없습니다"
      description="이 페이지에 접근할 권한이 없습니다. 로그인하거나 플랜을 업그레이드해주세요."
      onRetry={onGoBack}
      retryLabel="돌아가기"
    />
  )
}

// Rate Limit - 429
export function RateLimitError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorState
      icon={<WarningIcon size={48} className="text-warning-500" />}
      title="요청 한도 초과"
      description="너무 많은 요청을 보냈습니다. 잠시 후 다시 시도해주세요."
      onRetry={onRetry}
    />
  )
}

// Inline Error - 인라인 에러 메시지
export function InlineError({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div className="flex items-center gap-3 p-4 bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg" role="alert">
      <ErrorIcon size={20} className="text-error-500 flex-shrink-0" />
      <p className="text-sm text-error-700 dark:text-error-300 flex-1">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm text-error-600 dark:text-error-400 hover:underline flex-shrink-0"
        >
          다시 시도
        </button>
      )}
    </div>
  )
}

// Warning Banner - 경고 배너
export function WarningBanner({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}) {
  return (
    <div className="flex items-start gap-3 p-4 bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg">
      <WarningIcon size={20} className="text-warning-500 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm font-medium text-warning-800 dark:text-warning-200">
          {title}
        </p>
        {description && (
          <p className="text-sm text-warning-700 dark:text-warning-300 mt-1">
            {description}
          </p>
        )}
      </div>
      {action && (
        <button
          onClick={action.onClick}
          className="text-sm font-medium text-warning-700 dark:text-warning-300 hover:underline flex-shrink-0"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
