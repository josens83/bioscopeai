import { useState, useEffect, useCallback } from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import {
  useTheme,
  Avatar,
  Button,
  IconButton,
  BeakerIcon,
  HomeIcon,
  DocumentIcon,
  ChartBarIcon,
  SparklesIcon,
  SunIcon,
  MoonIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
} from './ui'

const navigation = [
  { name: '대시보드', href: '/dashboard', icon: HomeIcon },
  { name: '논문', href: '/papers', icon: DocumentIcon },
  { name: '분석', href: '/analysis', icon: ChartBarIcon },
  { name: '구독', href: '/subscription', icon: SparklesIcon },
]

export default function Layout() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const { theme, setTheme, isDark } = useTheme()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const toggleTheme = () => {
    if (theme === 'system') {
      setTheme(isDark ? 'light' : 'dark')
    } else {
      setTheme(isDark ? 'light' : 'dark')
    }
  }

  // Close mobile menu on Escape key
  const handleEscape = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && mobileMenuOpen) {
      setMobileMenuOpen(false)
    }
  }, [mobileMenuOpen])

  useEffect(() => {
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [handleEscape])

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex flex-col">
      {/* Skip Link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-brand-500 focus:text-white focus:rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-600 focus:ring-offset-2"
      >
        메인 콘텐츠로 건너뛰기
      </a>

      {/* 헤더 */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-surface-900/80 backdrop-blur-lg border-b border-surface-200 dark:border-surface-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* 로고 */}
            <div className="flex items-center gap-8">
              <Link to="/dashboard" className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
                  <BeakerIcon size={20} className="text-white" />
                </div>
                <span className="text-lg font-bold text-surface-900 dark:text-surface-50 hidden sm:block">
                  BioscopeAI
                </span>
              </Link>

              {/* 데스크톱 네비게이션 */}
              <nav className="hidden md:flex items-center gap-1">
                {navigation.map((item) => {
                  const isActive = location.pathname === item.href
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`
                        flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                        ${isActive
                          ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400'
                          : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100 hover:bg-surface-100 dark:hover:bg-surface-800'
                        }
                      `}
                    >
                      <Icon size={18} />
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
            </div>

            {/* 우측 액션 */}
            <div className="flex items-center gap-2">
              {/* 테마 토글 */}
              <IconButton
                variant="ghost"
                onClick={toggleTheme}
                aria-label={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
              >
                {isDark ? <SunIcon size={20} /> : <MoonIcon size={20} />}
              </IconButton>

              {/* 사용자 정보 및 로그아웃 (데스크톱) */}
              <div className="hidden md:flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Avatar size="sm" name={user?.username || user?.email} />
                  <span className="text-sm font-medium text-surface-700 dark:text-surface-300">
                    {user?.username || user?.email?.split('@')[0]}
                  </span>
                </div>
                <div className="w-px h-6 bg-surface-200 dark:bg-surface-700" />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  leftIcon={<ArrowRightOnRectangleIcon size={18} />}
                >
                  로그아웃
                </Button>
              </div>

              {/* 모바일 메뉴 버튼 */}
              <IconButton
                variant="ghost"
                className="md:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="메뉴"
              >
                {mobileMenuOpen ? <XMarkIcon size={24} /> : <Bars3Icon size={24} />}
              </IconButton>
            </div>
          </div>
        </div>

        {/* 모바일 메뉴 */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-900">
            <div className="px-4 py-3 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-colors
                      ${isActive
                        ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400'
                        : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800'
                      }
                    `}
                  >
                    <Icon size={20} />
                    {item.name}
                  </Link>
                )
              })}
            </div>
            <div className="px-4 py-3 border-t border-surface-200 dark:border-surface-800">
              <div className="flex items-center gap-3 mb-3">
                <Avatar size="sm" name={user?.username || user?.email} />
                <span className="text-sm font-medium text-surface-700 dark:text-surface-300">
                  {user?.username || user?.email?.split('@')[0]}
                </span>
              </div>
              <Button
                variant="secondary"
                className="w-full"
                onClick={handleLogout}
                leftIcon={<ArrowRightOnRectangleIcon size={18} />}
              >
                로그아웃
              </Button>
            </div>
          </div>
        )}
      </header>

      {/* 메인 콘텐츠 */}
      <main
        id="main-content"
        tabIndex={-1}
        className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 outline-none"
      >
        <Outlet />
      </main>

      {/* 푸터 */}
      <footer className="border-t border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <BeakerIcon size={18} className="text-brand-500" />
              <span className="text-sm font-medium text-surface-600 dark:text-surface-400">
                BioscopeAI
              </span>
            </div>
            <p className="text-sm text-surface-500 dark:text-surface-500">
              &copy; 2024 BioscopeAI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
