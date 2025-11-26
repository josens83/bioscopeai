/**
 * BioscopeAI Mobile Theme - 웹 프론트엔드와 동기화된 디자인 시스템
 */

// 색상 팔레트 - 웹과 동일한 디자인 토큰
export const colors = {
  // Brand Colors
  brand: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9', // Primary
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
    950: '#082f49',
  },
  // Accent Colors
  accent: {
    50: '#fdf4ff',
    100: '#fae8ff',
    200: '#f5d0fe',
    300: '#f0abfc',
    400: '#e879f9',
    500: '#d946ef',
    600: '#c026d3',
    700: '#a21caf',
    800: '#86198f',
    900: '#701a75',
    950: '#4a044e',
  },
  // Surface Colors
  surface: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },
  // Status Colors
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
  },
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
  },
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
  },
  // Base colors
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
}

// 타이포그래피
export const typography = {
  fontFamily: {
    sans: 'System',
    mono: 'Menlo',
  },
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
  },
  fontWeight: {
    normal: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.625,
  },
}

// 간격
export const spacing = {
  0: 0,
  0.5: 2,
  1: 4,
  1.5: 6,
  2: 8,
  2.5: 10,
  3: 12,
  3.5: 14,
  4: 16,
  5: 20,
  6: 24,
  7: 28,
  8: 32,
  9: 36,
  10: 40,
  12: 48,
  14: 56,
  16: 64,
}

// 테두리 반경
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
}

// 그림자
export const shadows = {
  none: {
    shadowColor: 'transparent',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  sm: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  lg: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 15,
    elevation: 5,
  },
}

// 라이트 테마
export const lightTheme = {
  colors: {
    primary: colors.brand[500],
    primaryLight: colors.brand[100],
    primaryDark: colors.brand[700],
    accent: colors.accent[500],
    background: colors.surface[50],
    surface: colors.white,
    surfaceSecondary: colors.surface[100],
    text: colors.surface[900],
    textSecondary: colors.surface[500],
    textTertiary: colors.surface[400],
    border: colors.surface[200],
    borderLight: colors.surface[100],
    success: colors.success[500],
    warning: colors.warning[500],
    error: colors.error[500],
    successBackground: colors.success[50],
    warningBackground: colors.warning[50],
    errorBackground: colors.error[50],
  },
}

// 다크 테마
export const darkTheme = {
  colors: {
    primary: colors.brand[400],
    primaryLight: colors.brand[900],
    primaryDark: colors.brand[300],
    accent: colors.accent[400],
    background: colors.surface[950],
    surface: colors.surface[800],
    surfaceSecondary: colors.surface[900],
    text: colors.surface[50],
    textSecondary: colors.surface[400],
    textTertiary: colors.surface[500],
    border: colors.surface[700],
    borderLight: colors.surface[800],
    success: colors.success[400],
    warning: colors.warning[400],
    error: colors.error[400],
    successBackground: `${colors.success[700]}30`,
    warningBackground: `${colors.warning[700]}30`,
    errorBackground: `${colors.error[700]}30`,
  },
}

export type Theme = typeof lightTheme
export type ThemeColors = typeof lightTheme.colors
