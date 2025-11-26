import { HTMLAttributes, forwardRef, ReactNode, KeyboardEvent, useCallback } from 'react'

export type CardVariant = 'default' | 'elevated' | 'outlined' | 'ghost'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
  /** Accessible label for clickable cards (required when onClick is provided) */
  ariaLabel?: string
}

const variantStyles: Record<CardVariant, string> = {
  default: `
    bg-white dark:bg-surface-800
    border border-surface-200 dark:border-surface-700
    shadow-sm
  `,
  elevated: `
    bg-white dark:bg-surface-800
    border border-surface-200 dark:border-surface-700
    shadow-md dark:shadow-dark-md
  `,
  outlined: `
    bg-transparent
    border-2 border-surface-200 dark:border-surface-700
  `,
  ghost: `
    bg-surface-50 dark:bg-surface-900
  `,
}

const paddingStyles: Record<'none' | 'sm' | 'md' | 'lg', string> = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      variant = 'default',
      hover = false,
      padding = 'md',
      className = '',
      onClick,
      onKeyDown,
      ariaLabel,
      ...props
    },
    ref
  ) => {
    const isClickable = Boolean(onClick)

    // Handle Enter and Space key for keyboard accessibility
    const handleKeyDown = useCallback(
      (e: KeyboardEvent<HTMLDivElement>) => {
        if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault()
          onClick?.(e as unknown as React.MouseEvent<HTMLDivElement>)
        }
        onKeyDown?.(e)
      },
      [isClickable, onClick, onKeyDown]
    )

    return (
      <div
        ref={ref}
        role={isClickable ? 'button' : undefined}
        tabIndex={isClickable ? 0 : undefined}
        aria-label={ariaLabel}
        onClick={onClick}
        onKeyDown={handleKeyDown}
        className={`
          rounded-xl
          transition-all duration-200
          ${variantStyles[variant]}
          ${paddingStyles[padding]}
          ${hover || isClickable ? 'hover:-translate-y-0.5 hover:shadow-lg hover:border-brand-500/20 cursor-pointer' : ''}
          ${isClickable ? 'focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:ring-offset-2' : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

// Card Header
export interface CardHeaderProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  title: ReactNode
  subtitle?: ReactNode
  action?: ReactNode
}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ title, subtitle, action, className = '', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`flex items-start justify-between gap-4 ${className}`}
        {...props}
      >
        <div className="min-w-0 flex-1">
          {typeof title === 'string' ? (
            <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {title}
            </h3>
          ) : (
            title
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
              {subtitle}
            </p>
          )}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
    )
  }
)

CardHeader.displayName = 'CardHeader'

// Card Content
export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ children, className = '', ...props }, ref) => {
    return (
      <div ref={ref} className={`${className}`} {...props}>
        {children}
      </div>
    )
  }
)

CardContent.displayName = 'CardContent'

// Card Footer
export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ children, className = '', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`pt-4 mt-4 border-t border-surface-200 dark:border-surface-700 ${className}`}
        {...props}
      >
        {children}
      </div>
    )
  }
)

CardFooter.displayName = 'CardFooter'

// Stat Card - 통계 표시용 카드
export interface StatCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    type: 'increase' | 'decrease' | 'neutral'
  }
  icon?: ReactNode
  description?: string
  loading?: boolean
}

export function StatCard({ title, value, change, icon, description, loading }: StatCardProps) {
  return (
    <Card hover className="relative overflow-hidden">
      {/* 배경 장식 */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-brand-500/10 to-transparent rounded-bl-full" />

      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-surface-500 dark:text-surface-400">
            {title}
          </p>
          {loading ? (
            <div className="mt-2 h-8 w-20 skeleton-shimmer rounded" />
          ) : (
            <p className="mt-2 text-3xl font-bold text-surface-900 dark:text-surface-100">
              {value}
            </p>
          )}
          {change && !loading && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={`
                  text-sm font-medium
                  ${change.type === 'increase' ? 'text-success-600 dark:text-success-400' : ''}
                  ${change.type === 'decrease' ? 'text-error-600 dark:text-error-400' : ''}
                  ${change.type === 'neutral' ? 'text-surface-500' : ''}
                `}
                aria-label={`${change.type === 'increase' ? '증가' : change.type === 'decrease' ? '감소' : '변동 없음'} ${change.value}%`}
              >
                <span aria-hidden="true">
                  {change.type === 'increase' && '↑'}
                  {change.type === 'decrease' && '↓'}
                  {change.type === 'neutral' && '→'}
                </span>
                {' '}{change.type === 'increase' && '+'}{change.value}%
              </span>
              <span className="text-xs text-surface-400">vs 지난달</span>
            </div>
          )}
          {description && (
            <p className="mt-2 text-sm text-surface-500">{description}</p>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 p-3 bg-brand-100 dark:bg-brand-900/30 rounded-xl text-brand-600 dark:text-brand-400">
            {icon}
          </div>
        )}
      </div>
    </Card>
  )
}
