import { HTMLAttributes, forwardRef, ReactNode } from 'react'

export type BadgeVariant = 'default' | 'secondary' | 'brand' | 'accent' | 'success' | 'warning' | 'error'
export type BadgeSize = 'sm' | 'md' | 'lg'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  size?: BadgeSize
  icon?: ReactNode
  dot?: boolean
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-surface-100 text-surface-700 dark:bg-surface-700 dark:text-surface-300',
  secondary: 'bg-surface-200 text-surface-600 dark:bg-surface-600 dark:text-surface-300',
  brand: 'bg-brand-100 text-brand-700 dark:bg-brand-900/30 dark:text-brand-400',
  accent: 'bg-accent-100 text-accent-700 dark:bg-accent-900/30 dark:text-accent-400',
  success: 'bg-success-100 text-success-700 dark:bg-success-700/30 dark:text-success-400',
  warning: 'bg-warning-100 text-warning-700 dark:bg-warning-700/30 dark:text-warning-400',
  error: 'bg-error-100 text-error-700 dark:bg-error-700/30 dark:text-error-400',
}

const dotColors: Record<BadgeVariant, string> = {
  default: 'bg-surface-500',
  secondary: 'bg-surface-400',
  brand: 'bg-brand-500',
  accent: 'bg-accent-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  error: 'bg-error-500',
}

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-xs',
  lg: 'px-3 py-1 text-sm',
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      children,
      variant = 'default',
      size = 'md',
      icon,
      dot = false,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <span
        ref={ref}
        className={`
          inline-flex items-center gap-1.5
          font-medium rounded-full
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `}
        {...props}
      >
        {dot && (
          <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />
        )}
        {icon && <span className="flex-shrink-0">{icon}</span>}
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

// Status Badge - 상태 표시용
export type StatusType = 'active' | 'inactive' | 'pending' | 'success' | 'error' | 'warning'

export interface StatusBadgeProps {
  status: StatusType
  label?: string
}

const statusConfig: Record<StatusType, { variant: BadgeVariant; label: string }> = {
  active: { variant: 'success', label: '활성' },
  inactive: { variant: 'default', label: '비활성' },
  pending: { variant: 'warning', label: '대기중' },
  success: { variant: 'success', label: '성공' },
  error: { variant: 'error', label: '오류' },
  warning: { variant: 'warning', label: '경고' },
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <Badge variant={config.variant} dot>
      {label || config.label}
    </Badge>
  )
}

// Plan Badge - 구독 플랜 표시용
export type PlanType = 'free' | 'basic' | 'premium' | 'enterprise'

export interface PlanBadgeProps {
  plan: PlanType
}

const planConfig: Record<PlanType, { variant: BadgeVariant; label: string }> = {
  free: { variant: 'default', label: 'Free' },
  basic: { variant: 'brand', label: 'Basic' },
  premium: { variant: 'accent', label: 'Premium' },
  enterprise: { variant: 'success', label: 'Enterprise' },
}

export function PlanBadge({ plan }: PlanBadgeProps) {
  const config = planConfig[plan]
  return (
    <Badge variant={config.variant} size="sm">
      {config.label}
    </Badge>
  )
}
