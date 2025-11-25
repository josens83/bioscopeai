import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { ThemeProvider, ToastProvider } from './components/ui'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import PapersPage from './pages/PapersPage'
import AnalysisPage from './pages/AnalysisPage'
import SubscriptionPage from './pages/SubscriptionPage'
import Layout from './components/Layout'

function AppRoutes() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {isAuthenticated ? (
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/papers" element={<PapersPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/subscription" element={<SubscriptionPage />} />
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
