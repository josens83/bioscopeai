import { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { ThemeProvider, ToastProvider, PageLoadingFallback, FullPageLoading } from './components/ui'
import Layout from './components/Layout'

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const PapersPage = lazy(() => import('./pages/PapersPage'))
const AnalysisPage = lazy(() => import('./pages/AnalysisPage'))
const SubscriptionPage = lazy(() => import('./pages/SubscriptionPage'))

// Wrapper component for lazy-loaded pages
function LazyPage({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<PageLoadingFallback />}>
      {children}
    </Suspense>
  )
}

function AppRoutes() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route
        path="/login"
        element={
          <Suspense fallback={<FullPageLoading />}>
            <LoginPage />
          </Suspense>
        }
      />
      <Route
        path="/register"
        element={
          <Suspense fallback={<FullPageLoading />}>
            <RegisterPage />
          </Suspense>
        }
      />

      {isAuthenticated ? (
        <Route element={<Layout />}>
          <Route
            path="/dashboard"
            element={
              <LazyPage>
                <DashboardPage />
              </LazyPage>
            }
          />
          <Route
            path="/papers"
            element={
              <LazyPage>
                <PapersPage />
              </LazyPage>
            }
          />
          <Route
            path="/analysis"
            element={
              <LazyPage>
                <AnalysisPage />
              </LazyPage>
            }
          />
          <Route
            path="/subscription"
            element={
              <LazyPage>
                <SubscriptionPage />
              </LazyPage>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
      ) : (
        <Route path="*" element={<Navigate to="/login" replace />} />
      )}
    </Routes>
  )
}

function App() {
  return (
    <ThemeProvider defaultTheme="system">
      <ToastProvider>
        <Router>
          <AppRoutes />
        </Router>
      </ToastProvider>
    </ThemeProvider>
  )
}

export default App
