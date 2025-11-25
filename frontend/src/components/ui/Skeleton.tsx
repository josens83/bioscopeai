import { HTMLAttributes, forwardRef } from 'react'

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'shimmer'
  width?: string | number
  height?: string | number
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full'
}

const roundedStyles = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  full: 'rounded-full',
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  (
    {
      variant = 'shimmer',
      width,
      height,
      rounded = 'md',
      className = '',
      style,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={`
          ${variant === 'shimmer' ? 'skeleton-shimmer' : 'skeleton'}
          ${roundedStyles[rounded]}
          ${className}
        `}
        style={{
          width: typeof width === 'number' ? `${width}px` : width,
          height: typeof height === 'number' ? `${height}px` : height,
          ...style,
        }}
        aria-hidden="true"
        {...props}
      />
    )
  }
)

Skeleton.displayName = 'Skeleton'

// Skeleton Text - 텍스트 라인용
export interface SkeletonTextProps {
  lines?: number
  lastLineWidth?: string
}

export function SkeletonText({ lines = 3, lastLineWidth = '60%' }: SkeletonTextProps) {
  return (
    <div className="space-y-2" aria-hidden="true">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          height={16}
          width={index === lines - 1 ? lastLineWidth : '100%'}
        />
      ))}
    </div>
  )
}

// Skeleton Avatar - 아바타용
export interface SkeletonAvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const avatarSizes = {
  sm: 32,
  md: 40,
  lg: 48,
  xl: 64,
}

export function SkeletonAvatar({ size = 'md' }: SkeletonAvatarProps) {
  const sizeValue = avatarSizes[size]
  return <Skeleton width={sizeValue} height={sizeValue} rounded="full" />
}

// Skeleton Card - 카드 레이아웃용
export function SkeletonCard() {
  return (
    <div className="card p-6 space-y-4" aria-hidden="true">
      <div className="flex items-center gap-4">
        <SkeletonAvatar size="md" />
        <div className="flex-1 space-y-2">
          <Skeleton height={16} width="60%" />
          <Skeleton height={12} width="40%" />
        </div>
      </div>
      <SkeletonText lines={2} />
      <div className="flex gap-2">
        <Skeleton height={32} width={80} rounded="lg" />
        <Skeleton height={32} width={80} rounded="lg" />
      </div>
    </div>
  )
}

// Skeleton Table Row - 테이블 행용
export function SkeletonTableRow({ columns = 5 }: { columns?: number }) {
  return (
    <tr className="border-b border-surface-200 dark:border-surface-700" aria-hidden="true">
      {Array.from({ length: columns }).map((_, index) => (
        <td key={index} className="px-4 py-3">
          <Skeleton height={16} width={index === 0 ? '70%' : index === columns - 1 ? 60 : '80%'} />
        </td>
      ))}
    </tr>
  )
}

// Skeleton Stat Card - 통계 카드용
export function SkeletonStatCard() {
  return (
    <div className="card p-6" aria-hidden="true">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-3">
          <Skeleton height={14} width={80} />
          <Skeleton height={32} width={100} />
          <Skeleton height={12} width={60} />
        </div>
        <Skeleton width={48} height={48} rounded="lg" />
      </div>
    </div>
  )
}

// Skeleton List Item - 리스트 아이템용
export function SkeletonListItem() {
  return (
    <div className="flex items-center gap-3 py-3" aria-hidden="true">
      <Skeleton width={40} height={40} rounded="lg" />
      <div className="flex-1 space-y-2">
        <Skeleton height={14} width="70%" />
        <Skeleton height={12} width="40%" />
      </div>
    </div>
  )
}

// Paper Card Skeleton - 논문 카드용
export function SkeletonPaperCard() {
  return (
    <div className="card p-5 space-y-3" aria-hidden="true">
      <Skeleton height={18} width="90%" />
      <Skeleton height={14} width="60%" />
      <div className="flex gap-2 pt-2">
        <Skeleton height={24} width={60} rounded="full" />
        <Skeleton height={24} width={80} rounded="full" />
      </div>
    </div>
  )
}

// Chat Message Skeleton - 채팅 메시지용
export function SkeletonChatMessage({ isUser = false }: { isUser?: boolean }) {
  return (
    <div
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
      aria-hidden="true"
    >
      <SkeletonAvatar size="sm" />
      <div className={`flex-1 max-w-[70%] space-y-2 ${isUser ? 'items-end' : ''}`}>
        <Skeleton height={60} rounded="lg" />
        <Skeleton height={12} width={80} />
      </div>
    </div>
  )
}
