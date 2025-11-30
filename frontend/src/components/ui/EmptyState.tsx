import { ReactNode } from 'react'
import { DocumentIcon, SearchIcon, FolderIcon, ChatIcon, ChartBarIcon } from './Icons'
import { Button } from './Button'

export interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary'
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  size?: 'sm' | 'md' | 'lg'
}

const sizeStyles = {
  sm: {
    container: 'py-8',
    iconSize: 40,
    iconContainer: 'w-16 h-16',
    title: 'text-base',
    description: 'text-sm',
  },
  md: {
    container: 'py-12',
    iconSize: 48,
    iconContainer: 'w-20 h-20',
    title: 'text-lg',
    description: 'text-sm',
  },
  lg: {
    container: 'py-16',
    iconSize: 56,
    iconContainer: 'w-24 h-24',
    title: 'text-xl',
    description: 'text-base',
  },
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  size = 'md',
}: EmptyStateProps) {
  const styles = sizeStyles[size]

  return (
    <div className={`flex flex-col items-center justify-center text-center ${styles.container}`}>
      {/* Icon */}
      <div
        className={`
          ${styles.iconContainer}
          flex items-center justify-center
          bg-surface-100 dark:bg-surface-800
          rounded-full mb-4
          text-surface-400 dark:text-surface-500
        `}
      >
        {icon || <FolderIcon size={styles.iconSize} />}
      </div>

      {/* Title */}
      <h3
        className={`
          ${styles.title}
          font-semibold text-surface-900 dark:text-surface-100
          mb-2
        `}
      >
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p
          className={`
            ${styles.description}
            text-surface-500 dark:text-surface-400
            max-w-sm mb-6
          `}
        >
          {description}
        </p>
      )}

      {/* Actions */}
      {(action || secondaryAction) && (
        <div className="flex flex-col sm:flex-row items-center gap-3">
          {action && (
            <Button
              variant={action.variant || 'primary'}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant="ghost"
              onClick={secondaryAction.onClick}
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

// 미리 정의된 Empty State 패턴들

// 논문 없음
export function EmptyPapers({ onAddPaper }: { onAddPaper?: () => void }) {
  return (
    <EmptyState
      icon={<DocumentIcon size={48} />}
      title="아직 저장된 논문이 없습니다"
      description="PubMed에서 논문을 검색하거나 PDF 파일을 업로드하여 라이브러리를 구성하세요."
      action={onAddPaper ? {
        label: '첫 논문 추가하기',
        onClick: onAddPaper,
      } : undefined}
    />
  )
}

// 검색 결과 없음
export function EmptySearchResults({
  query,
  onClear,
}: {
  query?: string
  onClear?: () => void
}) {
  return (
    <EmptyState
      icon={<SearchIcon size={48} />}
      title="검색 결과가 없습니다"
      description={
        query
          ? `"${query}"에 대한 검색 결과를 찾을 수 없습니다. 다른 키워드로 시도해보세요.`
          : '검색 조건에 맞는 결과가 없습니다.'
      }
      action={onClear ? {
        label: '검색 초기화',
        onClick: onClear,
        variant: 'secondary',
      } : undefined}
    />
  )
}

// 분석 기록 없음
export function EmptyAnalyses({ onStartAnalysis }: { onStartAnalysis?: () => void }) {
  return (
    <EmptyState
      icon={<ChatIcon size={48} />}
      title="분석 기록이 없습니다"
      description="논문에 대해 AI에게 질문하거나, 요약 및 비교 분석을 시작해보세요."
      action={onStartAnalysis ? {
        label: 'AI 분석 시작하기',
        onClick: onStartAnalysis,
      } : undefined}
    />
  )
}

// 차트 데이터 없음
export function EmptyChartData() {
  return (
    <EmptyState
      icon={<ChartBarIcon size={48} />}
      title="표시할 데이터가 없습니다"
      description="아직 충분한 데이터가 수집되지 않았습니다."
      size="sm"
    />
  )
}

// 일반 빈 상태
export function EmptyGeneric({
  message = '데이터가 없습니다',
}: {
  message?: string
}) {
  return (
    <EmptyState
      title={message}
      size="sm"
    />
  )
}
