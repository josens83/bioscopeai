import { ButtonHTMLAttributes, forwardRef, ReactNode } from 'react'
import { LoaderIcon } from './Icons'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
export type ButtonSize = 'sm' | 'md' | 'lg'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  isLoading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  fullWidth?: boolean
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: `
    bg-brand-500 text-white
    hover:bg-brand-600 hover:shadow-md
    active:scale-[0.98] active:bg-brand-700
    dark:bg-brand-600 dark:hover:bg-brand-500
  `,
  secondary: `
    bg-surface-100 text-surface-700
    border border-surface-200
    hover:bg-surface-200 hover:border-surface-300
    active:scale-[0.98]
    dark:bg-surface-700 dark:text-surface-100 dark:border-surface-600
    dark:hover:bg-surface-600 dark:hover:border-surface-500
  `,
  ghost: `
    text-surface-600
    hover:bg-surface-100
    active:scale-[0.98]
    dark:text-surface-300 dark:hover:bg-surface-800
  `,
  danger: `
    bg-error-500 text-white
    hover:bg-error-600 hover:shadow-md
    active:scale-[0.98] active:bg-error-700
  `,
  outline: `
    bg-transparent text-brand-600
    border-2 border-brand-500
    hover:bg-brand-50 hover:border-brand-600
    active:scale-[0.98]
    dark:text-brand-400 dark:border-brand-400
    dark:hover:bg-brand-950 dark:hover:border-brand-300
  `,
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2.5 text-sm gap-2',
  lg: 'px-6 py-3 text-base gap-2.5',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || isLoading

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={`
          inline-flex items-center justify-center
          font-medium rounded-lg
          transition-all duration-200 ease-smooth
          focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2
          disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${fullWidth ? 'w-full' : ''}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <>
            <LoaderIcon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} className="animate-spin" />
            <span>로딩 중...</span>
          </>
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

// Icon Button
export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: ReactNode
  variant?: ButtonVariant
  size?: ButtonSize
  label: string // 접근성을 위한 필수 label
  isLoading?: boolean
}

const iconSizeStyles: Record<ButtonSize, string> = {
  sm: 'p-1.5',
  md: 'p-2',
  lg: 'p-2.5',
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      icon,
      variant = 'ghost',
      size = 'md',
      label,
      isLoading = false,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || isLoading

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        aria-label={label}
        title={label}
        className={`
          inline-flex items-center justify-center
          rounded-lg
          transition-all duration-200 ease-smooth
          focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2
          disabled:opacity-50 disabled:cursor-not-allowed
          ${variantStyles[variant]}
          ${iconSizeStyles[size]}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <LoaderIcon size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} className="animate-spin" />
        ) : (
          icon
        )}
        <span className="sr-only">{label}</span>
      </button>
    )
  }
)

IconButton.displayName = 'IconButton'
