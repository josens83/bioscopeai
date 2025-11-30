import { ImgHTMLAttributes, forwardRef, useState } from 'react'
import { UserIcon } from './Icons'

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

export interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'size'> {
  size?: AvatarSize
  name?: string
  src?: string
  fallback?: string
  showStatus?: boolean
  status?: 'online' | 'offline' | 'busy' | 'away'
}

const sizeStyles: Record<AvatarSize, { container: string; text: string; status: string }> = {
  xs: { container: 'w-6 h-6', text: 'text-xs', status: 'w-1.5 h-1.5' },
  sm: { container: 'w-8 h-8', text: 'text-sm', status: 'w-2 h-2' },
  md: { container: 'w-10 h-10', text: 'text-base', status: 'w-2.5 h-2.5' },
  lg: { container: 'w-12 h-12', text: 'text-lg', status: 'w-3 h-3' },
  xl: { container: 'w-16 h-16', text: 'text-xl', status: 'w-3.5 h-3.5' },
  '2xl': { container: 'w-20 h-20', text: 'text-2xl', status: 'w-4 h-4' },
}

const statusColors = {
  online: 'bg-success-500',
  offline: 'bg-surface-400',
  busy: 'bg-error-500',
  away: 'bg-warning-500',
}

// 이름에서 이니셜 추출
function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

// 이름에서 배경색 생성
function getColorFromName(name: string): string {
  const colors = [
    'bg-brand-500',
    'bg-accent-500',
    'bg-success-500',
    'bg-warning-500',
    'bg-error-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      size = 'md',
      name,
      src,
      fallback,
      showStatus = false,
      status = 'offline',
      className = '',
      alt,
      ...props
    },
    ref
  ) => {
    const [imageError, setImageError] = useState(false)
    const styles = sizeStyles[size]
    const showImage = src && !imageError

    return (
      <div
        ref={ref}
        className={`
          relative inline-flex items-center justify-center
          ${styles.container}
          rounded-full
          overflow-hidden
          flex-shrink-0
          ${!showImage && name ? getColorFromName(name) : 'bg-surface-200 dark:bg-surface-700'}
          ${className}
        `}
      >
        {showImage ? (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
            {...props}
          />
        ) : name ? (
          <span
            className={`
              ${styles.text}
              font-medium text-white
            `}
          >
            {fallback || getInitials(name)}
          </span>
        ) : (
          <UserIcon
            size={size === 'xs' ? 14 : size === 'sm' ? 16 : size === 'lg' ? 24 : size === 'xl' ? 32 : size === '2xl' ? 40 : 20}
            className="text-surface-400 dark:text-surface-500"
          />
        )}

        {/* Status indicator */}
        {showStatus && (
          <span
            className={`
              absolute bottom-0 right-0
              ${styles.status}
              ${statusColors[status]}
              rounded-full
              border-2 border-white dark:border-surface-800
            `}
          />
        )}
      </div>
    )
  }
)

Avatar.displayName = 'Avatar'

// Avatar Group
export interface AvatarGroupProps {
  avatars: Array<{ name?: string; src?: string }>
  max?: number
  size?: AvatarSize
}

export function AvatarGroup({ avatars, max = 4, size = 'md' }: AvatarGroupProps) {
  const visibleAvatars = avatars.slice(0, max)
  const remainingCount = avatars.length - max

  return (
    <div className="flex -space-x-2">
      {visibleAvatars.map((avatar, index) => (
        <Avatar
          key={index}
          name={avatar.name}
          src={avatar.src}
          size={size}
          className="ring-2 ring-white dark:ring-surface-800"
        />
      ))}
      {remainingCount > 0 && (
        <div
          className={`
            ${sizeStyles[size].container}
            inline-flex items-center justify-center
            rounded-full
            bg-surface-200 dark:bg-surface-700
            ring-2 ring-white dark:ring-surface-800
          `}
        >
          <span className={`${sizeStyles[size].text} font-medium text-surface-600 dark:text-surface-300`}>
            +{remainingCount}
          </span>
        </div>
      )}
    </div>
  )
}
